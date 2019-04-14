from django.apps import AppConfig


class FileAppConfig(AppConfig):

    name = "safefileshare.file"
    verbose_name = "File"

    def ready(self):
        try:
            import users.signals  # noqa F401
        except ImportError:
            pass
