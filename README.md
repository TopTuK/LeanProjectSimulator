# SimulTrain Demo

A project-management business game modelled on the flow described in [behavior.md](behavior.md):
landing page → sign in with Yandex → simulation control → a one-week playable demo with a running clock,
mail, phone calls, decisions, and live Cost / Schedule / Quality / Motivation indexes.
Scenario content ("Webshop Launch") and scoring rules are original.

Stack: Vue 3 + Pinia + Tailwind CSS v4 (Vite), FastAPI + SQLAlchemy 2, PostgreSQL 16, nginx.
UI and scenario in English and Russian. Sign-in with Yandex ID.

## Quick start

```sh
cp .env.example .env   # fill in the Yandex ID app and SESSION_SECRET
docker compose up --build
```

Open http://localhost:8080, sign in with Yandex and press **Start simulation**. Pick the **Test** or
**Fast** speed to play a week in 3 or 7 min; **Demo** is 15 min per week.

## Configuration

All settings come from environment variables; `docker compose` reads them from `.env`.

| Variable | Default | Purpose |
| --- | --- | --- |
| `YANDEX_CLIENT_ID`, `YANDEX_CLIENT_SECRET` | — (required) | App credentials from https://oauth.yandex.ru |
| `YANDEX_REDIRECT_URI` | `http://localhost:8080/auth/login-yandex` | Must equal a Redirect URI registered in the Yandex app |
| `SESSION_SECRET` | — (required) | Signs the login cookie; keep it stable or everybody is signed out on restart |
| `COOKIE_SECURE` | `false` | `true` when served over https; must be `false` on plain-http localhost |
| `DATABASE_URL` | `sqlite:///./simultrain.db` | SQLAlchemy URL; compose points it at the `db` service |
| `POSTGRES_USER` / `_PASSWORD` / `_DB` | `simultrain` | Postgres container credentials |
| `WEB_PORT` | `8080` | Host port of the web container |

Redirect URIs to register in the Yandex app:

| Environment | Redirect URI |
| --- | --- |
| Production | `https://pmsim.pmi.moscow/auth/login-yandex` |
| `docker compose` on localhost | `http://localhost:8080/auth/login-yandex` |
| Vite dev server | `http://localhost:5173/auth/login-yandex` |

Use the same host in the browser as in the redirect URI (`localhost` and `127.0.0.1` have separate cookies).

## Local development

```sh
docker compose up -d db                      # or any Postgres
cd backend && pip install -r requirements.txt
export DATABASE_URL=postgresql+psycopg://simultrain:simultrain@localhost:5432/simultrain
export YANDEX_CLIENT_ID=... YANDEX_CLIENT_SECRET=... SESSION_SECRET=dev-secret COOKIE_SECURE=false
export YANDEX_REDIRECT_URI=http://localhost:5173/auth/login-yandex
uvicorn app.main:app --reload
cd frontend && npm install && npm run dev    # http://localhost:5173, proxies /api and /auth to :8000
```

To reach the database from the host, add `ports: ["5432:5432"]` to the `db` service.
Without `DATABASE_URL` the backend uses a local SQLite file.

## Tests

```sh
cd backend && pytest -q          # or: docker compose exec api pytest -q
cd frontend && npm test          # Vitest + jsdom
```

- **Backend** ([backend/tests](backend/tests)) runs against a throwaway SQLite database. Yandex is replaced
  by `FakeYandex` in [conftest.py](backend/tests/conftest.py); the `login()` helper walks the real redirect
  flow, and the `auth_client` fixture is a signed-in client. Covers clock maths, rules, a full demo week,
  sign-in (state check, open-redirect guard, errors), per-user access and the schema upgrade.
- **Frontend** ([frontend/src/\_\_tests\_\_](frontend/src/__tests__)) stubs `fetch`. Covers the API client,
  auth and sim stores, the router guard and the landing page in both languages.

## Architecture

### Deployment

```mermaid
flowchart LR
  B[Browser] -->|"/  (static SPA)"| W[web: nginx]
  W -->|"/api/*, /auth/*"| A[api: FastAPI / uvicorn]
  A --> D[(db: PostgreSQL)]
  B <-->|OAuth redirects| Y[Yandex ID]
  A -->|token + user info| Y
```

Three containers from [docker-compose.yml](docker-compose.yml):

- **web** — multi-stage [frontend/Dockerfile](frontend/Dockerfile): Vite builds the SPA, nginx serves it.
  [nginx.conf](frontend/nginx.conf) proxies `/api/` (with buffering off for server-sent events) and `/auth/`
  (the Yandex redirect URI) to the API, and falls back to `index.html` for client-side routes.
- **api** — FastAPI on uvicorn ([backend/Dockerfile](backend/Dockerfile)). Stateless apart from the
  database, so it can be restarted at any time; the clock catches up on the next request.
- **db** — PostgreSQL 16 with a named volume. JSON columns use `JSONB` on Postgres and plain `JSON` on SQLite.

The browser only ever talks to one origin, so the session cookie is first-party and there is no CORS setup.

### Backend layout

```
backend/app/
  main.py            app, middleware, error mapping, DB init + seed on startup
  db.py              engine and session factory from DATABASE_URL
  models.py          SQLAlchemy tables
  schemas.py         request bodies (pydantic)
  auth.py            Yandex client, cookie settings, current_user dependency
  routers/           thin HTTP layer: auth, scenarios, sessions
  engine/            the game, no HTTP
    clock.py         project time <-> real time
    schedule.py      critical path method over the baseline plan
    scenario.py      cached in-memory view of a scenario
    rules.py         pure functions: work, cost, EV/PV, indexes, effects
    leveling.py      resource-leveling proposal
    sim.py           session lifecycle and the JSON view
  seed/              built-in scenario content
```

Routers parse input, resolve the user, lock the session row and call `engine.sim`. The engine raises
`SimError(status, message)`, which [main.py](backend/app/main.py) turns into `{"detail": ...}` responses.
[rules.py](backend/app/engine/rules.py), [schedule.py](backend/app/engine/schedule.py),
[clock.py](backend/app/engine/clock.py) and [leveling.py](backend/app/engine/leveling.py) are pure
functions over plain data and are unit-tested without a database.

### The clock

The server owns time. A session stores `minutes` (project minutes since Monday 8:00 of week 1),
`status` (`ready | running | paused | ended`) and `last_tick_at`.

- Days run 8:00–19:00 on the clock (660 project minutes), people work 9:00–17:00, weekends are skipped.
- Speed is real seconds per project week: `test` 180, `fast` 420, `demo` 900.
- Nothing runs in the background. Every request for a running session calls `sim.advance`, which moves
  the clock by `elapsed real seconds × speed factor` and replays each completed project hour in order:

```
for each hour boundary passed:
    if work hour: rules.work_hour()     # progress, cost, overload penalties
    deliver due events                  # mail / phone / meetings, event effects, open decisions
    auto-resolve decisions past deadline with their default option
    write a snapshot                    # indexes, AC/EV/PV, hours
at the end of week 1: force-resolve open decisions, status = ended
```

Because every hour is replayed, the result does not depend on how often the client polls.
The session row is read with `SELECT … FOR UPDATE`, so concurrent requests can't double-count time.

### Session state

Fast-changing numbers (progress per activity, quality, motivation, overrides, delivered events) live in
one JSON column, `sessions.state`, so a tick is a single-row update. Everything that is a list the player
interacts with has its own table.

| Table | Holds |
| --- | --- |
| `users` | Yandex ID, login, email, display name, avatar |
| `sessions` | owner, frozen settings (`config`), clock, `state` JSON |
| `assignments` | who works on what, at what percent |
| `messages` | delivered mail and phone calls, read flag |
| `session_decisions` | opened decisions, deadline, chosen option, `team` or `auto` |
| `snapshots` | hourly index time series for reports |
| `action_log` | every player action; unique `client_action_id` makes writes idempotent |

Settings are frozen at creation: `config` is never changed afterwards.

### Scenario content

Scenario tables (`scenarios`, `activities`, `dependencies`, `resources`, `resource_weeks`,
`default_assignments`, `scenario_events`, `decisions`, `decision_options`) hold authored content with
texts as `{"en": ..., "ru": ...}`.

- The built-in "Webshop Launch" scenario lives in Python in [seed/webshop.py](backend/app/seed/webshop.py).
  [seed/\_\_init\_\_.py](backend/app/seed/__init__.py) rewrites it on every start, so content edits reach
  existing databases. Sessions refer to activities and people by number, so replacing rows is safe.
- [scenario.py](backend/app/engine/scenario.py) loads a scenario once into dataclasses, runs CPM to get
  early/late dates, slack and the critical path, and caches it per process.
- An event has a time, a channel (`mail`, `phone`, `meeting`), optional effects and an optional decision.
  A decision has options with effects, feedback, a learning point, a default and a deadline in project hours.

### Rules

Formulas are documented at the top of [rules.py](backend/app/engine/rules.py). In short:

- Each work hour, everyone assigned to a ready activity (all predecessors done) adds
  `share × pace` hours of progress and is paid `share × rate`. Load above 100% is scaled down.
- `pace = (0.7 + 0.3 × motivation/100) × difficulty pace`.
- Over-allocated people cost motivation and quality every work hour.
- Schedule index = SPI = EV / PV. Cost index = budget at completion / estimate at completion.
- Harmful decision effects are multiplied by the matching difficulty (easy 0.7, standard 1.0, hard 1.3).

### Authentication

Yandex ID with the OAuth 2.0 authorization code flow ([auth.py](backend/app/auth.py),
[routers/auth.py](backend/app/routers/auth.py)):

```
Browser            API                                  Yandex
  | GET /api/auth/yandex/login?next=/control
  |------------------>| store random state + next in cookie
  |<---- 302 ---------| to oauth.yandex.ru/authorize?client_id&redirect_uri&state
  |------------------------------------------------------->| user consents
  |<------------------------------------------------------ 302 /auth/login-yandex?code&state
  |------------------>| check state (single use)
  |                   |--- POST /token (code, client secret) -->|
  |                   |--- GET login.yandex.ru/info ----------->|
  |                   | upsert users row, cookie uid = user.id
  |<---- 302 next ----|
```

- The login cookie is Starlette's signed `SessionMiddleware` cookie (`simultrain_session`, HttpOnly,
  SameSite=Lax, 30 days, Secure when `COOKIE_SECURE=true`). No tokens are stored; Yandex is only asked
  during sign-in.
- `next` must be a same-site path; anything else becomes `/`.
- `current_user` guards every `/api/sessions` route. A session belongs to the user who created it;
  someone else's session returns 404, as if it did not exist.
- On startup `upgrade_schema()` adds `sessions.user_id` to databases created before sign-in existed
  (`create_all` never alters tables). Sessions from that time have no owner and are no longer reachable.

### Frontend

```
frontend/src/
  main.js, App.vue   app bootstrap
  router.js          routes and the sign-in guard
  api.js             fetch wrapper; errors carry .status and the server detail
  stores/auth.js     signed-in user, login redirect, logout
  stores/sim.js      current session state, SSE connection, actions
  pages/             Landing, Control (settings), Sim (game shell)
  views/             Office, Budget, Gantt, Team, Network, Reports, Calendar, Control, Help
  components/        clock button, mail drawer, decision / task / end modals, charts, form controls
  i18n/              en / ru strings and the in-game guide
```

- Routes: `/` (public), `/control` and `/sim/:id/:view` (need sign-in). The guard asks `/api/auth/me`
  once and otherwise sends the browser to Yandex with the full path as `next`.
- The server is the source of truth. Every action returns the full session state, which replaces the
  store's copy. While the clock runs, the store opens `GET /api/sessions/{id}/stream` (server-sent
  events, one state per second) and closes it when the clock stops.
- Each write sends a fresh `client_action_id`, so a retried request is not applied twice.
- A 401 during play (cookie expired, signed out elsewhere) sends the player to sign in and back.
- The last session id is kept in `localStorage` for "Continue last simulation"; the UI language too.

## API

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/health` | Liveness |
| GET | `/api/auth/yandex/login?next=/path` | Redirect to Yandex ID |
| GET | `/auth/login-yandex` | Yandex redirect URI: sign in, back to `next` |
| GET | `/api/auth/me` | Signed-in user, or 401 |
| POST | `/api/auth/logout` | Sign out |
| GET | `/api/scenarios` | Scenario list |
| POST | `/api/sessions` | Create a session with frozen settings |
| GET | `/api/sessions/{id}` | Full state |
| GET | `/api/sessions/{id}/stream` | SSE state stream |
| GET | `/api/sessions/{id}/snapshots` | Index time series for reports |
| POST | `/api/sessions/{id}/clock/start` · `/pause` | Clock control |
| PUT | `/api/sessions/{id}/assignments` | Replace assignments (clock must be paused) |
| POST | `/api/sessions/{id}/leveling` | Resource-leveling proposal |
| POST | `/api/sessions/{id}/messages/{mid}/read` | Mark message read |
| POST | `/api/sessions/{id}/decisions/{did}` | Choose an option, or `postpone` |

All `/api/sessions` calls need a signed-in user (401 otherwise); another user's session is 404.
Write calls accept an optional `client_action_id`; a repeated id is ignored. Errors are
`{"detail": "..."}` with 400 / 404 / 409 / 422.

## Not in this demo

Risk register, RACI matrix, weeks 2–12, periods, licenses and the trainer desk. The control page shows
Risk/RACI as disabled.
