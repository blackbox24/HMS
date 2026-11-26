from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver


@receiver(user_logged_in)
def bind_session_to_user(sender, request, user, **kwargs):
    """Record this session as the user's single active session."""
    session_key = request.session.session_key
    if session_key and user.active_session_key != session_key:
        user.active_session_key = session_key
        user.save(update_fields=["active_session_key"])
