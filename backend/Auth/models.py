from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.crypto import get_random_string
from staff.models import Staff

class UserData(AbstractUser):
    staff_id = models.ForeignKey(Staff, on_delete=models.CASCADE, blank=False, null=False)
    phone_number = models.CharField(max_length=20)
    is_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=True)
    verification_token = models.CharField(max_length=100, blank=True, null=True)

    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    def generate_verification_token(self):
        token = get_random_string(length=32)
        self.verification_token = token
        self.save()
        return token

    def __Str__(self):
        return self.username
    
