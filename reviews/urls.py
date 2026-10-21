from django.contrib import admin
from django.urls import path
from . import views
from . import views, api_views
urlpatterns = [
    path('api/first_api_view/',  api_views.first_api_view),
    path('', views.welcome_view, name='welcome_view'),
    path("publishers/<int:pk>/",views.publisher_edit, name="publisher_edit"),
    path("publishers/new/",views.publisher_edit, name="publisher_create"),

    path('books/<int:book_id>/', views.book_detail, name='book_detail'),
    #path("publishers/new/", views.publisher_edit, name="publisher_create"),
]