from django.conf import settings                     # Dùng để kiểm tra chế độ DEBUG và MEDIA_URL/MEDIA_ROOT
from django.conf.urls.static import static          # Hàm phục vụ tập tin media khi phát triển
from django.contrib.auth import views as auth_views  # Các view xác thực có sẵn của Django (Ch.7 - Bài I, bước 6)
from django.urls import include, path

from reviews.admin import admin
import reviews.views
from bookr.views import profile                      # (Ch.7 - Bài II, bước 3) View hồ sơ người dùng

urlpatterns = [
    # (Ch.7 - Bài I, bước 6) Gắn toàn bộ URL xác thực của Django (login, logout, đổi/đặt lại mật khẩu...)
    # dưới tiền tố accounts/ với namespace "accounts" (dùng trong template: {% url 'accounts:login' %})
    path(
        "accounts/",
        include(
            ("django.contrib.auth.urls", "auth"),
            namespace="accounts"
        )
    ),
    # Hai trang kết quả của quy trình đặt lại mật khẩu
    path(
        "accounts/password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "accounts/reset/done/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    # (Ch.7 - Bài II, bước 3) Trang hồ sơ người dùng: /accounts/profile/
    path('accounts/profile/', profile, name='profile'),

    path("admin/", admin.site.urls),
    path("book-search/", reviews.views.book_search, name="book_search"),
    path("", include("reviews.urls")),
]

# (BT Chương 6 - Bài 1, bước 2) Chỉ trong chế độ DEBUG: phục vụ tập tin trong MEDIA_ROOT tại MEDIA_URL
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
