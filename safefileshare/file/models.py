import uuid

from django.db import models

from safefileshare.users.models import User


class SafeSecret(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    secret_link = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    password_hash = models.CharField(max_length=255)
    downloads = models.IntegerField(default=0)
    upload_date = models.DateTimeField(auto_now_add=True)
    link = models.CharField(max_length=255, null=True)
    file = models.CharField(max_length=255, null=True)


class SecretCounter(models.Model):
    date = models.DateField()
    downloads = models.IntegerField(default=0)
    links = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.date} downloads:{self.downloads} links:{self.links}"
