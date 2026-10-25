from django.conf import settings
from django.db import models
from django.db.models import Q


class DocumentQuerySet(models.QuerySet):
    def visible_to(self, user):
        """Documents the user owns or that were shared with them."""
        return self.filter(Q(owner=user) | Q(shares__user=user)).distinct()


class Document(models.Model):
    title = models.CharField(max_length=200, default="Untitled document")
    # Sanitised HTML produced by the editor. HTML is the storage format because
    # it round-trips formatting (bold/italic/underline/headings/lists) without
    # an extra serialisation layer.
    content = models.TextField(blank=True, default="")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owned_documents"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = DocumentQuerySet.as_manager()

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title

    def role_for(self, user):
        """Return 'owner', 'edit', 'view', or None for the given user."""
        if not user.is_authenticated:
            return None
        if self.owner_id == user.id:
            return "owner"
        share = self.shares.filter(user=user).first()
        return share.role if share else None

    def can_view(self, user):
        return self.role_for(user) is not None

    def can_edit(self, user):
        return self.role_for(user) in ("owner", "edit")


class DocumentShare(models.Model):
    VIEW = "view"
    EDIT = "edit"
    ROLE_CHOICES = [(VIEW, "Can view"), (EDIT, "Can edit")]

    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="shares")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="document_shares"
    )
    role = models.CharField(max_length=4, choices=ROLE_CHOICES, default=VIEW)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["document", "user"], name="unique_share_per_user")
        ]

    def __str__(self):
        return f"{self.document} -> {self.user} ({self.role})"
