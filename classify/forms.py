from django import forms

class ImageUploadForm(forms.Form):
    image = forms.ImageField(label='上傳食物照片')

from .models import Photo

class PhotoForm(forms.ModelForm):
    class Meta:
        model  = Photo
        fields = ['image']

