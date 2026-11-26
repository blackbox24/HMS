from django.contrib.auth.views import PasswordChangeDoneView
from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("password-change/", views.HMSPasswordChangeView.as_view(), name="password_change"),
    path(
        "password-change/done/",
        PasswordChangeDoneView.as_view(template_name="registration/password_change_done.html"),
        name="password_change_done",
    ),
    path(
        "password-reset/", views.PasswordResetRequestView.as_view(), name="password_reset_request"
    ),
    path(
        "password-reset-requests/",
        views.PasswordResetRequestsAdminView.as_view(),
        name="password_reset_requests",
    ),
    path(
        "password-reset-requests/<int:pk>/issue/",
        views.PasswordResetRequestsAdminView.as_view(),
        name="password_reset_issue",
    ),
]
