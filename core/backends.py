from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

User = get_user_model()


class EmailOrUsernameBackend(ModelBackend):
    """Authenticate with either username or email in the 'username' field."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get("email") or kwargs.get(User.USERNAME_FIELD)
        if username is None or password is None:
            return None

        user = (
            User.objects.filter(Q(username__iexact=username) | Q(email__iexact=username))
            .distinct()
            .first()
        )
        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
