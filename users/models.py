from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    photo = models.ImageField(upload_to='users/', blank=True, null=True, verbose_name='Photo')
    phone = models.CharField(blank=True, null=True, verbose_name='Phone')
    api_key = models.CharField(blank=True, null=True, verbose_name='takealot ApiKey', db_index=True)
    sellers_id = models.CharField(null=True, db_index=True)
    status = models.BooleanField(default=False, verbose_name='user status', db_index=True)
    company_name = models.CharField(blank=True, null=True, verbose_name='company name', db_index=True)
    street = models.CharField(blank=True, null=True, verbose_name='company street', db_index=True)
    city = models.CharField(blank=True, null=True, verbose_name='company city', db_index=True)
    postal_code = models.CharField(blank=True, null=True, verbose_name='company postal_code', db_index=True)
    email_verify = models.BooleanField(default=False, db_index=True)
    invoice = models.IntegerField(db_index=True, default=20)
    autoprice = models.IntegerField(default=20, db_index=True)

    def __str__(self):
        return f'User: #{self.username}'
