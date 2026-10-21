from django.contrib import messages
from django.db.models import Avg
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import PublisherForm, ReviewForm, SearchForm
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


#tạo mới hoặc chỉnh sửa review của một cuốn sách
def review_edit(request, book_pk, review_pk=None):
    book = get_object_or_404(Book, pk=book_pk)

    if review_pk is not None:
        # đảm bảo review thuộc về cuốn sách này
        review = get_object_or_404(Review, book_id=book_pk, pk=review_pk)
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
    return render(request, 'book_detail.html', context)