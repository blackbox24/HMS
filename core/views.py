import logging
import secrets
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View

from patients.models import Patient

from .audit import audit
from .models import AuditLog, PasswordResetRequest
from .permissions import is_admin

logger = logging.getLogger(__name__)
User = get_user_model()

DUPLICATE_REQUEST_WINDOW = timedelta(minutes=5)


@login_required
def dashboard(request):
    ctx = {
        "total_patients": Patient.objects.count(),
        "recent_patients": Patient.objects.order_by("-registered_at")[:5],
        "recent_activity": AuditLog.objects.select_related("user")[:10],
    }
    return render(request, "core/dashboard.html", ctx)


class HMSPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = "registration/password_change_form.html"
    success_url = reverse_lazy("password_change_done")

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.user.must_change_password:
            self.request.user.must_change_password = False
            self.request.user.save(update_fields=["must_change_password"])
        return response


class PasswordResetRequestView(View):
    """'Forgot password' — staff submit their username; an admin later
    issues a temporary password from the reset-requests page."""

    template_name = "registration/password_reset_request.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get("username", "").strip()
        # Always show the same message — don't reveal whether the account exists.
        generic_msg = (
            "If that account exists, a reset request has been "
            "submitted. Please see the administrator."
        )

        user = User.objects.filter(username__iexact=username).first()
        if user and user.is_active:
            recent = PasswordResetRequest.objects.filter(
                user=user,
                requested_at__gte=timezone.now() - DUPLICATE_REQUEST_WINDOW,
            ).exists()
            if not recent:
                PasswordResetRequest.objects.create(user=user)
                logger.info(
                    "Password reset requested for %s by ip=%s",
                    username,
                    request.META.get("REMOTE_ADDR"),
                )
        messages.info(request, generic_msg)
        return redirect("password_reset_request")


class PasswordResetRequestsAdminView(LoginRequiredMixin, View):
    """Admin page: pending reset requests + issue temporary passwords."""

    template_name = "registration/password_reset_requests.html"

    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_staff or is_admin(request.user)):
            from django.core.exceptions import PermissionDenied

            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(
            request,
            self.template_name,
            {
                "pending": PasswordResetRequest.objects.filter(
                    status=PasswordResetRequest.Status.PENDING
                ).select_related("user"),
                "handled": PasswordResetRequest.objects.exclude(
                    status=PasswordResetRequest.Status.PENDING
                ).select_related("user", "handled_by")[:20],
            },
        )

    def post(self, request, pk=None):
        if pk is None:
            return redirect("password_reset_requests")
        reset_req = PasswordResetRequest.objects.select_related("user").get(
            pk=pk, status=PasswordResetRequest.Status.PENDING
        )

        temp_password = secrets.token_urlsafe(9)
        user = reset_req.user
        user.set_password(temp_password)
        user.must_change_password = True
        user.save(update_fields=["password", "must_change_password"])

        reset_req.status = PasswordResetRequest.Status.COMPLETED
        reset_req.handled_by = request.user
        reset_req.handled_at = timezone.now()
        reset_req.save(update_fields=["status", "handled_by", "handled_at"])

        audit(request, "UPDATE", user, changes={"password_reset": "temporary password issued"})
        logger.warning("Admin %s issued temp password for %s", request.user.username, user.username)
        # Shown once — the admin writes it down / tells the staff member.
        messages.success(
            request,
            f"Temporary password for {user.username}: "
            f"{temp_password}  (shown once — user must "
            f"change it at next login)",
        )
        return redirect("password_reset_requests")
