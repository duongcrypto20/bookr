from django.contrib import admin
from django.urls import path
import form_example.views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('form-example/', form_example.views.form_example),
]