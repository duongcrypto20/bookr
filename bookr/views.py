# (Ch.7 - Bài II, bước 1) View hiển thị trang hồ sơ người dùng
from django.shortcuts import render


def profile(request):
    # Không cần truyền dữ liệu riêng: template dùng trực tiếp request.user
    # (nhờ context processor 'auth' / 'request' đã bật trong TEMPLATES của settings.py)
    return render(request, 'profile.html')
