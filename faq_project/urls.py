from django.contrib import admin
from django.urls import path, include
from faq import views  # Import the views from the 'faq' app

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('api/', include('faq.urls')),
    path('', views.home, name='home'),  # Add this line to map root URL to home view
]
