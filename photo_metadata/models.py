from django.db import models
import os
import uuid
from django.core.validators import MinValueValidator

class PhotoMetadata(models.Model):
    FORMAT_CHOICES = [
        ('JPEG', 'JPEG'),
        ('PNG', 'PNG'),
        ('GIF', 'GIF'),
        ('BMP', 'BMP'),
        ('TIFF', 'TIFF'),
    ]
    
    filename = models.CharField(max_length=255,unique=True, verbose_name="Имя файла")
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, verbose_name="Формат")
    file_size = models.PositiveIntegerField(
        verbose_name="Размер файла (байт)",
        validators=[MinValueValidator(1)]
    )
    width = models.PositiveIntegerField(
        verbose_name="Ширина (px)",
        validators=[MinValueValidator(1)]
    )
    height = models.PositiveIntegerField(
        verbose_name="Высота (px)", 
        validators=[MinValueValidator(1)]
    )
    camera_make = models.CharField(max_length=100, blank=True, verbose_name="Производитель камеры")
    camera_model = models.CharField(max_length=100, blank=True, verbose_name="Модель камеры")
    exposure_time = models.CharField(max_length=20, blank=True, verbose_name="Выдержка")
    aperture = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, verbose_name="Диафрагма")
    iso = models.PositiveIntegerField(null=True, blank=True, verbose_name="ISO")
    focal_length = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True, verbose_name="Фокусное расстояние")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="Широта")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="Долгота")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания записи")
    capture_date = models.DateTimeField(null=True, blank=True, verbose_name="Дата съемки")
    description = models.TextField(blank=True, verbose_name="Описание")
    tags = models.CharField(max_length=500, blank=True, verbose_name="Теги (через запятую)")
    
    class Meta:
        verbose_name = "Метаданные фотографии"
        verbose_name_plural = "Метаданные фотографий"
        unique_together = ['filename', 'format', 'file_size', 'width', 'height']  
    
    def __str__(self):
        return f"{self.filename} ({self.width}x{self.height})"

def get_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join('json_uploads', filename)
def clean(self):
    if PhotoMetadata.objects.filter(filename=self.filename).exclude(id=self.id).exists():
        raise ValidationError({'filename': 'Запись с таким именем файла уже существует'})

class ImportedFile(models.Model):
    file = models.FileField(upload_to=get_upload_path, verbose_name="Файл JSON")
    upload_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")
    is_valid = models.BooleanField(default=True, verbose_name="Валидный файл")
    
    class Meta:
        verbose_name = "Импортированный файл"
        verbose_name_plural = "Импортированные файлы"
    
    def __str__(self):
        return f"{os.path.basename(self.file.name)}"
