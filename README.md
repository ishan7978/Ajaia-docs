# Ajaia Docs — lightweight collaborative document editor

A small full-stack Google-Docs-style editor: create, rename, rich-text edit, import files, and share documents between users.

**Live demo:** `< https://ajaia-docs-vxb9.onrender.com >`
**Test accounts** (password for all: `demo1234`): `alice`, `bob`, `carol`

## Features

| Area | What works |
|---|---|
| Documents | Create, rename (title field), edit, autosave (debounced), reopen, delete (owner only) |
| Rich text | Bold, italic, underline, headings (H1–H3), bulleted and numbered lists, clear formatting |
| File upload | Import **.txt, .md, .docx** into a **new editable document** (max 2 MB). Supported types are shown in the UI. Anything else is rejected with a clear message |
| Sharing | Owner shares by username with **view** or **edit** access; owner can change or revoke access. List is split into **My documents** (badge "Owned by me") and **Shared with me** (badge shows "Can edit" / "View only" and the owner) |
| Persistence | SQLite by default (Postgres via `DATABASE_URL`). Content is stored as sanitised HTML so formatting survives refresh |
| Quality | Server-side permission checks, input validation, HTML sanitisation, 18 automated tests |

## Run locally

Requires Python 3.11+.

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo      # creates alice / bob / carol + a sample shared document
python manage.py runserver
```

Open http://127.0.0.1:8000 and log in as `alice` / `demo1234`.

The editor loads Quill from the jsDelivr CDN, so an internet connection is needed in the browser.

### Run the tests

```bash
python manage.py test
```

## Try the sharing flow (2 minutes)

1. Log in as **alice**. Open "Welcome to Ajaia Docs" (already shared with bob = edit, carol = view).
2. In another browser or a private window, log in as **bob**. It appears under **Shared with me** with "Can edit". Edit it. Changes autosave.
3. Log in as **carol**. Same document, but the editor is read-only and the title is locked.
4. As alice, create a new document, share it with `carol` as "Can view", then remove her access. She loses it immediately.

## Deploy (Render, free)

1. Push this folder to a GitHub repo.
2. Render → **New → Blueprint** → select the repo. `render.yaml` configures everything.
3. After deploy, open the service URL and log in as `alice`.

**Known limitation:** Render's free tier has an ephemeral disk, so with SQLite the data resets on redeploy or restart. The start command re-seeds the demo users each time so reviewers can always log in. For durable data, create a free Postgres instance (Render or Supabase) and set the `DATABASE_URL` environment variable. No code changes are needed.

## Configuration

| Variable | Purpose | Default |
|---|---|---|
| `DEBUG` | `1` for local dev, `0` in production | `1` |
| `SECRET_KEY` | Required when `DEBUG=0` | dev key |
| `ALLOWED_HOSTS` | Comma-separated hosts | localhost |
| `DATABASE_URL` | Use Postgres instead of SQLite | unset |

## Project layout

```
config/            Django settings and root URLs
docs/models.py     Document, DocumentShare
docs/views.py      Pages + JSON endpoints (save, share, unshare, upload)
docs/importers.py  .txt / .md / .docx -> sanitised HTML
docs/sanitize.py   HTML allow-list (bleach)
docs/templates/    list, editor, login
docs/tests.py      Automated tests
```

## Scope cuts and what I'd do next

Deliberately not built: real-time multi-user editing, comments, version history, export, images, tables, password reset or sign-up (users are seeded).

With another 2–4 hours: (1) version history with restore, (2) export to Markdown/PDF, (3) simple "last edited by" and conflict warning (today the last save wins), (4) email-style invite by address, (5) browser end-to-end tests.
