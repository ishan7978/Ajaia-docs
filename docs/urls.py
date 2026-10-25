from django.urls import path

from . import views

urlpatterns = [
    path("", views.doc_list, name="doc_list"),
    path("docs/new/", views.doc_create, name="doc_create"),
    path("docs/upload/", views.doc_upload, name="doc_upload"),
    path("docs/<int:pk>/", views.doc_detail, name="doc_detail"),
    path("docs/<int:pk>/save/", views.doc_save, name="doc_save"),
    path("docs/<int:pk>/delete/", views.doc_delete, name="doc_delete"),
    path("docs/<int:pk>/share/", views.share_add, name="share_add"),
    path("docs/<int:pk>/unshare/", views.share_remove, name="share_remove"),
]
