# Deployment Guide

Production runs at **https://pmsim.pmi.moscow**. A manual GitHub Actions workflow builds and deploys it to a
Docker host that already runs the shared **nginx-proxy**.

## Architecture

```
Internet --https--> nginx-proxy --(pmi_network)--> web:80 --> api:8000 --> db:5432
                    (shared, TLS)                  nginx +    FastAPI     PostgreSQL 16
                                                   Vue SPA    uvicorn
```

| Service | Image | Networks | Exposure |
| --- | --- | --- | --- |
| `web` | `simultrain-web:latest` (nginx serving the built SPA, proxying `/api/` and `/auth/` to `api`) | `default`, `pmi_network` | Through nginx-proxy via `VIRTUAL_HOST`; `127.0.0.1:8086` on the host for debugging |
| `api` | `simultrain-api:latest` (FastAPI) | `default` | Internal only |
| `db` | `postgres:16-alpine` | `default` | Internal only |

- The shared **nginx-proxy** is not part of this repo. It sits on the external docker network `pmi_network`,
  terminates TLS with the `pmi.moscow` certificate and routes by hostname. `web` advertises itself with
  `VIRTUAL_HOST=pmsim.pmi.moscow` and `VIRTUAL_PORT=80`.
- Only `web` joins `pmi_network`. `api` and `db` are reachable only from inside the stack.
- No public host ports are published. The loopback port `127.0.0.1:${WEB_HOST_PORT:-8086}` exists only for
  debugging on the server.
- The browser only talks to one origin, so the session cookie is first-party (Secure, since `COOKIE_SECURE=true`)
  and there is no CORS setup.
- On startup the API creates or upgrades the schema and reseeds the built-in scenario. There is no separate
  migration step.

Related files:

| File | Purpose |
| --- | --- |
| [docker-compose.production.yml](docker-compose.production.yml) | Production stack; runs prebuilt images, never builds |
| [deploy/vhost.d/pmsim.pmi.moscow](deploy/vhost.d/pmsim.pmi.moscow) | nginx-proxy server snippet: certificate, TLS protocols and ciphers, HSTS |
| [deploy/vhost.d/pmsim.pmi.moscow_location](deploy/vhost.d/pmsim.pmi.moscow_location) | nginx-proxy location snippet: body size, gzip, security headers, unbuffered 1 h reads for server-sent events |
| [frontend/nginx.conf](frontend/nginx.conf) | nginx inside `web`; passes the original `X-Forwarded-Proto` (https) to the API |
| [.github/workflows/deploy-production.yml](.github/workflows/deploy-production.yml) | Manual build and deploy workflow |
| [.github/workflows/tests.yml](.github/workflows/tests.yml) | Backend and frontend tests |

## Server layout

```
/home/toptuk/pmsim/
  docker-compose.production.yml   copied by every deploy
  .env                            rendered from GitHub secrets by every deploy (mode 600)
```

The Postgres data lives in the named volume `pmsim_pgdata`. The prefix is the compose project name, which is
the directory name.

## One-time setup

### 1. Server

1. Docker Engine with the Compose plugin, plus the shared nginx-proxy running on `pmi_network`.
2. The proxy network. The deploy creates it if missing, but nginx-proxy needs to be on it:

   ```sh
   docker network inspect pmi_network >/dev/null 2>&1 || docker network create pmi_network
   ```

3. A DNS record for `pmsim.pmi.moscow` pointing at the server. The `pmi.moscow` certificate must cover it
   (wildcard `*.pmi.moscow`) and be present in the proxy as `certs/pmi.moscow.crt` / `.key`.
4. The vhost snippets, copied into the proxy's `vhost.d/` directory, followed by a proxy reload:

   ```sh
   scp deploy/vhost.d/pmsim.pmi.moscow deploy/vhost.d/pmsim.pmi.moscow_location <server>:<rproxy>/vhost.d/
   docker exec <nginx-proxy> nginx -t && docker exec <nginx-proxy> nginx -s reload
   ```

   The pipeline never touches the shared proxy config. Repeat this step whenever these files change.
5. An SSH user that can run `docker` and owns `/home/toptuk/pmsim`. The workflow creates the directory.

### 2. Sign-in providers

Register these redirect URIs:

| Provider | Where | Redirect URI |
| --- | --- | --- |
| Yandex ID | https://oauth.yandex.ru, app settings | `https://pmsim.pmi.moscow/auth/login-yandex` |
| VK ID (VK, Odnoklassniki, Mail.ru) | https://id.vk.com/about/business, trusted Redirect URL | `https://pmsim.pmi.moscow/auth/login-vk` |
| Google | https://console.cloud.google.com/apis/credentials, OAuth client "Web application", Authorized redirect URIs | `https://pmsim.pmi.moscow/auth/login-google` |

### 3. GitHub secrets and variables

Set these under **Settings → Secrets and variables → Actions**. The workflow checks the required ones and fails
early with a clear message if one is missing.

| Kind | Name | Required | Notes |
| --- | --- | --- | --- |
| Secret | `PRODUCTION_SSH_HOST` | yes | Server host name or IP |
| Secret | `PRODUCTION_SSH_USERNAME` | yes | SSH user |
| Secret | `PRODUCTION_SSH_KEY` | yes | Private key (PEM / OpenSSH, full text) |
| Secret | `PRODUCTION_SSH_PORT` | no | Default `22` |
| Secret | `REGISTRY_TOKEN` | yes | GitHub PAT with `read:packages`; the server uses it to pull from GHCR |
| Secret | `YANDEX_CLIENT_ID`, `YANDEX_CLIENT_SECRET` | yes | Yandex ID app credentials |
| Secret | `YANDEX_REDIRECT_URI` | yes | `https://pmsim.pmi.moscow/auth/login-yandex` |
| Secret | `VK_CLIENT_ID` | yes | VK ID app id. Not the secret or service key: the flow uses PKCE |
| Secret | `VK_REDIRECT_URI` | yes | `https://pmsim.pmi.moscow/auth/login-vk` |
| Secret | `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` | yes | Google OAuth client credentials. The id ends in `.apps.googleusercontent.com`, the secret starts with `GOCSPX-` |
| Secret | `GOOGLE_REDIRECT_URI` | yes | `https://pmsim.pmi.moscow/auth/login-google` |
| Secret | `SESSION_SECRET` | yes | Long random string (`openssl rand -hex 32`). Keep it stable, or every user is signed out |
| Secret | `POSTGRES_PASSWORD` | yes | Set before the first deploy. Postgres keeps the password from the first start of the volume |
| Secret | `POSTGRES_USER`, `POSTGRES_DB` | no | Default `simultrain` |
| Variable | `DEPLOY_DIR` | no | Default `/home/toptuk/pmsim` |
| Variable | `VIRTUAL_HOST` | no | Default `pmsim.pmi.moscow` |
| Variable | `WEB_HOST_PORT` | no | Default `8086` |

The build job pushes images with the built-in `GITHUB_TOKEN`, so pushing needs no extra secret.

## Deploying

1. Merge the changes into the branch you deploy from (normally `main`) and check that **tests** are green.
2. Open **Actions → Manual deploy production → Run workflow**, pick the branch and run it.

The workflow does the following:

1. **Build and push images**: builds `backend/` and `frontend/` and pushes `ghcr.io/toptuk/leanprojectsimulator-api:latest`
   and `-web:latest`.
2. **Deploy to PROD**:
   1. validates the secrets
   2. renders `.env` from secrets and variables
   3. copies `docker-compose.production.yml` and `.env` to `DEPLOY_DIR`
   4. on the server, logs in to GHCR, ensures `pmi_network` exists, pulls both images and retags them as
      `simultrain-api:latest` / `simultrain-web:latest`
   5. runs `docker compose down` followed by `up -d --force-recreate`, then prunes unused images

The database volume survives redeploys. Expect a few seconds of downtime while containers are recreated. Running
simulations are not lost: the clock catches up on the next request.

### Manual deploy

Do this on the server, for example when GitHub Actions is unavailable:

```sh
cd /home/toptuk/pmsim
echo "$REGISTRY_TOKEN" | docker login ghcr.io -u <github-user> --password-stdin
for s in api web; do
  docker pull ghcr.io/toptuk/leanprojectsimulator-$s:latest
  docker tag ghcr.io/toptuk/leanprojectsimulator-$s:latest simultrain-$s:latest
done
docker compose -f docker-compose.production.yml up -d --no-build --remove-orphans
```

### Rollback

Images are tagged only `latest`, and the deploy prunes old images. To roll back, deploy older code:

1. Create a branch or tag at the last good commit, for example `git tag rollback-2026-10-24 <sha> && git push origin rollback-2026-10-24`.
2. Run **Manual deploy production** and select that tag or branch.

A rollback does not undo schema upgrades. The startup upgrade only ever adds columns or relaxes constraints, so
older code still runs against the newer schema.

## Verifying

On the server:

```sh
cd /home/toptuk/pmsim
docker compose -f docker-compose.production.yml ps          # all three services Up, db healthy
curl -s http://127.0.0.1:8086/api/health                     # {"ok":true}
docker compose -f docker-compose.production.yml logs -f api  # startup, requests
```

From outside:

```sh
curl -sI https://pmsim.pmi.moscow | head -n 5               # 200 and a Strict-Transport-Security header
curl -s https://pmsim.pmi.moscow/api/health                 # {"ok":true}
```

In the browser:

1. Sign in with Yandex, with VK and with Google.
2. Start a simulation and let the clock run for more than a minute. The clock should keep ticking without
   reconnect gaps.

## Operations

### Database backup and restore

```sh
cd /home/toptuk/pmsim
# backup
docker compose -f docker-compose.production.yml exec -T db \
  pg_dump -U simultrain -d simultrain -Fc > backup-$(date -u +%Y%m%dT%H%M%SZ).dump
# restore (stop the API first)
docker compose -f docker-compose.production.yml stop api
docker compose -f docker-compose.production.yml exec -T db \
  pg_restore -U simultrain -d simultrain --clean --if-exists < backup-XXXX.dump
docker compose -f docker-compose.production.yml start api
```

### Rotating secrets

Update the secret in GitHub and run the deploy workflow again. It rewrites `.env` and recreates the containers.
Two secrets need extra care:

- **`SESSION_SECRET`**: changing it signs everyone out.
- **`POSTGRES_PASSWORD`**: changing the secret alone does nothing for an existing volume. First change the
  password in the database (`ALTER USER simultrain PASSWORD '...'`), then update the secret and redeploy.

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `502 Bad Gateway` or the default proxy page | `web` is not on `pmi_network`, or the proxy hasn't picked it up | `docker network inspect pmi_network` should list the `web` container; check `VIRTUAL_HOST` in `.env` and the nginx-proxy logs |
| Certificate warning | The `vhost.d` snippet is missing, or the cert doesn't cover the host | Copy `deploy/vhost.d/*` to the proxy and reload it; check the `certs/pmi.moscow.*` files |
| Yandex: `redirect_uri` mismatch | The secret differs from the app setting | `YANDEX_REDIRECT_URI` must exactly equal the URI registered in the Yandex app |
| VK ID error after consent | Redirect URL not trusted, or wrong app id | Add `https://pmsim.pmi.moscow/auth/login-vk` to the VK ID app; check `VK_CLIENT_ID` |
| Google: `redirect_uri_mismatch` or `invalid_client` | URI not authorized, or wrong id / secret | Add `https://pmsim.pmi.moscow/auth/login-google` to the OAuth client; check `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` |
| Signed in, but bounced back to the landing page | The cookie isn't stored | The site must be opened over https (`COOKIE_SECURE=true`); avoid mixing hosts |
| The clock freezes or jumps every minute | The proxy buffers or times out the SSE stream | Check that `pmsim.pmi.moscow_location` is in the proxy's `vhost.d/` and the proxy was reloaded |
| `api` restarts with a DB authentication error | `POSTGRES_PASSWORD` changed after the volume was created | See [Rotating secrets](#rotating-secrets) |
| Deploy fails with `Permission denied (publickey)` | Wrong SSH user or key | Check `PRODUCTION_SSH_USERNAME`, `PRODUCTION_SSH_KEY` and `PRODUCTION_SSH_PORT` |
| `denied` pulling from ghcr.io on the server | `REGISTRY_TOKEN` is missing `read:packages` or has expired | Issue a new PAT and update the secret |
