from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager

class Users(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    manager = models.BooleanField(default=False)

    def __str__(self):
        return self.email


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()