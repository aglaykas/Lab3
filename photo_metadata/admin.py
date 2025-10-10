from django.contrib import admin
from .models import PhotoMetadata, ImportedFile

@admin.register(PhotoMetadata)
class PhotoMetadataAdmin(admin.ModelAdmin):
    list_display = ('filename', 'format', 'file_size', 'width', 'height', 'camera_make', 'created_date')
    list_filter = ('format', 'camera_make', 'created_date')
    search_fields = ('filename', 'camera_model', 'description')
    readonly_fields = ('created_date',)

@admin.register(ImportedFile)
class ImportedFileAdmin(admin.ModelAdmin):
    list_display = ('file', 'upload_date', 'is_valid')
    list_filter = ('is_valid', 'upload_date')
    readonly_fields = ('upload_date',)