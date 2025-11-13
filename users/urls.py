from django.urls import path
from .views import registration, login, activate, profile, toggle_save_post, update_profile, logout

urlpatterns = [
    path("registration/", registration, name="registration"),
    path("login/", login, name="login"),
    path("logout/", logout, name="logout"),
    path("activate/<uid>/<token>/", activate, name="activate"),
    path("profile/", profile, name="profile"),
    path("profile/<username>/", profile, name="profile"),
    path("entries/<int:blog_id>/toggle_save/", toggle_save_post, name="toggle_save_post"),
    path("profile/user/update/", update_profile, name="update_profile")
]
