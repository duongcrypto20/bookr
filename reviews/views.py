from io import BytesIO                                   # Bộ đệm trong bộ nhớ, dùng khi thu nhỏ ảnh bìa
from PIL import Image                                    # Pillow: mở và thu nhỏ hình ảnh

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
# (Ch.7 - Bài III) login_required: bắt buộc đăng nhập; user_passes_test: kiểm tra người dùng bằng hàm tự viết
from django.core.exceptions import PermissionDenied      # Gây lỗi 403 Forbidden
from django.core.files.images import ImageFile           # Bọc dữ liệu ảnh để lưu vào ImageField
from django.db.models import Avg
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import BookMediaForm, PublisherForm, ReviewForm, SearchForm
from .models import Book, Contributor, Publisher, Review
from .utils import average_rating

#view hiển thị trang chủ
def index(request):
    return render(request, "base.html")

#view lấy toàn bộ danh sách sách, tính  điểm đánh giá trung bình, SL review cho từng cuốn sách
def book_list(request):
    books = Book.objects.all()
    book_list = []
    for book in books:
        reviews = book.review_set.all()
        if reviews:
            book_rating = average_rating([review.rating for review in reviews])
            number_of_reviews = len(reviews)
        else:
            book_rating = None
            number_of_reviews = 0
        book_list.append({
            'book': book,
            'book_rating': book_rating,
            'number_of_reviews': number_of_reviews
        })
    context = {
        'book_list': book_list
    }
    return render(request, 'views/base.html', context)

#view trang chào mừng
def welcome_view(request):
    return render(request, 'base.html')

#tìm kiếm sách, lấy chuỗi = GET
def book_search(request):
    # Khởi tạo form với dữ liệu từ request.GET
    form = SearchForm(request.GET)
    books = []
    search_text = ""
    if form.is_valid():
        search_text = form.cleaned_data.get("search")
        
        search_in = form.cleaned_data.get("search_in") or "title"
        
        if search_text:
            if search_in == "title":
                books = Book.objects.filter(title__icontains=search_text)
            #5.
            elif search_in == "contributor":
                #tìm bằng first_names, lats_names
                contributors_first = Contributor.objects.filter(first_names__icontains=search_text)
                contributors_last = Contributor.objects.filter(last_names__icontains=search_text)

                contributors = contributors_first.union(contributors_last)

                books = set()
                for contributor in contributors:
                    for book in contributor.book_set.all():
                        books.add(book)

    context = {
        "form": form,
        "search_text": search_text,
        "books": books,
    }
    return render(request, "reviews/search-results.html", context)

# (Ch.7 - Bài III, bước 2) Hàm kiểm tra: chỉ nhân viên (is_staff) mới đạt
def is_staff_user(user):
    return user.is_staff


# (Ch.7 - Bài III) Chỉ nhân viên mới được tạo/sửa nhà xuất bản.
# Người chưa đạt điều kiện sẽ bị chuyển tới trang đăng nhập.
# Cách 1 (thay thế, dùng quyền): @permission_required('edit_publisher')
@user_passes_test(is_staff_user)
#sửa publisher thông tin nhà xuất bản
def publisher_edit(request, pk=None):
    if pk is not None:
        publisher = get_object_or_404(Publisher, pk=pk)
    else:
        publisher = None
#kiếm tra người dùng gửi dữ liệu bằng POST hay GET
    if request.method == "POST":
        form = PublisherForm(request.POST, instance=publisher)
        if form.is_valid():
            updated_publisher = form.save()
            if publisher is None:
                messages.success(request, 'Publisher "{}" was created.'.format(updated_publisher))
            else:
                messages.success(request, 'Publisher "{}" was updated.'.format(updated_publisher))
            return redirect("publisher_edit", updated_publisher.pk)
    else:
        form = PublisherForm(instance=publisher)
    return render(request, "instance-form.html", {
        "form": form,
        "instance": publisher,
        "model_type": "Publisher",
    })


# (Ch.7 - Bài III, bước 3) Bắt buộc đăng nhập mới được tạo/sửa review
@login_required
#tạo mới hoặc chỉnh sửa review của một cuốn sách
def review_edit(request, book_pk, review_pk=None):
    book = get_object_or_404(Book, pk=book_pk)

    if review_pk is not None:
        # đảm bảo review thuộc về cuốn sách này
        review = get_object_or_404(Review, book_id=book_pk, pk=review_pk)
        # (Ch.7 - Bài III, bước 4) Chỉ nhân viên hoặc chính người viết review mới được sửa;
        # ngược lại báo lỗi 403 Forbidden
        user = request.user
        if not user.is_staff and review.creator.id != user.id:
            raise PermissionDenied
    else:
        review = None

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            updated_review = form.save(commit=False)
            updated_review.book = book

            if review is not None:
                updated_review.date_edited = timezone.now()

            updated_review.save()

            if review is None:
                messages.success(request, 'Review for "{}" created.'.format(book))
            else:
                messages.success(request, 'Review for "{}" updated.'.format(book))

            return redirect("book_detail", book.pk)
    else:
        form = ReviewForm(instance=review)

    return render(request, "instance-form.html", {
        "form": form,
        "instance": review,
        "model_type": "Review",
        "related_instance": book,
        "related_model_type": "Book",
    })

# (Bài tập Chương 6 - Bài 1) Thêm/đổi ảnh bìa và tập tin nội dung mẫu cho một cuốn sách ĐÃ CÓ
# (không tạo sách mới nên bắt buộc có tham số pk). Yêu cầu đăng nhập (Ch.7 - Bài III, bước 3).
@login_required
def book_media(request, pk):
    book = get_object_or_404(Book, pk=pk)

    if request.method == "POST":
        # request.FILES chứa các tập tin tải lên; instance=book để cập nhật sách hiện có
        form = BookMediaForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            # commit=False: chưa lưu ngay vì còn phải thu nhỏ ảnh bìa
            book = form.save(False)
            cover = form.cleaned_data.get("cover")
            # Chỉ xử lý ảnh khi người dùng vừa chọn một ảnh MỚI ("cover" nằm trong changed_data).
            # Nếu để trống, hoặc ảnh đã có sẵn từ trước, thì không thu nhỏ lại.
            if cover and "cover" in form.changed_data:
                image = Image.open(cover)
                image.thumbnail((300, 300))          # Thu nhỏ, giữ tỉ lệ, tối đa 300 x 300 pixel
                image_data = BytesIO()               # Ghi ảnh đã thu nhỏ vào bộ nhớ
                image.save(fp=image_data, format=image.format)
                image_file = ImageFile(image_data)
                book.cover.save(cover.name, image_file)   # Lưu ảnh đã thu nhỏ vào media/book_covers/
            book.save()                              # Lưu các thay đổi (kể cả tập tin sample) vào CSDL
            messages.success(request, 'Book "{}" was successfully updated.'.format(book))
            return redirect("book_detail", book.pk)
    else:
        # Mở trang lần đầu: form điền sẵn các tập tin hiện có của cuốn sách
        form = BookMediaForm(instance=book)

    return render(request, "instance-form.html", {
        "form": form,
        "instance": book,
        "model_type": "Book",
        "is_file_upload": True,      # Để instance-form.html thêm enctype="multipart/form-data"
    })


#view hiển thị chi tiết của một cuốn sách
def book_detail(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    reviews = book.review_set.all()
    overall_rating = reviews.aggregate(Avg('rating'))['rating__avg']

    context = {
        'book': book,
        'reviews': reviews,
        'overall_rating': round(overall_rating, 1) if overall_rating else None
    }

    # (Ch.7 - Bài VI) Chỉ lưu lịch sử xem sách cho người dùng ĐÃ đăng nhập
    if request.user.is_authenticated:
        max_viewed_books_length = 10    # Tối đa 10 cuốn sách xem gần nhất
        # Lấy danh sách đã lưu trong session; chưa có thì dùng danh sách rỗng
        viewed_books = request.session.get('viewed_books', [])
        viewed_book = [book.id, book.title]
        # Nếu sách đã có trong danh sách thì bỏ ra để đưa lên đầu (tránh trùng lặp)
        if viewed_book in viewed_books:
            viewed_books.pop(viewed_books.index(viewed_book))
        viewed_books.insert(0, viewed_book)                      # Sách vừa xem nằm đầu danh sách
        viewed_books = viewed_books[:max_viewed_books_length]    # Chỉ giữ 10 cuốn đầu tiên
        request.session['viewed_books'] = viewed_books           # Ghi lại vào session cho các request sau

    return render(request, 'book_detail.html', context)
