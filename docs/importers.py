"""Turn an uploaded file into (title, sanitised HTML).

Supported types are deliberately limited to .txt, .md and .docx and this list is
surfaced in the UI and README. Everything else is rejected with a clear error.
"""

import html
import io
import os

import markdown as md

from .sanitize import clean_html

SUPPORTED_EXTENSIONS = (".txt", ".md", ".docx")


class ImportError_(Exception):
    """Raised with a user-presentable message when a file cannot be imported."""


def _title_from_filename(name: str) -> str:
    base = os.path.splitext(os.path.basename(name))[0].strip()
    return (base or "Imported document")[:200]


def _from_txt(data: bytes) -> str:
    text = data.decode("utf-8", errors="replace")
    paragraphs = [p for p in text.replace("\r\n", "\n").split("\n\n")]
    parts = []
    for p in paragraphs:
        if p.strip():
            parts.append("<p>" + html.escape(p.strip()).replace("\n", "<br>") + "</p>")
    return "".join(parts)


def _from_md(data: bytes) -> str:
    return md.markdown(data.decode("utf-8", errors="replace"), extensions=["sane_lists"])


def _from_docx(data: bytes) -> str:
    import docx  # imported lazily so .txt/.md imports never need it

    try:
        document = docx.Document(io.BytesIO(data))
    except Exception as exc:
        raise ImportError_("That .docx file could not be read. Is it a valid Word document?") from exc

    out = []
    open_list = None  # "ul" / "ol" while inside a list

    def close_list():
        nonlocal open_list
        if open_list:
            out.append(f"</{open_list}>")
            open_list = None

    for para in document.paragraphs:
        style = (para.style.name or "").lower() if para.style is not None else ""
        runs = []
        for run in para.runs:
            text = html.escape(run.text)
            if not text:
                continue
            if run.bold:
                text = f"<strong>{text}</strong>"
            if run.italic:
                text = f"<em>{text}</em>"
            if run.underline:
                text = f"<u>{text}</u>"
            runs.append(text)
        inner = "".join(runs)
        if not inner.strip():
            close_list()
            continue

        if style.startswith("list bullet") or style.startswith("list number"):
            kind = "ul" if style.startswith("list bullet") else "ol"
            if open_list != kind:
                close_list()
                out.append(f"<{kind}>")
                open_list = kind
            out.append(f"<li>{inner}</li>")
            continue

        close_list()
        if style == "title":
            out.append(f"<h1>{inner}</h1>")
        elif style.startswith("heading"):
            level = "".join(c for c in style if c.isdigit()) or "1"
            level = min(max(int(level), 1), 3)
            out.append(f"<h{level}>{inner}</h{level}>")
        else:
            out.append(f"<p>{inner}</p>")
    close_list()
    return "".join(out)


def import_upload(uploaded_file, max_bytes: int):
    """Validate an UploadedFile and return (title, html). Raises ImportError_."""
    if uploaded_file is None:
        raise ImportError_("Choose a file to upload.")
    name = uploaded_file.name or ""
    ext = os.path.splitext(name)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ImportError_(
            f"Unsupported file type '{ext or 'unknown'}'. Supported: "
            + ", ".join(SUPPORTED_EXTENSIONS)
            + "."
        )
    if uploaded_file.size > max_bytes:
        raise ImportError_(f"File is too large (limit {max_bytes // (1024 * 1024)} MB).")
    data = uploaded_file.read()
    if not data:
        raise ImportError_("The uploaded file is empty.")

    if ext == ".txt":
        body = _from_txt(data)
    elif ext == ".md":
        body = _from_md(data)
    else:
        body = _from_docx(data)
    return _title_from_filename(name), clean_html(body)
