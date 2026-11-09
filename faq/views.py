import nh3
from django.conf import settings
from django.core.cache import cache
from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response

from .models import FAQ, SUPPORTED_LANGUAGES
from .serializers import FAQSerializer
from .signals import faq_cache_key

LANGUAGE_NAMES = {"en": "English", "hi": "हिन्दी", "bn": "বাংলা"}


def resolve_lang(value):
    """Normalise a ?lang= value; anything unsupported falls back to English."""
    value = (value or "en").strip().lower()
    return value if value in SUPPORTED_LANGUAGES else "en"


def translated_faqs(lang):
    """Serialized FAQ list for ``lang``, cached per language.

    The cache stores plain data (not model instances) and is cleared by
    ``faq.signals`` whenever an FAQ changes.
    """
    key = faq_cache_key(lang)
    data = cache.get(key)
    if data is None:
        data = []
        for faq in FAQ.objects.all():
            item = FAQSerializer(faq).data
            item["question"] = faq.get_translated_question(lang)
            item["answer"] = faq.get_translated_answer(lang)
            # Answers are rich-text HTML; strip scripts/event handlers before
            # they are rendered by the home page or by API clients.
            for field in ("answer", "answer_hi", "answer_bn"):
                if item.get(field):
                    item[field] = nh3.clean(item[field])
            data.append(item)
        cache.set(key, data, timeout=settings.FAQ_CACHE_TIMEOUT)
    return data


def home(request):
    lang = resolve_lang(request.GET.get("lang"))
    context = {
        "faqs": translated_faqs(lang),
        "lang": lang,
        "languages": [(code, LANGUAGE_NAMES[code]) for code in SUPPORTED_LANGUAGES],
    }
    return render(request, "faq/home.html", context)


class FAQListView(generics.ListAPIView):
    """GET /api/faqs/?lang=hi|bn — read-only, public."""

    serializer_class = FAQSerializer
    queryset = FAQ.objects.all()

    def list(self, request, *args, **kwargs):
        lang = resolve_lang(request.query_params.get("lang"))
        return Response(translated_faqs(lang))
