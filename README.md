# Corelytic ERP

Frappe/ERPNext app for **Calco PolyTechnik Pvt Ltd**. One app, five modules:

| Module | Folder | What it does | Docs |
| --- | --- | --- | --- |
| Corelytic Branding | `corelytic_erp/corelytic_branding/` | Branding of login, desk home and workspaces; the "Corelytic ERP" apps tile | this README |
| Corelytic WhatsApp | `corelytic_erp/corelytic_whatsapp/` | WhatsApp messages and notification rules | `corelytic_erp/corelytic_whatsapp/README.md`, `docs/whatsapp.md` |
| Corelytic Assessment | `corelytic_erp/corelytic_assessment/` | Online candidate assessments for HRMS Job Applicants | `docs/recruitment.md`, `docs/recruitment-internals.md` |
| Corelytic AI | `corelytic_erp/corelytic_ai/` | AI Assistant: questions on ERP data in English / Hindi / Hinglish, within each user's permissions | `docs/ai.md` |
| Corelytic Interview | `corelytic_erp/corelytic_interview/` | Video interviews on HRMS Interview: scheduling, emails, room, recording, AI draft, results | `docs/interview.md`, `docs/interview-internals.md` |

Needs `erpnext` and `hrms`. Corelytic WhatsApp, Corelytic Assessment, Corelytic AI and Corelytic Interview were
separate apps (`grid_whatsapp`, `akash_recruitment_assessment`, `grid_ai`, `grid_interview`) and are
now modules of this app. The merge moved files and renamed import paths only; the logic is unchanged.

## Renamed from grid_erp (2026-11-08)

This app was called **grid_erp** ("Grid ERP") until 2026-11-08. Only names changed, no logic:

| Before | After |
| --- | --- |
| app `grid_erp`, title "Grid ERP" | app `corelytic_erp`, title "Corelytic ERP" (apps tile too) |
| module Grid ERP (`grid_erp/grid_erp/`) | module **Corelytic Branding** (`corelytic_erp/corelytic_branding/`) |
| module Grid AI (`grid_ai/`) | module **Corelytic AI** (`corelytic_ai/`) |
| module Grid WhatsApp (`grid_whatsapp/`) | module **Corelytic WhatsApp** (`corelytic_whatsapp/`) |
| module Grid Interview (`grid_interview/`) | module **Corelytic Interview** (`corelytic_interview/`) |
| app `calco_calls` (separate repo) | app `corelytic_calls`, module Corelytic Calls |

In a second step the same day, the remaining "Grid" names became "Corelytic" too:

| Before | After |
| --- | --- |
| DocTypes Grid Interview * (16), Grid Branding Settings | Corelytic Interview *, Corelytic Branding Settings (tables renamed, data kept) |
| Roles Grid Interview Administrator / HR User / Reviewer / Candidate | Corelytic Interview … (users keep their roles) |
| Print Formats Grid Tax Invoice, Grid Salary Slip, … (11) | Corelytic Tax Invoice, Corelytic Salary Slip, … (still the defaults) |
| Page `/desk/grid-interview-dashboard` | `/desk/corelytic-interview-dashboard` |
| Jinja helpers `grid_print_branding`, `grid_hsn`, … | `corelytic_print_branding`, `corelytic_hsn`, … (`templates/print/corelytic_print.html`) |
| folders `private/grid_interview_recordings`, `grid_interview_ingest` | `private/corelytic_interview_recordings`, `corelytic_interview_ingest` |

That part is the patch `patches/rename/grid_names_to_corelytic.py` (pre_model_sync, runs on
`bench migrate`): `frappe.rename_doc` renames each DocType's table and every link to it, Roles,
Print Formats and their default-format settings; it also moves stored passwords (`__Auth`, e.g. the
Jitsi secret), references to the two Single DocTypes, AI Tool Configurations and the storage
folders. The room pages' header `X-Grid-Interview` is still accepted next to
`X-Corelytic-Interview` for pages that were open during the switch.

Third step (same day): module **Recruitment Assessment → Corelytic Assessment** (folder
`recruitment_assessment/` → `corelytic_assessment/`, desk route `/desk/corelytic-assessment`) and its
16 DocTypes: `Assessment …` → `Corelytic Assessment …` (Template, Assignment, Attempt, Result,
Settings, …) and `Question Bank / Option` → `Corelytic Question Bank / Option`. Patch
`patches/rename/assessment_names_to_corelytic.py` (shared steps in `patches/rename/utils.py`).
Field names (`assessment_template`, …) are DB columns and did not change; the candidate URL
`/assessment-portal` did not change; old `…recruitment_assessment.api/certificate/…` method URLs
(under grid_erp or corelytic_erp) are mapped in `hooks.py`.

Kept on purpose: history (comments, versions, deleted documents, route history) and text about the
*former* apps (`grid_ai`, `grid_interview`, `grid_whatsapp`). CSS Grid layout (`display: grid`)
and Frappe's own `grid` API are not names and are unchanged.

Old URLs keep working: `hooks.py → override_whitelisted_methods` maps the public
`grid_erp.*` methods (WhatsApp webhook, candidate portal / interview / assessment APIs,
certificate, `assets.serve`) to the new paths; corelytic_calls does the same for `calco_calls.api.*`
(phones with the old PWA cached). The WhatsApp providers can be switched to the new webhook URL
`/api/method/corelytic_erp.corelytic_whatsapp.api.webhook.status_callback` at any time.

Moving an existing site (done on griderp.in): the bench needs `apps/corelytic_erp` and
`apps/corelytic_calls` instead of the old folders, then, **before** `bench migrate`, run
`~/griderp_build/scripts/rename-db.py` in `bench --site <site> console`. It renames the installed
apps, Module Defs (and every link to them), Patch Log entries (so old patches do not run again)
and app-name columns, and removes the old Sidebars / Dock / Scheduled Job Types that migrate
recreates. Then `bench --site <site> migrate`.

Candidates use **one portal, `/candidate-portal`**: their assessments, interviews, applications,
results, profile and references. Taking an assessment still opens `/assessment-portal`.

At a glance:

```text
corelytic_erp/
├── README.md                     module table + full file tree (below)
├── docs/                         whatsapp.md, recruitment*.md, ai.md, interview.md, interview-internals.md
├── deploy/                       docker/ (image layer), corelytic_ai/ (egress proxy)
└── corelytic_erp/
    ├── hooks.py                  one section per module
    ├── corelytic_branding/            Branding module, print formats
    ├── corelytic_whatsapp/            WhatsApp module
    ├── corelytic_assessment/   Assessment module (doctypes, reports, workflow, api…)
    ├── corelytic_ai/                  AI Assistant module (doctypes, chat page, providers, tools…)
    ├── corelytic_interview/           Interview module (doctypes, pages, api, services, video…)
    ├── www/candidate-portal/     Candidate portal (assessments + interviews)
    ├── www/assessment-portal/    Taking an assessment (proctored)
    ├── www/interview/            Interview join link + video room
    ├── templates/                Interview emails, portal header
    ├── dock/                     the "Corelytic ERP" tile's module rail
    └── public/js|css/corelytic_assessment/, public/js|css|images/corelytic_interview/
```

On the desk (`/apps`) all five modules sit under one tile, **Corelytic ERP**. Its rail lists
WhatsApp, Corelytic Assessment, Interviews, AI Assistant and Branding; each opens its module's sidebar.

## Desk navigation (Frappe 16.51)

Frappe 16.51 builds the desk from three pieces of app data; corelytic_erp ships all three:

| Piece | File | What it does |
| --- | --- | --- |
| Apps screen tile | `hooks.py` → `add_to_apps_screen` | One tile, "Corelytic ERP", on `/apps`; opens `/desk/corelytic-assessment` |
| Dock (rail) | `corelytic_erp/dock/corelytic_erp/corelytic_erp.json` | Entries on the tile's rail, one per module sidebar |
| Sidebar | `<module>/sidebar/<module>/<module>.json` | The left menu of a module: Corelytic WhatsApp, Corelytic Assessment, Corelytic Interview, Corelytic AI, Corelytic Branding |

A rail entry is shown only to users who may see its module (Role → Modules). After changing a
sidebar or the dock, bump its `modified` and run `bench migrate`. Older versions used a
"Business Suite" desktop folder and Workspace Sidebars, which Frappe 16.51 no longer loads;
`desktop.py` removes their leftovers on migrate.

## Branding

The branding changes presentation only: native routes, permissions and workspace
data stay as ERPNext defines them.

## Changing logo, text or colours

Everything visible is edited from the desk, with no code change:

1. Log in as `Administrator`.
2. Open **Corelytic Branding Settings** (`/desk/corelytic-branding-settings`).
3. Click **Unlock to Edit** and enter the branding password.
4. Edit, **Save**, then refresh the page.

| Section | Controls |
| --- | --- |
| Company | Company name, ERP name, footer version, browser tab titles |
| Images | Logo, favicon, home banner image (blank = built-in Calco image) |
| Banner Text | Tagline, capabilities, values, description, footer line, workspaces heading |
| Login Page | Heading, subtitle prefix, access and connection notices |
| Colours | Primary, primary dark, dark header, text, page background |
| Workspace Order | Optional home-page order, one workspace per line |

A blank field falls back to the built-in default in `calco_workspace_config.js`.

### Access and password

- Only the `Administrator` user can open the settings (`branding.py: has_permission`).
- Editing needs the branding password; a correct password unlocks editing for
  15 minutes in that login session. Five attempts are allowed per 5 minutes.
- The code stores only a hash of the password (`branding.py: DEFAULT_PASSWORD_HASH`).
  To use a different password on one site, set `corelytic_branding_password_hash` in
  that site's `site_config.json` to a hash from `frappe.utils.password.passlibctx.hash()`.

## Print formats

Eleven standard Jinja print formats (module Corelytic Branding), branded from **Corelytic Branding Settings**
(logo, company name, tagline, footer line, colours). Only the print layout is custom; the
DocTypes are standard ERPNext / HRMS. Full documentation: `docs/print-formats.md`.

| Print format | DocType | Notes |
| --- | --- | --- |
| Corelytic Offer Letter | Job Offer | Offer terms table, terms, candidate acceptance |
| Corelytic Appointment Letter | Appointment Letter | Introduction, numbered terms, closing notes |
| Corelytic Salary Slip | Salary Slip | Earnings / deductions side by side, net pay in words |
| Corelytic Experience Letter | Employee | Left employees: "was employed … to <relieving date>"; active: "has been working since" |
| Corelytic Relieving Letter | Employee | Uses Resignation Letter Date and Relieving Date |
| Corelytic Quotation | Quotation | Payment terms, bank details |
| Corelytic Tax Invoice | Sales Invoice | Credit / Debit Note title for returns; HSN, GSTIN, bank details |
| Corelytic Delivery Note | Delivery Note | Transport details; amounts hidden with "Print Without Amount" |
| Corelytic Request for Quotation | Request for Quotation | Per supplier (Tools > Download PDF picks the supplier) |
| Corelytic Purchase Order | Purchase Order | Bill to / ship to, payment terms |
| Corelytic Payment Receipt | Payment Entry | Receipt for Receive, Payment Voucher for Pay |

Files: `corelytic_branding/print_format/<name>/<name>.html` (one per format),
`templates/print/corelytic_print.html` (shared header, boxes, totals, signatures, footer, CSS) and
`printing.py` (Jinja methods registered in `hooks.py > jinja`). The patch
`patches/print_formats/set_default_print_formats.py` makes them the default format once;
Employee keeps its default, so pick the two letters from the print format list.

Where the data comes from: company address = the Company's primary address (Address with
"Is Your Company Address"), GSTIN = Company / Customer / Supplier **Tax ID**, HSN = Item
**Customs Tariff Number** (or India Compliance's HSN field when installed), bank details =
the company's default **Bank Account**. A missing designation or relieving date prints in red
as `[… not set]`.

PDFs are made by wkhtmltopdf: layout uses tables (no flexbox / CSS variables), and letter
paragraphs avoid inline bold, which wkhtmltopdf renders without the space before it.

## Code layout

```text
corelytic_erp/                                  repository root
├── README.md                              this file
├── pyproject.toml
├── docs/
│   ├── whatsapp.md                        Corelytic WhatsApp guide
│   ├── recruitment.md                     Recruitment process, step by step (Hinglish)
│   ├── recruitment-internals.md           Recruitment internals: documents, fields, flow
│   ├── ai.md                              Corelytic AI: how it works, setup, migrating from the corelytic_ai app
│   ├── interview.md                       Interview process + candidate portal, step by step (Hinglish)
│   └── interview-internals.md             Interview internals: code, flows, security, deploy
├── deploy/
│   ├── docker/                            Image layer (Containerfile, build.sh)
│   └── corelytic_ai/egress_proxy.py            Optional HTTPS egress proxy for AI provider APIs
└── corelytic_erp/                              the Python package (the app)
    ├── hooks.py                           All hooks, one section per module
    ├── modules.txt                        Corelytic Branding, Corelytic WhatsApp, Corelytic Assessment, Corelytic AI, Corelytic Interview
    ├── patches.txt / patches/             Data patches (patches/corelytic_assessment/, patches/corelytic_ai/, patches/corelytic_interview/)
    ├── fixtures/                          "Assessment Invitation" Email Template
    │
    │   ── shared app files ──
    ├── assets.py                          Serves public/ files through the backend
    ├── branding.py                        Serves branding settings to desk/login; edit lock
    ├── desktop.py                         Removes desk icons / sidebars of older versions on migrate
    ├── dock/corelytic_erp/corelytic_erp.json        "Corelytic ERP" tile rail: WhatsApp, Recruitment, Interviews, AI Assistant, Branding
    │
    │   ── modules (each has sidebar/<module>/ = its left menu on the desk) ──
    ├── corelytic_branding/                     Module "Corelytic Branding"
    │   └── doctype/corelytic_branding_settings/, sidebar/corelytic_branding/
    ├── corelytic_whatsapp/                     Module "Corelytic WhatsApp"
    │   ├── doctype/                       WhatsApp Instance, Settings, Template, Notification Rule/Log …
    │   ├── sidebar/corelytic_whatsapp/         Desk menu
    │   ├── services/                      notification engine, dispatcher, providers (Evolution, eValidation)
    │   ├── api/                           webhook, notification APIs
    │   └── install.py, seed.py, seed_data/, tests/, utils/
    ├── corelytic_assessment/            Module "Corelytic Assessment"
    │   ├── doctype/                       Assessment Template/Assignment/Attempt/Result, Question Bank, Settings …
    │   ├── report/                        Leaderboard, pending/completed/expired, violations, analytics
    │   ├── workspace/                     "Corelytic Assessment" workspace page (the tile's home)
    │   ├── sidebar/corelytic_assessment/  Desk menu (assessments, results, reports, setup)
    │   ├── workflow.py                    Template choice + auto-send on Shortlist
    │   ├── service.py                     Assignment, login, start, autosave, submit, scoring
    │   ├── api.py                         Whitelisted APIs for the portal and HR
    │   ├── notifications.py               Invitation email
    │   ├── install.py, seed.py            Custom fields, roles, starter templates
    │   └── scheduler.py, evaluation.py, ai_evaluation.py, certificate.py, …
    ├── corelytic_ai/                           Module "Corelytic AI" (details: docs/ai.md)
    │   ├── doctype/                       AI Settings, AI Tool Configuration, AI Conversation, AI Query Log …
    │   ├── page/ai_assistant/             Chat page (/desk/ai-assistant)
    │   ├── sidebar/corelytic_ai/               Desk menu (chat, usage, settings)
    │   ├── report/ai_usage/               Questions, failures, tokens per user / day
    │   ├── api/                           chat.py, my_ai.py (whitelisted APIs for the page)
    │   ├── ai/                            Orchestrator, prompts, providers (OpenRouter, Ollama, OpenAI, Claude, Gemini)
    │   ├── tools/                         Registry, discovery, permissions, query builder, engine
    │   └── install.py, utils.py, exceptions.py, tests/
    ├── corelytic_interview/                    Module "Corelytic Interview" (details: docs/interview-internals.md)
    │   ├── doctype/                       Video Session, Recording, Transcript, Analysis, Result, Reference, Settings …
    │   ├── page/                          Interview Dashboard, Interview Scheduler
    │   ├── sidebar/corelytic_interview/        Desk menu
    │   ├── api/ → services/               Browser calls api/; rules, emails, status live in services/
    │   ├── integrations/hrms_adapter.py   The only code that reads HRMS
    │   └── video/, utils/, setup/, permissions.py, www_helpers.py, tests/
    │
    ├── www/candidate-portal/              Candidate portal (/candidate-portal): assessments, interviews, results, profile
    ├── www/assessment-portal/             Taking an assessment (/assessment-portal)
    ├── www/interview/                     Interview join link and video room
    ├── templates/emails/, templates/includes/  Interview emails, portal header
    └── public/
        ├── js/
        │   ├── calco_workspace_config.js  Branding: built-in defaults, merged with the settings
        │   ├── calco_branding.js          Branding: login panel, home banner, footer, brand bar
        │   ├── workspace_presentation.js  Branding: icon + description on workspace tiles
        │   └── corelytic_assessment/    Desk form scripts (job_applicant.js, assessment_*.js …)
        │                                  + proctoring.js (candidate portal)
        ├── css/
        │   ├── calco_branding.css, workspace_presentation.css
        │   └── corelytic_assessment/proctoring.css
        └── images/                        Default logo, favicon, banner, corelytic_erp.svg (tile), corelytic_ai.svg
```

How the settings reach the page: `branding.py` adds them to `frappe.boot` on
the desk and to an inline `<script>` in `<head>` on website/login pages.
`calco_workspace_config.js` merges them over its defaults into
`window.calcoWorkspaceViewConfig`, which `calco_branding.js` reads.

## How CSS, JS and images load

Branding files: `assets.py` serves everything under `public/` from the Python backend at
`/api/method/corelytic_erp.assets.serve?path=<file>&v=<hash>`, not from `/assets/`.
So nothing has to be built, copied or symlinked, and nginx needs no change:
the files load on any bench or Docker setup where the app is installed.

`<hash>` is computed from the files themselves, so after editing anything in
`public/` browsers fetch the new copy automatically. No version bump is needed.

Corelytic Assessment files load the normal Frappe way: desk form scripts through
`doctype_js` in `hooks.py`, and the portal page from `/assets/corelytic_erp/...`. After
changing `proctoring.js` or `proctoring.css`, bump `?v=` in
`www/assessment-portal/index.html`.

## Corelytic Assessment flow

```text
Job Applicant marked Shortlisted
  → hooks.py doc_events → corelytic_assessment/workflow.py (template: Job Opening, else default)
  → service.create_assignment → notifications.py emails the link immediately
  → candidate takes the test at /assessment-portal (proctoring.js, api.py)
  → Assessment Attempt (answers + one camera video with audio) → Assessment Result
  → HR scores on the Attempt form → Job Applicant "Assessment" tab updates
```

- Auto-send on Shortlist: **Assessment Settings > Auto-send Assessment on Shortlist**
  (on by default), or per Job Opening with *Auto-assign on Shortlist*.
- Manual: Job Applicant > Assessment > **Assign Assessment** (or **Assign Another Assessment**)
  to send any template.
- Step-by-step process: `docs/recruitment.md`. Documents, fields, code map:
  `docs/recruitment-internals.md`.

## Installing on any server

```bash
bench get-app https://github.com/akashdataanalyst/ErpNext-Demo.git
bench --site <site> install-app corelytic_erp   # existing site: bench --site <site> migrate
```

In Docker, the app code must be present in every Python container (backend,
queue-short, queue-long, scheduler), because they share one Redis cache.
After pulling new code, restart those containers and run
`bench --site <site> migrate`.

This setup (`~/frappe_docker/pwd.yml`) bind-mounts `custom_apps/hrms` and
`custom_apps/corelytic_erp` into every container, so code changes need no `docker cp`:

```bash
cd ~/frappe_docker
docker-compose -p frappe_docker -f pwd.yml restart backend queue-short queue-long scheduler
docker exec frappe_docker_backend_1 bench --site ampugerp.in migrate
docker exec frappe_docker_backend_1 bench --site ampugerp.in clear-cache
```

After editing `public/js/corelytic_assessment/proctoring.js` or its CSS, bump `?v=` in
`www/assessment-portal/index.html`.

## Version

1.4.0 (grid_interview merged as module Corelytic Interview; one candidate portal `/candidate-portal`).
On a site that had the `grid_interview` app: `bench --site <site> remove-from-installed-apps grid_interview`
before `bench migrate` (see `docs/interview-internals.md` › 11).

1.3.0 (desk navigation for Frappe 16.51; Drive removed from the image)


#test

