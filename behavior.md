# SimulTrain behavior model

Observed 23 October 2026 with REA browser scenarios against the public site [https://simultrain.swiss/](https://simultrain.swiss/) and the public demo at `https://simultrain.swiss/smt12/?pwd=0`.

This file is a behavior model for planning an original project-management training simulator (Vue client, .NET or Python API, a database). It records screens, flows, and contracts that were actually exercised or that the served client script names. It is not a copy of STS scenario prose, artwork, or tuned simulation coefficients. Those stay with STS. Build original scenarios, original media, and original scoring rules.

Evidence is runtime observation unless a row says otherwise. The client script `smt12/js1/smt.min.js` (build string on screen: online build 12.2.241) was read as served bytes, not executed by the analyzer. Static script references are marked as such.

## Evidence

| What | Evidence id | Result |
| --- | --- | --- |
| Marketing homepage | `ev_55ada31f57b790bee806254a984c4eac4d5704ed0c17381406f5f10d60d4eab4` | Loaded `https://simultrain.swiss/` |
| Demo shell before save | `ev_7625b769cac3b2324a404ed79488c576b9a4892f61619a5124738152207023bd` | Simulation Control |
| Language and scenario menus, then Save and Go | `ev_b08b41f171e98e9627255298a1b81a59c7e0bb1fcc0861d62cab25710f55a00b` | Dashboard |
| Budget, Gantt, Team, Activity Network | `ev_d410b3ee0a7118caf1013c03ae9d44df0504312f87c94cc62f2beab1985236b4` | Four planning views |
| Reports and Calendar | `ev_6a595cd8d64c8f77c9664377a433416bc81912b36d905fb26f80b0608b3797e3` | Two more views |
| Reports DOM | `ev_fc2e6ce11ccc1630197c2da185c5f0cbf2c4ed4367e3264dba67d4a3dbcdf5a3` | Report tiles are clickable divs |
| Save, with request and response bodies | `ev_4d42c9a93b5f0578b25580ac14f523e56deda883c3cdc7d6766443a921a3656f` | PHP calls and string pack |
| Periods, speed, risk, difficulty, planned menus | `ev_b04ff3b4d25fe3af43f1ccec489f19d806a868388f9d4c1551e67984a5ce970e` | Option lists |
| License and privacy page | `ev_cc78792c5b0435c74a987f22e9c21fc0c460f40c0c659dad5355c211f3209ca7` | License rules |

Browser: provider-owned headless Edge/Chromium, viewport 1280×720, locale en-US, timezone UTC. Network initiator stacks were not available. Response bodies are Playwright body bytes, not guaranteed wire bytes.

## Product in one paragraph

SimulTrain 12 is a browser business game. A team of 3 or 4 people shares one license and plays the project manager of a mid-size project. They plan work and people, then run a compressed clock. The clock brings meetings, mail, phone calls, and decisions. Cost, schedule, quality, and motivation move as a result. A trainer debriefs. There are no per-person accounts. Progress, scores, and reports are stored against the license number.

The public demo is the same learner shell with `sessionID` `demo`. On-screen copy says the demo stops at the end of the first project week, and that it lasts 12.5 minutes once the clock starts (1 project week instead of 12).

## Two sites, one product

| Surface | URL | Role |
| --- | --- | --- |
| Marketing site | `https://simultrain.swiss/` | Static brochure, password gate, contact form |
| Learner app | `https://simultrain.swiss/smt12/` | Simulation. Page sets `var isPHP = true` and loads `js1/smt.min.js` |
| Chinese brochure | `index-cn.html` | Alternate marketing page. Not opened |
| License text | `/license-agreement-and-data-privacy/` | Rules for licenses, privacy, trainer desk |
| Trainer desk | Not in the learner shell | Separate trainer tool, named on the marketing site and the license page. Not observed |

The learner page title is “Simultrain® 12 | project management business game”. The shell warns that Firefox has a known bug where the clock does not stop at the end of a period, and recommends another browser. The license page requires a current Chrome, Edge, or Firefox on 64-bit Windows 10 or 11, JavaScript on, about 5 Mbps, mouse and keyboard, and at least 1024×768. Touch and screen readers are best-effort. The license page says the app is not fully WCAG 2.1.

Hosting claim on the license page: Infomaniak data centers in Switzerland. Not verified from network geography.

## Actors

| Actor | What they do | Account |
| --- | --- | --- |
| Learner team | One shared browser session. Plan, assign, run the clock, answer mail and decisions | None. They type an 8-digit license number |
| Trainer | Sets the session, watches teams, debriefs. Marketing site says the trainer desk can watch a simulation in passive mode | Separate TrainerDesk agreement. Not observed |
| STS operator | Issues licenses, support via the trainer, train-the-trainer courses | Outside the app |

Support path on the marketing footer is an Atlassian customer portal. Contact mail on the brochure is `info@sts.ch`. The in-app Help item was not opened in a completed capture.

## Marketing site behavior

The homepage is one long page, jQuery, not a SPA.

Navigation: Features, Description, Resources, License, Chinese, Contact (modal), Login.

Hero: short product statement, a link to a PDF about virtual teams (`#PlayApartTogether`), **Try the Demo** (`/smt12/?pwd=0`), **Login** (`/smt12/`).

Features claimed on the page, and what the demo actually showed:

| Claim | Observed in the demo |
| --- | --- |
| New layout and visuals | Fixed left icon bar, one main canvas, absolute-positioned controls |
| One-page simulation control, risk level, advanced controls | Yes. See configuration |
| Resource leveling chart, assignment on the task page, resource types | Team screen has a **Resource leveling** button and a week-by-week staffing strip. Task page and the leveling result were not opened |
| Trainer status board, team identification, passive mode | Not in the learner demo |

Description tabs (Overview, Audience, Concept, Practical info) are on-page sections, not routes. Practical claims, not re-tested: 22+ languages, up to about 10 scenarios per language, online only, 4–10 hours including debrief, often two half-days. Classroom use is the intended setting.

Resources block links a best-practices PDF, three YouTube tutorials (user, trainer, trainer desk), and `resources.html`. `resources.html` was not opened.

A password modal asks for an 8-digit number (`type="number"`, minlength 8, maxlength 8) and says the license decides which product version to open. A commented nav item points at `/plus/` for a strategic-management product. That version was not opened.

Contact form posts to `dynaform.php` with name, email, country, and message, and names `info@sts.ch` as the recipient. Submit was not sent.

Footer courses are “Discover SimulTrain” webinars with Microsoft registration links. Dates on the page at capture time: English 30 Jan, 27 Mar, 30 Apr, 26 Jun; French 27 Feb, 29 May; German 13 Feb, 27 Apr, 12 Jun.

## License behavior that shapes the data model

From the license page, which is product behavior, not just legal boilerplate:

- One license number runs one simulation for one team of 3 or 4.
- No personal accounts and no participant personal data are supposed to be stored.
- Progress, scores, and reports are bound to the license number.
- License data is kept at least 90 days after the simulation, then may be archived.
- Demo use is evaluation only and has restricted features.
- Settings (language, speed, and the other control-page parameters) are chosen before start and cannot be changed after the simulation starts.
- License duration claimed: 365 days from issuance unless agreed otherwise. Unused licenses may be removed. Fees are described as one simulation per license.
- TrainerDesk is a separate program under a separate agreement.
- Learners do not get direct STS support. The trainer is the contact.

The learner client matches the “settings freeze after start” rule: **Save and Go** leaves the control page and later saves of config are skipped when the session is a demo.

## Entering the learner app

1. Brochure **Login** opens `/smt12/` with no password.
2. Brochure **Try the Demo** opens `/smt12/?pwd=0`.
3. The client treats the password as an 8-digit license. The demo query value `0` is sent to the server as `pwd=00000000`.
4. On load, before Save and Go, the shell already shows the left menu and the Simulation Control page. Clock label is `8:00 | Monday | Week 1`.
5. **Save and Go** applies the control form and opens the project. The corner reads `v12.2, en, ecom, DEMO`.

An early `getteamname.php` call went out with a different 8-digit value and came back empty. The client function `getTeamName` is skipped once demo mode is on. Do not treat any unused placeholder as a working license. Full-license team names were not observed.

Password check lives in `php/chkp.php` (`password`, `active`). If the body is shorter than 8 characters, the client replaces the clock object with an empty object. That failure path was not exercised. Portfolio and extension checks exist in the script (`portfolio_licence_status.php`, `is_extension_date_valid.php`, `is_minerva_simultrain.php`) and were not called in the demo session.

## Shell

Persistent left bar, top to bottom:

| Control id | Label before save | Label after save on the ecom demo |
| --- | --- | --- |
| `menuTime` | `8:00 \| Monday \| Week 1` | Same until a clock run, which was not started |
| `office` | Office | Office |
| `budget` | Budget | Budget |
| `gantt` | Gantt | Gantt Diagram |
| `resources` | Resources | Team |
| `network` | Activity Network | Activity Network |
| `reports` | Reports | Reports |
| `calendar` | Calendar | Calendar |
| `riskregister` | Risk Register | Still in the menu. Screen not captured |
| `racimatrix` | RACI Matrix | Still in the menu. Screen not captured |
| `control` | Control | Control |
| `help` | Help | Help. Screen not captured |

Footer of the bar: © STS, version `online build 12.2.241`, `sessionID demo`.

The main stage is `#content` / `#page`. Layout is absolute positioning over a fixed design size (reports DOM used a 1398×720 background box). This is a single page that swaps the contents of `#page`. There is no router URL change. The address stayed `/smt12/?pwd=0` on every screen.

A back control `←` (`#n3`) is on the control page. Its destination was not tested.

## Simulation Control

Shown first. Each setting is a button that opens a choice list. Observed lists:

| Button id | Label | Demo default | Choices observed |
| --- | --- | --- | --- |
| `language` | Language | English | English, German, French, Brazilian, 中文, Croatian, Czech, Danish, Dutch, Spanish, Italian, Japanese, Korean, Lithuanian, Uzbek, Polski, Portuguese, Russian, Sweden, Turkish, Vietnamese, Arabic, Quechua |
| `scenario` | Scenario | `ecom` | `ecom`, `agile`, `agilehybrid`, `event`, `hres`, `marketing`, `oilandgas`, `product`, `productionmove`, `reorghr`, `reorg`, `risk`, `pm1`, `pm2`, `pm3` |
| `periods` | Periods | 2 | 2 Periods, 3 Periods |
| `speed` | Speed | Demo | Test, Demo, Fast 4, Fast 3, Fast 2, Fast 1, Standard, Slow 1, Slow 2, Slow 3 |
| `risk` | Risk | No | No, Yes |
| `raci` | RACI Matrix | No | Not opened. Same Yes/No pattern is likely. Unconfirmed |
| `change` | Plan Changes | No | Not opened |
| `planned` | Already Planned | Yes | No, Yes |
| `difficultyCost` | Difficulty Cost | Standard | Easy, Standard, Hard |
| `difficultySchedule` | Difficulty Schedule | Standard | Same control pattern. List not re-opened |
| `difficultyQuality` | Difficulty Quality | Standard | Same |
| `difficultyMotivation` | Difficulty Motivation | Standard | Same |
| `difficultyRisk` | Difficulty Risk | Standard | Same |
| `save` | Save and Go | — | Commits and enters the project |

Demo footnote on the page: “The DEMO lasts 12.5 minutes when clock starts (1 project week instead of 12).”

Choosing a language issues `HEAD` requests for `scenario/<code>_<lang>.txt` for many scenario codes (`agile`, `agilehybrid`, `event`, `hres`, `marketing`, `oilandgas`, `product`, `productionmove`, `reorghr`, `reorg`, `retrofit`, `risk`, `pm1`–`pm4`, plus the menu codes). `retrofit` and `pm4` were probed and were not in the visible scenario menu. A missing file is how the client decides a scenario is unavailable for that language. One language click logged `22 g.isAgile=false` from `smt.min.js`.

`Save and Go` is the freeze point described in the license. After it, the script’s `saveConfig` posts only when the session is not a demo and is active.

## Screens after Save and Go

Scenario actually entered: English, `ecom`, speed Demo, risk No, RACI No, plan changes No, already planned Yes, all difficulties Standard. Only this combination was walked.

### Office / performance (landing view)

The first view after save is a performance board, still under the Office icon:

- Performance indexes: Costs 100%, Schedule 100%, Quality 100%, Motivation 100%.
- Badge: `v12.2, en, ecom, DEMO`.
- Banner: demo stops at the end of the first week.

The string pack also names **Start Clock** and **Pause Clock**, mail, voicemail, and phone. Those controls were not on the accessibility tree of this landing view, so either they sit on a deeper Office state or they appear only after an action that was not clicked. Do not assume the landing board is the whole Office.

### Budget

A task table plus project-level cost buckets.

Columns read from the accessibility name: Progress, Actual Costs, Estimated costs at completion, Planned Costs, and the people assigned.

Rows observed for this scenario: 17 activities (Specifications through Start Operation), then Project management, Material, Other costs (meetings, team events, training), and a Total. At minute zero, progress is 0% and actual cost is 0. Planned and estimated figures differ on some tasks, which is the planning gap the player is meant to see. Some tasks already show names (Fred, Sue, Hans, Tim, Livio). That matches **Already Planned = Yes**.

### Gantt Diagram

- Time axis: Week 1 through Week 12, plus a Today marker. The demo still stops after week 1. The axis stays a 12-week plan.
- One row per activity, with assignee names on some bars.
- Legend: Initial planning, Activity, Critical Activity, Error Correction, Milestone, Quality Review, Slack.
- Quality-review markers are numbered.

Bars are images. Clicking a bar to open the task page was not done.

### Team

- Rows of people across Week 1–12. Names on this scenario include Alex, Anna, Bill, Cindy, Felix, Fred, Hans, John, Livio, Luc, Marco, Paul, Peter, Sue, Ted, Tim.
- Some cells show activity numbers (Fred on 1 and 4, Hans on 3, Livio on 11, Sue on 1 and 3, Tim on 4).
- Legend: On Payroll, Available, Training, Sick, Holiday, Other project.
- Button: **Resource leveling**. The chart it draws was not opened.

### Activity Network

A precedence diagram of the same 17 activities. Boxes are images. Dependencies were visible as layout, not as a data table, so predecessor lists were not read off the screen.

### Reports

A menu of tiles (`div.rmenu`, ids `0`–`11`), not separate routes:

1. Project description
2. Organization Chart
3. Dashboard
4. Cost Performance Index (CPI)
5. Schedule Performance Index (SPI)
6. Quality
7. Motivation
8. Hours invested
9. Earned Value
10. Decisions taken
11. Learning Points
12. Status Report

No tile was opened. The client can save a status report (`svs.php` / `getstatus.php`). Those endpoints were not called in the demo. `saveStatus` is skipped when `g.demo` is set.

### Calendar

- Hours 8:00–19:00.
- Week buttons 1–12.
- Columns Monday–Friday.
- The week is preloaded with appointments (meetings, kick-off, trip, coaching, lunch, phone conference, status report, and similar). Treat the names as scenario content. An original product needs its own calendar script.
- A `?` control is on the page. It was not clicked.

### Not captured

Risk Register, RACI Matrix, Help, any report tile, any task page, resource leveling, mail, phone, a decision dialog, Start Clock, Pause Clock, end of week, and end of project. The string pack shows those features exist. Their screens were not observed because later browser captures timed out.

## Clock and session lifecycle

Inferred from the screen, the license page, and strings in the language pack. The clock was not started, so timing was not measured.

- Time display is hour, weekday, and project week. Workdays are Monday–Friday. Visible hours run 8:00–19:00.
- Speed changes how many real minutes a project week takes. The demo speed is defined as 12.5 real minutes for one project week.
- Periods split the run into 2 or 3 parts. Strings include “end of the period”, “end of the project”, and internal names `EndPeriod1` and `EndPeriod2`.
- The player can start and pause the clock. The license text says the parameter set cannot be changed after start.
- At the end of a period the clock is supposed to stop. The page itself says Firefox sometimes fails to stop it.
- Demo mode forces an early stop after week 1 and forces demo speed when demo is detected (`g.demo=true`, speed set to the demo index).
- A full license is expected to persist the event log as the clock runs (`svl.php`). The demo skips that write. The server can answer with a body containing `2#start`, which the client treats as a signal to start the clock if it is not already running. That response was not seen.

## Decisions, mail, and phone

Not clicked. Present in the UI string pack and in client symbols (`mail`, `blinkPhone`, `dec`):

- Mail list and a message body. Messages have sender, hour, and a read flag.
- Voicemail (`isVoiceMail`) and a phone icon that blinks.
- Decisions have a week, a prompt, at least two choices, and coach feedback. The player can postpone (“later this week”). If a decision is still open, a later event can record that someone else decided.
- Quality reviews and project reviews are first-class events, also drawn on the Gantt.
- Learning points are accumulated and can be written with `svf.php` (a named text file on the server). Skipped in the demo.

Do not copy STS decision text. Model the shape: trigger time, channel (mail, phone, meeting), choices, immediate feedback, and delayed consequence on cost, schedule, quality, or motivation.

## What the simulation is tracking

Observed names, not formulas. Scoring math was not recovered as a documented algorithm, and the numeric tables inside the script should not be copied.

Four headline indexes, each starting at 100% on a new plan:

- Cost
- Schedule
- Quality
- Motivation

Reports add CPI, SPI, hours, earned value, decisions taken, and learning points.

Money is split into task labor, project management, material, other costs, and (when risk is on) a risk cost line. The budget screen shows planned, actual, and estimate-at-completion.

Work is a network of activities with duration, predecessors, assignees, slack, a critical flag, milestones, error-correction work, and quality reviews.

People have a weekly state: on payroll, available, training, sick, holiday, or on another project. Assigning someone to a task is the main planning decision. Resource leveling is an explicit player action, not only an automatic function.

Risk and RACI are optional modules. With Risk = No and RACI = No, those menu entries were still visible. Whether they are inert until enabled was not tested.

Agile is a mode (`g.isAgile`), turned on by scenario choice. The walked scenario logged `isAgile=false`. Agile-specific screens were not opened.

## Client/server contract

The learner UI is a jQuery page. When `isPHP` is true, persistence is HTTP POST form bodies to `smt12/php/`. The script also has a `localStorage` branch keyed by session id, used when `isPHP` is false. The hosted page forces PHP.

Calls observed on demo load and on Save and Go:

| Call | Body observed | Response observed | When |
| --- | --- | --- | --- |
| `POST php/getteamname.php` | `pwd` (8 digits) | Empty HTML | Early. Client later skips this in demo mode |
| `POST php/getconfig.php` | `pwd=00000000` | Empty | Load. Empty means no saved config for the demo |
| `POST php/getpcid.php` | `pwd=00000000` | Empty | Load |
| `POST php/tt.php` | `key=en` | Large `id@text&` string pack | Save and Go, language pack |
| `POST php/getdata.php` | `key=task&id=1` … `id=17` | One semicolon row, about 30 bytes | Save and Go, activity plan |
| `POST php/getdata.php` | `key=res&id=1` … higher ids | One semicolon row | Save and Go, people |
| `HEAD scenario/<code>_<lang>.txt` | — | Status only | Language menu, availability probe |

`getdata.php` rows are positional, semicolon-separated, fixed width. Task rows and resource rows do not share the same column count. A short row looks like seven fields, the last of which is a comma-separated list of five numbers. A longer row adds two trailing numbers. Column meanings were not labeled by the server. Do not hard-code the demo numbers. Store a real schema (see the database section) and return JSON.

Named by the client, not called in this demo session:

| Endpoint | Client sends | Client expects | Demo behavior in the script |
| --- | --- | --- | --- |
| `chkp.php` | `password`, `active` | Body of at least 8 characters or the clock is cleared | Not called |
| `svc.php` | `pwd`, `config` (the settings list) | A positive result, else an alert that config could not be saved | Skipped when `g.demo` or inactive |
| `svl.php` | `pwd`, `log` (joined session log) | May include `2#start` to start the clock | Skipped in demo |
| `getlog.php` | `pwd` | Previous log text | Not called |
| `svs.php` | `pwd`, `statusreport` | Positive result | Skipped in demo |
| `getstatus.php` | `pwd` | Saved status text | Not called |
| `svid.php` | `pwd`, `pcid` | Positive result | Skipped in demo |
| `svf.php` | `name`, `txt` | `1` on success. Used for learning-point text | Skipped in demo |
| `savemessage.php` | `message`, `pwd` | Logged only | Not called |
| `changestatus.php` | `status`, `pwd` | Logged only | Not called |
| `portfolio_licence_status.php` | `password`, `portfolioEntry` | JSON | Not called |
| `is_extension_date_valid.php` | `password` | JSON boolean | Not called |
| `is_minerva_simultrain.php` | `password` | Loose body | Not called |

`tt.php` is both the chrome language and a large amount of scenario wording, in one `id@text&` table (ids observed from 101 into the 2700s for English). Split those in a new system: UI strings in the client, scenario copy in scenario records.

Error alerts in the script are numbered (124 text pack, 126 config, 128 pc id, 129 file, 130 missing data key). The demo did not raise them.

## Domain model for a new system

Design this as data, not as a 200 KB script.

**License.** Eight-digit public id, status (unused, active, expired), product line (learner sim vs trainer desk), expiry, demo flag, team display name, created time. No user table for learners.

**Session.** One row per license run. Frozen config: language, scenario, period count, speed, risk on, RACI on, plan-changes on, already-planned on, five difficulty levels. Clock: running flag, project minute, weekday, week, period index. Version of the rules used.

**Scenario.** Code, language, title, week count, currency amounts, work calendar (days, start hour, end hour).

**Activity.** Order, name, planned duration, planned cost, predecessors, milestone flag, quality-review points, whether it starts pre-assigned.

**Resource.** Name, portrait, cost rate, weekly availability mask (payroll, available, training, sick, holiday, other project), skill or productivity weights if you choose to model them.

**Assignment.** Activity, resource, hours or percent per week. Leveling produces a proposed assignment the team can accept.

**Calendar item.** Week, weekday, start hour, duration, kind (meeting, mail, phone, decision, review), title, body, optional speaker.

**Decision.** Prompt, choices, feedback per choice, effect keys (cost, schedule, quality, motivation, risk), deadline in project time, postponed flag, resolved-by (team or auto).

**Message.** Channel, sender, project time, body, read flag, voice attachment id.

**Risk.** Only if the module is on. Description, related activity, probability band, cost impact, response the team picked, status.

**RACI.** Only if the module is on. Activity × role with R, A, C, I, and an optional quality mark.

**Snapshot.** Each clock tick or each player action writes indexes: cost, schedule, quality, motivation, actual cost, earned value, CPI, SPI, hours. This is the dashboard and the report charts.

**Log.** Append-only player actions and clock marks, keyed by license. This replaces `svl.php`.

**Report.** Generated views over snapshots plus the narrative fields the team types into a status report. Learning points are a list of strings produced by decisions.

## Suggested build

### Vue client

One route for the brochure and one route for the sim. Inside the sim, do not copy the absolute-positioned canvas. Use a real app shell:

- Left nav with the eleven destinations above, plus the clock chip.
- A control wizard that is read-only after start.
- Views: dashboard, budget table, Gantt (a chart component fed by activities), team heatmap, network graph, report gallery, calendar, risk register, RACI grid, help.
- Overlays: mail drawer, phone/voicemail, decision modal, task editor.
- i18n catalogs for chrome only. Scenario text comes from the API in the selected language.
- The clock is a display of server time. The client sends start, pause, and player actions. It does not own the score.

### API, .NET or Python

Either stack is enough. Pick one.

- ASP.NET Core minimal APIs, or Python FastAPI.
- Auth for learners is the license id plus a server session cookie issued after the license checks out. Do not put the license in a query string the way the demo does.
- Trainers are the only real user accounts, for the desk product.
- Authoritative clock in a background worker. On each project hour, load due events, apply rules, append a snapshot, push the new state over WebSocket or SSE.
- All writes are idempotent per `(license, client_action_id)`.
- Demo licenses are a flag on the license row: one week, demo speed, no long-term save. Do not special-case this with scattered `if demo` skips. Skip retention, not correctness.

### Database

PostgreSQL is the straightforward choice.

- `licenses`, `sessions`, `session_config`
- `scenarios`, `scenario_locales`
- `activities`, `dependencies`, `resources`, `resource_weeks`, `assignments`
- `events` (calendar, mail, phone, decisions) with a JSON payload checked by a schema per event type
- `decisions`, `decision_options`, `decision_outcomes`
- `messages`
- `risks`, `raci_cells` (present only when the session enabled them)
- `snapshots` (time series for the four indexes and earned value)
- `action_log`
- `status_reports`, `learning_points`

Keep scenario content in rows so a trainer-authored scenario is the same shape as a built-in one. The marketing site says trainers can create scenarios. That editor was not observed. Treat it as a later module: CRUD on the tables above, not a second engine.

### Rules engine

Put cost, schedule, quality, and motivation in one module with tests. Inputs are the frozen difficulty settings, assignments versus availability, and decision outcomes. Outputs are the next snapshot. Publish the formulas you invent. Do not lift coefficients out of the STS script.

Suggested first slice, enough to demo the loop:

1. License gate and control page with the settings in the table above.
2. Save and Go creates a session and loads one original scenario (about 15 activities, 10 people, 12 weeks).
3. Budget, Gantt, and Team read that plan. The team can reassign people while the clock is stopped.
4. Start Clock runs one project day in a few real seconds and drops two mail items and one decision.
5. Dashboard indexes move by your own rules.
6. Pause at the end of week 1 for a demo license. A normal license continues.

Second slice: network view, calendar, reports (CPI, SPI, earned value, status report), resource leveling.

Third slice: risk module, RACI module, agile scenario flag, trainer desk (list sessions, open one read-only, compare teams).

## Unknowns

- Exact column meaning of `getdata.php` rows.
- Whether Risk = No hides the register or shows it empty.
- Task-page fields and how assignment is edited.
- What Resource leveling changes.
- Mail, phone, and decision screen layout.
- Clock start control location and the real duration of each speed.
- How 2 periods and 3 periods split the weeks.
- What a full (non-demo) license returns from `getconfig.php` and `getlog.php`.
- Trainer desk screens, passive mode, and multi-team board.
- The `/plus/` product.
- Whether `scenario/*.txt` files are still used after the `HEAD` probe, or whether all copy now comes from `tt.php`.
- Help content.
- Report tile contents.
- Any WebSocket. None was seen. Updates on the walked screens were full page redraws inside `#page`.
