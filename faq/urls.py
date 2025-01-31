from django.urls import path, include
from .views import FAQListView

urlpatterns = [
    path('faqs/', FAQListView.as_view(), name='faq-list'),
    path('api/', include('faq.urls')),
]