from django.contrib import admin

from safefileshare.file.forms import SetPasswordForm
from safefileshare.file.models import SafeSecret


@admin.register(SafeSecret)
class FileAdmin(admin.ModelAdmin):
    form = SetPasswordForm
    list_display = ["user", "secret_link", "downloads", "link", "file"]

