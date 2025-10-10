from django import forms
from .models import PhotoMetadata
import re

class PhotoMetadataForm(forms.ModelForm):
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
    
    def clean_iso(self):
        iso = self.cleaned_data.get('iso')
        if iso and iso <= 0:
            raise forms.ValidationError("ISO должно быть положительным числом")
        return iso
    
    def clean_latitude(self):
        latitude = self.cleaned_data.get('latitude')
        if latitude and (latitude < -90 or latitude > 90):
            raise forms.ValidationError("Широта должна быть в диапазоне от -90 до 90")
        return latitude
    
    def clean_longitude(self):
        longitude = self.cleaned_data.get('longitude')
        if longitude and (longitude < -180 or longitude > 180):
            raise forms.ValidationError("Долгота должна быть в диапазоне от -180 до 180")
        return longitude

class FileUploadForm(forms.Form):
    file = forms.FileField(
        label="Выберите JSON файл",
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.json'}),
        help_text="Поддерживаемый формат: JSON"
    )