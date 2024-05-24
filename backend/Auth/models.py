from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from Staff.models import Staff
from django.utils.crypto import get_random_string

class UserManager(BaseUserManager):

    use_in_migration = True

    def create_user(self, first_name,last_name,email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is Required')
        if not first_name:
            raise ValueError('First name is Required')
        if not last_name:
            raise ValueError('last name is Required')
        
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.first_name = first_name
        user.last_name = last_name
        user.set_password(password)
        user.is_staff = True
        user.save()
        return user

    def create_superuser(self,first_name, last_name,email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff = True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser = True')

        user =  self.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            is_staff=True,
            is_superuser=True,
            )
        user.save()
        return user



class UserData(AbstractUser):
    staff_id = models.ForeignKey(Staff,on_delete=models.CASCADE,null=True,blank=True)
    username = None
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=255)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name','last_name']

    def generate_verification_token(self):
        token = get_random_string(length=32)
        self.verification_token = token
        self.save()
        return token

    def __str__(self):
        return f"{self.first_name} {self.last_name}"