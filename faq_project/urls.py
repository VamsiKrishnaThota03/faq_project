from django.contrib import admin
from django.urls import include, path

from faq.views import home

admin.site.site_header = "FAQ administration"
admin.site.site_title = "FAQ admin"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('faq.urls')),
    path('', home, name='home'),
]
