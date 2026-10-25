# AI-native workflow note

> **Ishan: read and edit this before submitting.** The sections marked **[EDIT]** can only be true if *you* did them. Delete or rewrite anything that isn't accurate. Reviewers are checking whether this is honest and specific.

## Tools used

- **Claude** (chat with file/shell tools): generated the initial project scaffold, models, views, importers, templates, tests and first drafts of the documentation.
- **[EDIT]** Any other tools you used (Cursor, Copilot, ChatGPT, etc.), or delete this line.

## Where AI materially sped things up

- Scaffolding the Django app, models and endpoints in one pass instead of by hand.
- The `.docx` importer (mapping Word styles and runs to HTML) and the test suite, including edge cases like corrupt, empty and oversized uploads.
- Drafting README, architecture note and the demo script.

## Design decisions made while using AI

These were deliberate choices in the generated code that I kept or steered toward:

- **404 instead of 403** for documents a user can't see, so ids can't be probed.
- **Sanitise all HTML server-side** (bleach allow-list) instead of trusting the editor, since content is shown to other users.
- **`getSemanticHTML()`** rather than the editor's raw DOM, because Quill 2's raw list markup is non-standard.
- **One access-control method** (`Document.role_for`) used by every view, rather than ad-hoc checks per endpoint.
- Server-rendered Django pages instead of a SPA, to fit the timebox and keep setup to `pip install`.

## What I changed or rejected

- **[EDIT]** List concrete things you changed after reading the generated code (e.g. renamed something, changed styling, adjusted a message, removed a feature). If you changed nothing, say so honestly and describe what you reviewed instead.
- **[EDIT]** Anything you asked the AI to redo or that you decided not to build (e.g. real-time collaboration, export).

## How correctness was verified

- Automated: 18 tests pass (`python manage.py test`), covering the permission matrix, sharing, validation, sanitisation, formatting round trip and all upload paths.
- Static: `python manage.py check` is clean, and `collectstatic` works in production mode.
- Server smoke test: login page returns 200 and anonymous access to the home page redirects to login.
- **[EDIT]** Manual browser verification you actually did, for example: formatting each toolbar option and refreshing; logging in as bob and carol in separate sessions and confirming edit vs view-only; importing one file of each type; checking the deployed URL. **Only list what you did.**
- **Known gap:** the Quill editor's client-side behaviour (toolbar, autosave timing) is not covered by automated browser tests; it needs manual checking before you submit.
