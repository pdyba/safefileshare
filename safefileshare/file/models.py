from django.db import models

from safefileshare.users.models import User


class SafeSecret(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    secret_link = models.CharField(max_length=255)
    password_hash = models.CharField(max_length=255)
    downloads = models.IntegerField(default=0)
    upload_date = models.DateTimeField(auto_now_add=True)
    file = models.ImageField(upload_to='user_files')
