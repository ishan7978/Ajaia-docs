# Submission

**Candidate:** Ishan
**Live product URL:** `< https://ajaia-docs-vxb9.onrender.com >`
**Walkthrough video:** `< https://drive.google.com/file/d/1kE8auJ01FNHxP1uUvPbFubFXOu9rd_Ug/view?usp=sharing >` 

## Test accounts (password for all: `demo1234`)

| User | Notes |
|---|---|
| alice | Owns "Welcome to Ajaia Docs", shared with bob (edit) and carol (view) |
| bob | Can edit alice's welcome doc; owns a private doc |
| carol | View-only on alice's welcome doc |

## What is included

| File / folder | Contents |
|---|---|
| `config/`, `docs/`, `manage.py` | Source code (Django project + app) |
| `requirements.txt`, `build.sh`, `render.yaml` | Dependencies and deployment config |
| `README.md` | Local setup, run, test and deploy instructions; sharing walkthrough |
| `ARCHITECTURE.md` | Architecture note: priorities, data model, access rules, trade-offs |
| `AI_WORKFLOW.md` | AI-native workflow note |
| `VIDEO_LINK.txt` | Walkthrough video URL |
| `SUBMISSION.md` | This file |

## Status

**Working end to end:** create, rename, rich-text edit (bold, italic, underline, H1–H3, bullet/numbered lists), autosave, reopen; import .txt/.md/.docx as a new document; share by username with view/edit access, change or revoke; Owned vs Shared lists with role badges; persistence across refresh; server-side permission checks, validation and HTML sanitisation; 18 automated tests.

**Incomplete / not built (intentional):** real-time collaboration (last save wins), comments, version history, export, images/tables, sign-up and password reset (users are seeded).

**Known limitation:** on Render's free tier SQLite data resets on redeploy; demo users are re-seeded on start. Set `DATABASE_URL` to use Postgres.

**With 2–4 more hours:** version history with restore, Markdown/PDF export, conflict warning on concurrent edits, browser end-to-end tests.
