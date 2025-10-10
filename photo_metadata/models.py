from django.db import models

from django.db import models
import os
import uuid

class PhotoMetadata(models.Model):
    FORMAT_CHOICES = [
        ('JPEG', 'JPEG'),
        ('PNG', 'PNG'),
        ('GIF', 'GIF'),
        ('BMP', 'BMP'),
        ('TIFF', 'TIFF'),
    ]
    
    # Основная информация
    filename = models.CharField(max_length=255, verbose_name="Имя файла")
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, verbose_name="Формат")
    file_size = models.PositiveIntegerField(verbose_name="Размер файла (байт)")
    
    # Размеры изображения
    width = models.PositiveIntegerField(verbose_name="Ширина (px)")
    height = models.PositiveIntegerField(verbose_name="Высота (px)")
    
    # Метаданные камеры
    camera_make = models.CharField(max_length=100, blank=True, verbose_name="Производитель камеры")
    camera_model = models.CharField(max_length=100, blank=True, verbose_name="Модель камеры")
    
    # Настройки съемки
    exposure_time = models.CharField(max_length=20, blank=True, verbose_name="Выдержка")
    aperture = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, verbose_name="Диафрагма")
    iso = models.PositiveIntegerField(null=True, blank=True, verbose_name="ISO")
    focal_length = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True, verbose_name="Фокусное расстояние")
    
    # Информация о местоположении
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="Широта")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="Долгота")
    
    # Дополнительная информация
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания записи")
    capture_date = models.DateTimeField(null=True, blank=True, verbose_name="Дата съемки")
    description = models.TextField(blank=True, verbose_name="Описание")
    tags = models.CharField(max_length=500, blank=True, verbose_name="Теги (через запятую)")
    
    class Meta:
        verbose_name = "Метаданные фотографии"
        verbose_name_plural = "Метаданные фотографий"
    
    def __str__(self):
        return f"{self.filename} ({self.width}x{self.height})"

def get_upload_path(instance, filename):
    """Генерируем безопасное имя файла"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join('json_uploads', filename)

class ImportedFile(models.Model):
    file = models.FileField(upload_to=get_upload_path, verbose_name="Файл JSON")
    upload_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")
    is_valid = models.BooleanField(default=True, verbose_name="Валидный файл")
    
    class Meta:
        verbose_name = "Импортированный файл"
        verbose_name_plural = "Импортированные файлы"
    
    def __str__(self):
        return f"{os.path.basename(self.file.name)}"