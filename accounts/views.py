"""Accounts views — auth pages UI (hms-auth-ui spec).

Business logic (axes, single session, must_change_password, audit) already
exists; these views only render the new templates and satisfy the HTMX
contracts described in hms-auth-ui/DESIGN_SPEC.md.
"""
import logging
import secrets
from datetime import timedelta

from axes.models import AccessAttempt
from axes.utils import reset as axes_reset
from django.conf import settings as djsettings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth import login as auth_login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone

from core.audit import audit

from .forms import LoginForm, ResetRequestForm
from .models import PasswordResetRequest

logger = logging.getLogger(__name__)
User = get_user_model()

DUPLICATE_WINDOW = timedelta(minutes=5)
# Unambiguous alphabet (no 0/O, 1/l/I) grouped 3-3-3, e.g. "K7M-X2Q-9PD"
TEMP_PW_ALPHABET = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789'


def _is_htmx(request):
    return request.headers.get('HX-Request') == 'true'


# ---------------------------------------------------------------- login ----

def _attempts_left(username):
    try:
        attempt = (AccessAttempt.objects
                   .filter(username__iexact=username)
                   .order_by('-attempt_time')
                   .first())
        if attempt:
            return max(0, djsettings.AXES_FAILURE_LIMIT
                       - attempt.failures_since_start)
    except Exception:
        pass
    return djsettings.AXES_FAILURE_LIMIT


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    next_url = (request.POST.get('next') or request.GET.get('next')
                or reverse_lazy('dashboard'))

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            if _is_htmx(request):
                response = HttpResponse('')
                response['HX-Redirect'] = str(next_url)
                return response
            return redirect(next_url)

        form = LoginForm(data={'username': username, 'password': password})
        form.is_valid()
        form.add_error(None, 'invalid')  # drives the alert + invalid styling
        ctx = {
            'form': form,
            'attempts_left': _attempts_left(username),
            'next': next_url,
        }
        if _is_htmx(request):
            return render(request, 'accounts/partials/_login_form.html', ctx)
        return render(request, 'accounts/login.html', ctx)

    form = LoginForm()
    return render(request, 'accounts/login.html', {
        'form': form,
        'next': request.GET.get('next', ''),
    })


# ------------------------------------------------------- password reset ----

def password_reset_request(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()

        user = User.objects.filter(username__iexact=username).first()
        if user and user.is_active:
            recent = PasswordResetRequest.objects.filter(
                user=user,
                created_at__gte=timezone.now() - DUPLICATE_WINDOW,
            ).exists()
            if not recent:
                req = PasswordResetRequest.objects.create(user=user)
                logger.info('Password reset requested for %s', username)
                return redirect(
                    f"{reverse_lazy('accounts:password_reset_requested')}"
                    f"?ref={req.pk}&u={user.username}")
            else:
                # Duplicate — show confirmation anyway (no info leak).
                return redirect(
                    f"{reverse_lazy('accounts:password_reset_requested')}"
                    f"?u={user.username}")

        # Unknown username: same confirmation, no row created.
        return redirect(
            f"{reverse_lazy('accounts:password_reset_requested')}?u={username}")

    return render(request, 'accounts/password_reset_request.html',
                  {'form': ResetRequestForm()})


def password_reset_requested(request):
    username = request.GET.get('u', '')
    reference = requested_at = None
    ref = request.GET.get('ref')
    if ref and ref.isdigit():
        req = (PasswordResetRequest.objects
               .filter(pk=int(ref)).select_related('user').first())
        if req:
            reference = req.reference
            requested_at = req.created_at
            username = req.user.username
    return render(request, 'accounts/password_reset_requested.html', {
        'username': username,
        'reference': reference,
        'requested_at': requested_at,
    })


# -------------------------------------------------------- password change --

class HMSPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'accounts/password_change_forced.html'
    success_url = reverse_lazy('dashboard')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['is_forced'] = self.request.user.must_change_password
        return ctx

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.user.must_change_password:
            self.request.user.must_change_password = False
            self.request.user.save(update_fields=['must_change_password'])
        return response


# --------------------------------------------------------- admin resets ----

def _can_issue_temp_password(user):
    return user.is_superuser or user.has_perm('accounts.issue_temp_password')


def _generate_temp_password():
    groups = [''.join(secrets.choice(TEMP_PW_ALPHABET) for _ in range(3))
              for _ in range(3)]
    return '-'.join(groups)


def _locked_accounts():
    """Latest axes AccessAttempt per username at/over the failure limit."""
    limit = djsettings.AXES_FAILURE_LIMIT
    latest = {}
    for attempt in (AccessAttempt.objects
                    .filter(failures_since_start__gte=limit)
                    .order_by('-attempt_time')):
        latest.setdefault(attempt.username, attempt)

    usernames = list(latest)
    users = {u.username: u for u in
             User.objects.filter(username__in=usernames)}
    rows = []
    for username, attempt in latest.items():
        user = users.get(username)
        rows.append({
            'username': username,
            'full_name': (user.get_full_name() if user else '') or username,
            'locked_at': attempt.attempt_time,
            'workstation': attempt.user_agent[:40] if attempt.user_agent else '',
            'ip_address': attempt.ip_address,
        })
    return rows


def password_resets(request):
    if not _can_issue_temp_password(request.user):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied

    tab = request.GET.get('tab', 'pending')
    today = timezone.localdate()
    base = PasswordResetRequest.objects.select_related('user', 'issued_by')

    if tab == 'issued':
        requests_qs = base.filter(status='issued',
                                  issued_at__date=today)
    elif tab == 'all':
        requests_qs = base.all()
    else:
        tab = 'pending'
        requests_qs = base.filter(status='pending')

    counts = {
        'pending': base.filter(status='pending').count(),
        'issued_today': base.filter(status='issued',
                                    issued_at__date=today).count(),
    }
    return render(request, 'accounts/admin/password_resets.html', {
        'tab': tab,
        'requests': requests_qs,
        'counts': counts,
        'locked_accounts': _locked_accounts(),
    })


def _render_reset_row(request, req, temp_password=None):
    return render(request, 'accounts/partials/_reset_row.html', {
        'req': req,
        'temp_password': temp_password,
    })


def issue_temp_password(request, pk):
    if not _can_issue_temp_password(request.user):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied

    req = PasswordResetRequest.objects.select_related('user').get(
        pk=pk, status=PasswordResetRequest.Status.PENDING)

    temp_password = _generate_temp_password()
    user = req.user
    user.set_password(temp_password)
    user.must_change_password = True
    user.save(update_fields=['password', 'must_change_password'])

    req.status = PasswordResetRequest.Status.ISSUED
    req.issued_by = request.user
    req.issued_at = timezone.now()
    req.save(update_fields=['status', 'issued_by', 'issued_at'])

    audit(request, 'UPDATE', user,
          changes={'password_reset': 'temporary password issued'})
    logger.warning('Admin %s issued temp password for %s',
                   request.user.username, user.username)

    if _is_htmx(request):
        return _render_reset_row(request, req, temp_password)
    messages.success(request, f'Temporary password for {user.username}: '
                               f'{temp_password} (shown once)')
    return redirect('accounts:password_resets')


def mark_handed_over(request, pk):
    if not _can_issue_temp_password(request.user):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied

    req = PasswordResetRequest.objects.get(pk=pk)
    if req.handed_over_at is None:
        req.handed_over_at = timezone.now()
        req.save(update_fields=['handed_over_at'])
    return _render_reset_row(request, req)


def _render_locked_row(request, acct, temp_password=None, resolved=False):
    return render(request, 'accounts/partials/_locked_row.html', {
        'acct': acct,
        'temp_password': temp_password,
        'resolved': resolved,
    })


def unlock_account(request, username):
    if not _can_issue_temp_password(request.user):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied

    removed = axes_reset(username=username)
    audit(request, 'UPDATE', None,
          changes={'axes_unlock': username})
    logger.warning('Admin %s unlocked axes account %s (%d attempts cleared)',
                   request.user.username, username, removed)

    temp_password = None
    user = User.objects.filter(username__iexact=username).first()
    if request.GET.get('issue_temp') == '1' and user:
        temp_password = _generate_temp_password()
        user.set_password(temp_password)
        user.must_change_password = True
        user.save(update_fields=['password', 'must_change_password'])
        PasswordResetRequest.objects.create(
            user=user, status=PasswordResetRequest.Status.ISSUED,
            issued_by=request.user, issued_at=timezone.now())
        audit(request, 'UPDATE', user,
              changes={'password_reset': 'temp password via unlock'})

    acct = {
        'username': username,
        'full_name': (user.get_full_name() if user else '') or username,
        'locked_at': None, 'workstation': '', 'ip_address': '',
    }
    if _is_htmx(request):
        return _render_locked_row(request, acct, temp_password, resolved=True)
    messages.success(request, f'Account {username} unlocked.')
    return redirect('accounts:password_resets')


def session_ended(request):
    return render(request, 'accounts/session_ended.html', {
        'username': request.session.pop('ended_username', ''),
    })
