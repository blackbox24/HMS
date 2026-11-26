import logging
import time

from django.contrib.auth import logout
from django.shortcuts import redirect

access_logger = logging.getLogger("hms.access")


class SingleSessionMiddleware:
    """Enforce one active session per user.

    On login we store the session key on the user (see core/signals.py).
    Any request whose session key no longer matches is logged out, so a
    login on a second terminal kicks the first one off.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if (
            user is not None
            and user.is_authenticated
            and request.session.get("auth_stopped") is not True
        ):
            session_key = request.session.session_key
            if session_key and user.active_session_key and session_key != user.active_session_key:
                logout(request)
                return redirect("login")
        return self.get_response(request)


class AccessLogMiddleware:
    """Writes one line per request to logs/access.log via the 'hms.access' logger."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.monotonic()
        response = self.get_response(request)
        elapsed_ms = (time.monotonic() - start) * 1000
        user = request.user.username if request.user.is_authenticated else "-"
        access_logger.info(
            '%s "%s %s" %s %.1fms',
            user,
            request.method,
            request.get_full_path(),
            response.status_code,
            elapsed_ms,
        )
        return response
