from reviews.admin import admin
import reviews.views
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("book-search/", reviews.views.book_search, name="book_search"),
    path("", include("reviews.urls")),
]