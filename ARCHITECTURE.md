# Architecture note

## What I prioritised, and why

The brief rewards depth in a few areas over breadth, so I spent the time on the loop a reviewer will actually click through: **create → edit → import → share → reopen as another user**, with permissions enforced on the server.

## Stack and reasoning

- **Django + SQLite (Postgres-ready).** One codebase covers auth, ORM, templates, CSRF and testing, so there is almost no glue code. `DATABASE_URL` switches to Postgres with no code change.
- **Quill 2 (CDN).** A mature editor that covers every required format (bold, italic, underline, headings, ordered/bullet lists) with a small footprint. No build step, so reviewers can run the project with `pip install` only.
- **Server-rendered pages + a few JSON endpoints.** Pages are plain Django templates. Only the editor needs JavaScript: autosave, and the share panel. A SPA would have added a build pipeline and a second place to enforce permissions for no reviewer-visible benefit.

## Data model

- `Document(title, content, owner, timestamps)`
- `DocumentShare(document, user, role[view|edit])` with a unique `(document, user)` constraint

Role resolution lives in one method, `Document.role_for(user)` → `owner | edit | view | None`. Every view goes through it, so there is a single access-control path.

## Access rules

| Action | Owner | Edit | View | Other |
|---|---|---|---|---|
| Open | ✅ | ✅ | ✅ | 404 |
| Edit / rename | ✅ | ✅ | ❌ 403 | 404 |
| Share / unshare / delete | ✅ | ❌ 403 | ❌ 403 | 404 |

Users without access get **404 rather than 403** so document ids can't be probed. The editor is also rendered read-only for viewers, but that is only UX. The server is the authority.

## Persistence and formatting

Content is stored as **HTML**. It round-trips Quill's formatting without a custom serialiser, and is what imported files are converted into. Quill's `getSemanticHTML()` is used on save because Quill 2's raw DOM represents bullets as `<ol data-list="bullet">`, which is awkward to store and re-import.

## Security

All content is passed through a **bleach allow-list** (`docs/sanitize.py`) on every save and import, restricted to the tags the toolbar can emit. This prevents stored XSS, which matters because one user's content is rendered in another user's browser. Uploads are checked for extension, size (2 MB) and emptiness. Text is HTML-escaped during `.txt` import.

## File upload design

Upload creates a **new document** from the file, which is the most predictable behaviour. Supported: `.txt` (paragraphs), `.md` (via `markdown`), `.docx` (via `python-docx`: headings, bold/italic/underline, bullet and numbered lists). The limit is stated in the UI and README. Unsupported and corrupt files fail with a message and nothing is created.

## Known trade-offs

- **Last write wins.** Two people editing at once can overwrite each other's autosaves. Fixing this properly means operational transforms or CRDTs (e.g. Yjs), which was out of scope for the timebox. It's the first thing I'd call out as a next step.
- **Sharing by username**, not email invite, because users are seeded. Auth is Django's built-in login, with no sign-up flow.
- **Ephemeral disk on free hosting** resets SQLite on redeploy. Documented, with a one-variable Postgres escape hatch.
- **Quill from a CDN** keeps the build trivial but needs network access in the browser.

## Testing

18 tests (`python manage.py test`) cover the risky logic rather than the happy path only: permission matrix, share/unshare/role-change, validation errors, HTML sanitisation, formatting round trip, and every upload type including rejected, empty, corrupt and oversized files. Not covered: browser-level behaviour of the editor (autosave timing, toolbar), which I'd add with Playwright next.
