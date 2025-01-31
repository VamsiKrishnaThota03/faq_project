from rest_framework import generics
from .models import FAQ
from .serializers import FAQSerializer

class FAQListView(generics.ListAPIView):
    serializer_class = FAQSerializer

    def get_queryset(self):
        lang = self.request.query_params.get('lang', 'en')
        queryset = FAQ.objects.all()
        for faq in queryset:
            faq.question = faq.get_translated_question(lang)
            faq.answer = faq.get_translated_answer(lang)
        return queryset