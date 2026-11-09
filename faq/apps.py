from django.apps import AppConfig


class FAQConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'faq'
    verbose_name = 'FAQs'

    def ready(self):
        from . import signals  # noqa: F401  (registers cache invalidation)
