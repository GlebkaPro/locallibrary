from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
  middle_name = models.CharField(max_length=100, blank=True, null=True)
  avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
  date_birth = models.DateField('Дата рождения', null=True, blank=True)
  privacy_policy_agreement = models.BooleanField(default=False)
  phone_number = models.CharField(max_length=100, blank=True, null=True)
  document = models.FileField(upload_to='documents/', null=True, blank=True)

  record_status = (
    ('а', 'активирована'),
    ('н', 'не активирована'),
  )

  record_status = models.CharField(
    max_length=1, choices=record_status, blank=True, default='н', verbose_name='Статус записи-')
  def __str__(self):
    return '{0} {1} {2}'.format( self.last_name, self.first_name, self.middle_name)

  def get_full_name(self):
    full_name = f"{self.last_name} {self.first_name}"
    if self.middle_name:
      full_name += f" {self.middle_name}"
    return full_name
