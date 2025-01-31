from rest_framework import generics
from .models import FAQ
from .serializers import FAQSerializer

from django.core.cache import cache

from googletrans import Translator

translator = Translator()

def translate_text(text, dest_lang):
    try:
        return translator.translate(text, dest=dest_lang).text
    except:
        return text

class FAQListView(generics.ListAPIView):
    serializer_class = FAQSerializer

    def get_queryset(self):
        lang = self.request.query_params.get('lang', 'en')
        cache_key = f'faqs_{lang}'
        queryset = cache.get(cache_key)
        if not queryset:
            queryset = FAQ.objects.all()
            for faq in queryset:
                faq.question = faq.get_translated_question(lang)
                faq.answer = faq.get_translated_answer(lang)
            cache.set(cache_key, queryset, timeout=60 * 15)  # Cache for 15 minutes
        return queryset