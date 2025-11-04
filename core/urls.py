from django.urls import path
from .views import index, create_blog_entry, all_blog_entries, blog_entry_details, blog_entry_delete, edit_blog_entry

urlpatterns = [
    path("", index, name="home"),
    path("entries/create", create_blog_entry, name="create_entry_blog"),
    path("entries", all_blog_entries, name="all_blog_entries"),
    path("entries/<int:blog_id>", blog_entry_details, name="blog_entry_details"),
    path("entries/<int:blog_id>/delete", blog_entry_delete, name="blog_entry_delete"),
    path("entries/<int:blog_id>/edit", edit_blog_entry, name="edit_blog_entry")
]
