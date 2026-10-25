import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotAllowed, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .importers import SUPPORTED_EXTENSIONS, ImportError_, import_upload
from .models import Document, DocumentShare
from .sanitize import clean_html

User = get_user_model()

MAX_TITLE = 200
MAX_CONTENT = 1_000_000  # characters of HTML


def _json_body(request):
    try:
        return json.loads(request.body or b"{}")
    except (ValueError, UnicodeDecodeError):
        return None


def _error(message, status=400):
    return JsonResponse({"ok": False, "error": message}, status=status)


def _get_visible_or_404(request, pk):
    """404 (not 403) for documents the user cannot see, so ids don't leak."""
    doc = get_object_or_404(Document, pk=pk)
    role = doc.role_for(request.user)
    if role is None:
        from django.http import Http404

        raise Http404("No such document")
    return doc, role


@login_required
def doc_list(request):
    owned = Document.objects.filter(owner=request.user)
    shared = (
        Document.objects.filter(shares__user=request.user)
        .select_related("owner")
        .distinct()
    )
    share_roles = dict(
        DocumentShare.objects.filter(user=request.user).values_list("document_id", "role")
    )
    for doc in shared:
        doc.my_role = share_roles.get(doc.id, "view")
    return render(
        request,
        "docs/list.html",
        {
            "owned": owned,
            "shared": shared,
            "supported": ", ".join(SUPPORTED_EXTENSIONS),
            "accept": ",".join(SUPPORTED_EXTENSIONS),
        },
    )


@login_required
@require_POST
def doc_create(request):
    doc = Document.objects.create(owner=request.user)
    return redirect("doc_detail", pk=doc.pk)


@login_required
def doc_detail(request, pk):
    doc, role = _get_visible_or_404(request, pk)
    shares = doc.shares.select_related("user") if role == "owner" else []
    return render(
        request,
        "docs/editor.html",
        {
            "doc": doc,
            "role": role,
            "can_edit": role in ("owner", "edit"),
            "is_owner": role == "owner",
            "shares": shares,
        },
    )


@login_required
@require_POST
def doc_save(request, pk):
    """Autosave endpoint: accepts JSON {title?, content?}."""
    doc, role = _get_visible_or_404(request, pk)
    if role not in ("owner", "edit"):
        return _error("You have view-only access to this document.", 403)
    body = _json_body(request)
    if not isinstance(body, dict):
        return _error("Invalid request body.")

    update_fields = ["updated_at"]
    if "title" in body:
        title = str(body["title"]).strip()
        if not title:
            return _error("Title cannot be empty.")
        if len(title) > MAX_TITLE:
            return _error(f"Title is too long (max {MAX_TITLE} characters).")
        doc.title = title
        update_fields.append("title")
    if "content" in body:
        content = body["content"]
        if not isinstance(content, str):
            return _error("Content must be a string.")
        if len(content) > MAX_CONTENT:
            return _error("Document is too large to save.")
        doc.content = clean_html(content)
        update_fields.append("content")
    doc.save(update_fields=update_fields)
    return JsonResponse({"ok": True, "title": doc.title, "updated_at": doc.updated_at.isoformat()})


@login_required
@require_POST
def doc_delete(request, pk):
    doc, role = _get_visible_or_404(request, pk)
    if role != "owner":
        return _error("Only the owner can delete a document.", 403)
    doc.delete()
    messages.success(request, "Document deleted.")
    return redirect("doc_list")


@login_required
@require_POST
def share_add(request, pk):
    doc, role = _get_visible_or_404(request, pk)
    if role != "owner":
        return _error("Only the owner can share this document.", 403)
    body = _json_body(request)
    if not isinstance(body, dict):
        return _error("Invalid request body.")

    username = str(body.get("username", "")).strip()
    share_role = body.get("role", DocumentShare.VIEW)
    if share_role not in (DocumentShare.VIEW, DocumentShare.EDIT):
        return _error("Role must be 'view' or 'edit'.")
    if not username:
        return _error("Enter a username to share with.")
    target = User.objects.filter(username__iexact=username).first()
    if target is None:
        return _error(f"No user named '{username}'.", 404)
    if target.id == doc.owner_id:
        return _error("You already own this document.")

    share, created = DocumentShare.objects.update_or_create(
        document=doc, user=target, defaults={"role": share_role}
    )
    return JsonResponse(
        {"ok": True, "username": target.username, "role": share.role, "created": created}
    )


@login_required
@require_POST
def share_remove(request, pk):
    doc, role = _get_visible_or_404(request, pk)
    if role != "owner":
        return _error("Only the owner can change sharing.", 403)
    body = _json_body(request)
    if not isinstance(body, dict):
        return _error("Invalid request body.")
    deleted, _ = DocumentShare.objects.filter(
        document=doc, user__username__iexact=str(body.get("username", ""))
    ).delete()
    if not deleted:
        return _error("That user does not have access.", 404)
    return JsonResponse({"ok": True})


@login_required
def doc_upload(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    try:
        title, html = import_upload(request.FILES.get("file"), settings.MAX_UPLOAD_BYTES)
    except ImportError_ as exc:
        messages.error(request, str(exc))
        return redirect("doc_list")
    doc = Document.objects.create(owner=request.user, title=title, content=html)
    messages.success(request, f"Imported '{doc.title}' as a new document.")
    return redirect("doc_detail", pk=doc.pk)
