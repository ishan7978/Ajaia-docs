from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from docs.models import Document, DocumentShare

DEMO_PASSWORD = "demo1234"
DEMO_USERS = ["alice", "bob", "carol"]

WELCOME_HTML = (
    "<h1>Welcome to Ajaia Docs</h1>"
    "<p>This document is owned by <strong>alice</strong> and shared with "
    "<em>bob</em> (can edit) and <u>carol</u> (view only).</p>"
    "<h2>Try this</h2>"
    "<ul><li>Format text with the toolbar</li><li>Rename the document at the top</li>"
    "<li>Log in as bob and edit it; log in as carol and notice it is read-only</li></ul>"
    "<ol><li>Upload a .txt, .md or .docx from the home page</li>"
    "<li>Share a document with another user</li></ol>"
)


class Command(BaseCommand):
    help = "Create demo users (alice, bob, carol) and a sample shared document. Idempotent."

    def handle(self, *args, **options):
        User = get_user_model()
        users = {}
        for name in DEMO_USERS:
            user, created = User.objects.get_or_create(username=name)
            if created:
                user.set_password(DEMO_PASSWORD)
                user.save()
            users[name] = user

        doc, created = Document.objects.get_or_create(
            owner=users["alice"],
            title="Welcome to Ajaia Docs",
            defaults={"content": WELCOME_HTML},
        )
        DocumentShare.objects.get_or_create(
            document=doc, user=users["bob"], defaults={"role": DocumentShare.EDIT}
        )
        DocumentShare.objects.get_or_create(
            document=doc, user=users["carol"], defaults={"role": DocumentShare.VIEW}
        )
        Document.objects.get_or_create(
            owner=users["bob"],
            title="Bob's private notes",
            defaults={"content": "<p>Only bob can see this until he shares it.</p>"},
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded users {', '.join(DEMO_USERS)} (password: {DEMO_PASSWORD})"
            )
        )
