from django import forms
from .models import PhotoMetadata
import re

class PhotoMetadataForm(forms.ModelForm):
    SAVE_CHOICES = [
        ('file', 'Сохранить в файл JSON'),
        ('db', 'Сохранить в базу данных'),
        ('both', 'Сохранить в файл и базу данных'),
    ]
    
    save_option = forms.ChoiceField(
        choices=SAVE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Куда сохранить данные?',
        initial='both'
    )
    
    class Meta:
        model = PhotoMetadata
        fields = [
            'filename', 'format', 'file_size', 'width', 'height',
            'camera_make', 'camera_model', 'exposure_time', 'aperture',
            'iso', 'focal_length', 'latitude', 'longitude',
            'capture_date', 'description', 'tags', 'save_option'
        ]
        widgets = {
            'filename': forms.TextInput(attrs={'class': 'form-control'}),
            'format': forms.Select(attrs={'class': 'form-control'}),
            'file_size': forms.NumberInput(attrs={'class': 'form-control'}),
            'width': forms.NumberInput(attrs={'class': 'form-control'}),
            'height': forms.NumberInput(attrs={'class': 'form-control'}),
            'camera_make': forms.TextInput(attrs={'class': 'form-control'}),
            'camera_model': forms.TextInput(attrs={'class': 'form-control'}),
            'exposure_time': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1/125'}),
            'aperture': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'iso': forms.NumberInput(attrs={'class': 'form-control'}),
            'focal_length': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'capture_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'пейзаж, природа, лето'}),
        }
    
    def clean_filename(self):
        filename = self.cleaned_data['filename']
        if not re.match(r'^[\w\-. ]+$', filename):
            raise forms.ValidationError("Имя файла содержит недопустимые символы")
        return filename
    
    def clean_file_size(self):
        file_size = self.cleaned_data['file_size']
        if file_size <= 0:
            raise forms.ValidationError("Размер файла должен быть положительным числом")
        return file_size
    
    def clean_width(self):
        width = self.cleaned_data['width']
        if width <= 0:
            raise forms.ValidationError("Ширина должна быть положительным числом")
        return width
    
    def clean_height(self):
        height = self.cleaned_data['height']
        if height <= 0:
            raise forms.ValidationError("Высота должна быть положительным числом")
        return height

class FileUploadForm(forms.Form):
    file = forms.FileField(
        label="Выберите JSON файл",
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.json'}),
        help_text="Поддерживаемый формат: JSON"
    )

class EditPhotoMetadataForm(forms.ModelForm):
    class Meta:
        model = PhotoMetadata
        fields = [
            'filename', 'format', 'file_size', 'width', 'height',
            'camera_make', 'camera_model', 'exposure_time', 'aperture',
            'iso', 'focal_length', 'latitude', 'longitude',
            'capture_date', 'description', 'tags'
        ]
        widgets = {
            'filename': forms.TextInput(attrs={'class': 'form-control'}),
            'format': forms.Select(attrs={'class': 'form-control'}),
            'file_size': forms.NumberInput(attrs={'class': 'form-control'}),
            'width': forms.NumberInput(attrs={'class': 'form-control'}),
            'height': forms.NumberInput(attrs={'class': 'form-control'}),
            'camera_make': forms.TextInput(attrs={'class': 'form-control'}),
            'camera_model': forms.TextInput(attrs={'class': 'form-control'}),
            'exposure_time': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1/125'}),
            'aperture': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'iso': forms.NumberInput(attrs={'class': 'form-control'}),
            'focal_length': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'capture_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'пейзаж, природа, лето'}),
        }