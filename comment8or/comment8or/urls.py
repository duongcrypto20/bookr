from django.contrib import admin
from django.urls import path
from comment8or.admin import admin_site

urlpatterns = [
    path('admin/', admin_site.urls),
]