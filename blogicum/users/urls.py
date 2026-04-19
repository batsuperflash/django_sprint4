from django.contrib.auth import views as auth_views
from django.urls import include, path, reverse_lazy

from . import views


urlpatterns = [
    path(
        "password_change/",
        auth_views.PasswordChangeView.as_view(
            success_url=reverse_lazy("password_change_done")
        ),
        name="password_change",
    ),
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            success_url=reverse_lazy("password_reset_done")
        ),
        name="password_reset",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            success_url=reverse_lazy("password_reset_complete")
        ),
        name="password_reset_confirm",
    ),
    path(
        "registration/",
        views.UserCreateView.as_view(),
        name='registration',
    ),
    path("", include("django.contrib.auth.urls")),
    path(
        "profile/edit/",
        views.UserProfileUpdateView.as_view(),
        name="edit_profile",
    ),
]