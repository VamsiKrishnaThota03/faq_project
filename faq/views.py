from rest_framework import generics
from .models import FAQ
from .serializers import FAQSerializer
from django.core.cache import cache
from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to the FAQ site!")


class FAQListView(generics.ListAPIView):
    serializer_class = FAQSerializer

    def get_queryset(self):
        lang = self.request.query_params.get('lang', 'en')  # Default to 'en' if no lang param
        cache_key = f'faqs_{lang}'
        queryset = cache.get(cache_key)

        if not queryset:
            queryset = FAQ.objects.all()
            for faq in queryset:
                faq.question = faq.get_translated_question(lang)  # Call the new method
                faq.answer = faq.get_translated_answer(lang)      # Call the new method
            cache.set(cache_key, queryset, timeout=60 * 15)  # Cache for 15 minutes
        return queryset
