from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
  middle_name = models.CharField(max_length=100, blank=True, null=True)
  avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
  date_birth = models.DateField('Дата рождения', null=True, blank=True)
  privacy_policy_agreement = models.BooleanField(default=False)
