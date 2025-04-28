from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    phone    = models.CharField("電話號碼", max_length=20, blank=True)
    birthday = models.DateField("生日", null=True, blank=True)
    # … any other extra fields
