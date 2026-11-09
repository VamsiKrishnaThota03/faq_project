from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import FAQ, SUPPORTED_LANGUAGES


def faq_cache_key(lang):
    return f"faqs_{lang}"


@receiver(post_save, sender=FAQ)
@receiver(post_delete, sender=FAQ)
def invalidate_faq_cache(**kwargs):
    """Drop every cached language list when an FAQ is created, edited or deleted."""
    cache.delete_many([faq_cache_key(lang) for lang in SUPPORTED_LANGUAGES])
