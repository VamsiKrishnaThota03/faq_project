from django.urls import path
from . import views

urlpatterns = [
    path('faq/', views.FAQListView.as_view(), name='faq-list'),
]
