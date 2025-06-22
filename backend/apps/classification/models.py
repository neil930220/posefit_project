from django.db import models

# Create your models here.

import os
from django.db import models
from django.conf import settings

def user_directory_path(instance, filename):
    # if user is logged in use their username, otherwise “guest”
    username = instance.user.username if instance.user else 'guest'
    # you can further nest by date, etc.
    return f'uploads/{username}/{filename}'

class Photo(models.Model):
    user        = models.ForeignKey(
                    settings.AUTH_USER_MODEL,
                    null=True, blank=True,
                    on_delete=models.SET_NULL
               )
    image     = models.ImageField(upload_to=user_directory_path)
    uploaded  = models.DateTimeField(auto_now_add=True)


