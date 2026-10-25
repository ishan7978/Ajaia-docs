# Walkthrough video script (target 4 min; limit is 3–5)

Record with Loom or YouTube (unlisted). Have two browser sessions ready (normal + private window): alice in one, bob in the other. Pre-create a small `.docx` and `.md` file to import.

**0:00 – Intro (20s)**
"This is a lightweight collaborative editor I built for the Ajaia assignment: Django, SQLite, Quill editor. I'll show the main flow, then what I cut and why."

**0:20 – Create and edit (60s)**
Log in as alice → New document → rename it → use bold, italic, underline, a heading, a bulleted and a numbered list. Point out the "All changes saved" indicator. Refresh the page to show it persists with formatting.

**1:20 – File upload (40s)**
Home page → point to the supported-types text → import the .docx → show it opens as a new editable doc with headings/bold preserved. Briefly try an unsupported file to show the error.

**2:00 – Sharing (70s)**
Open a document → share with bob as "Can edit". Switch to the bob window: show it under "Shared with me" with the badge, edit it. Share another with carol as view-only → show read-only editor and locked title. Back as alice, remove access, refresh as carol: it's gone.

**3:10 – Decisions and cuts (40s)**
"Permissions are enforced on the server through one method, and unauthorised users get a 404. HTML is sanitised on save and import. I deliberately skipped real-time collaboration, comments, version history and export. Last save wins today, and that's the first thing I'd fix, with Yjs or version history."

**3:50 – AI usage (20s)**
Say honestly which tools you used, what they sped up, and **one concrete thing you changed or caught**. Mention the 18 automated tests.

**4:10 – Close (10s)**
"Live link and test accounts are in the README. Thanks."

Tip: if you run long, shorten the formatting demo, not the sharing demo. Sharing is what they'll test hardest.
