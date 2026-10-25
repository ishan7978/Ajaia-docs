"""HTML sanitisation for editor content.

Content comes from a browser editor and from imported files, then is rendered
back into other users' browsers, so it is always cleaned server-side with an
allow-list that matches exactly what the toolbar can produce.
"""

import bleach

ALLOWED_TAGS = [
    "p", "br", "strong", "em", "u", "s", "h1", "h2", "h3",
    "ul", "ol", "li", "blockquote", "a", "span",
]
ALLOWED_ATTRS = {"a": ["href", "title"], "li": ["class"], "ol": ["class"], "ul": ["class"]}
ALLOWED_PROTOCOLS = ["http", "https", "mailto"]


def clean_html(html: str) -> str:
    return bleach.clean(
        html or "",
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRS,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )
