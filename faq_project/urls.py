from django.contrib import admin
from django.urls import path, include
from faq.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('api/', include('faq.urls')),
    path('', home, name='home'),
]
