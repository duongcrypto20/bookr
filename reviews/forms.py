from django import forms
from .models import Book, Publisher, Review

class PublisherForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = "__all__"

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        exclude = ["date_edited", "book"]

    # CSDL chấp nhận mọi giá trị rating, nên giới hạn 0-5 ở tầng form
    rating = forms.IntegerField(min_value=0, max_value=5)

#Tạo lớp Search Form 
class SearchForm(forms.Form):
    search = forms.CharField(required=False, min_length=3, label="Search")
    search_in = forms.ChoiceField(
        required=True,
        choices=[('title', 'Title'), ('contributor', 'Contributor')],
        initial='title',
        label="Search in"
    )


# (Bài tập Chương 6 - Bài 1, bước 5) Form chỉ dùng để tải ảnh bìa và nội dung mẫu cho sách
class BookMediaForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ["cover", "sample"]   # chỉ 2 trường vừa thêm ở model Book
