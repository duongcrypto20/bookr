from django import forms
from .models import Publisher

class PublisherForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = "__all__"

#Tạo lớp Search Form 
class SearchForm(forms.Form):
    search = forms.CharField(required=False, min_length=3, label="Search")
    search_in = forms.ChoiceField(
        required=True,
        choices=[('title', 'Title'), ('contributor', 'Contributor')],
        initial='title',
        label="Search in"
    )