from django.shortcuts import render

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
import os
import json

from .forms import PhotoMetadataForm, FileUploadForm
from .models import PhotoMetadata, ImportedFile
from .utils import JSONFileProcessor

def home(request):
    """Главная страница"""
    return render(request, 'photo_metadata/index.html')

def input_form(request):
    """Форма ввода данных"""
    if request.method == 'POST':
        form = PhotoMetadataForm(request.POST)
        if form.is_valid():
            # Сохраняем в базу данных
            photo_metadata = form.save()
            
            # Подготавливаем данные для экспорта в JSON
            data = {
                'id': photo_metadata.id,
                'filename': photo_metadata.filename,
                'format': photo_metadata.format,
                'file_size': photo_metadata.file_size,
                'width': photo_metadata.width,
                'height': photo_metadata.height,
                'camera_make': photo_metadata.camera_make,
                'camera_model': photo_metadata.camera_model,
                'exposure_time': photo_metadata.exposure_time,
                'aperture': str(photo_metadata.aperture) if photo_metadata.aperture else None,
                'iso': photo_metadata.iso,
                'focal_length': str(photo_metadata.focal_length) if photo_metadata.focal_length else None,
                'latitude': str(photo_metadata.latitude) if photo_metadata.latitude else None,
                'longitude': str(photo_metadata.longitude) if photo_metadata.longitude else None,
                'capture_date': photo_metadata.capture_date.isoformat() if photo_metadata.capture_date else None,
                'description': photo_metadata.description,
                'tags': photo_metadata.tags,
                'created_date': photo_metadata.created_date.isoformat(),
            }
            
            # Удаляем None значения
            data = {k: v for k, v in data.items() if v is not None}
            
            # Сохраняем в JSON файл
            file_processor = JSONFileProcessor()
            json_filename = file_processor.generate_safe_filename(photo_metadata.filename)
            json_path = file_processor.save_to_json(data, json_filename)
            
            messages.success(request, f'Данные успешно сохранены! JSON файл создан: {json_filename}')
            return redirect('input_form')
    else:
        form = PhotoMetadataForm()
    
    return render(request, 'photo_metadata/input_form.html', {'form': form})

def upload_file(request):
    """Загрузка JSON файлов на сервер"""
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            
            # Проверяем расширение файла
            if not uploaded_file.name.lower().endswith('.json'):
                messages.error(request, 'Пожалуйста, загружайте только JSON файлы')
                return redirect('upload_file')
            
            # Генерируем безопасное имя файла
            safe_filename = JSONFileProcessor.generate_safe_filename(uploaded_file.name)
            
            # Сохраняем файл
            fs = FileSystemStorage()
            filename = fs.save(safe_filename, uploaded_file)
            file_path = fs.path(filename)
            
            # Проверяем валидность JSON файла
            is_valid, message = JSONFileProcessor.validate_json_file(file_path)
            
            if is_valid:
                # Сохраняем информацию о файле в базу
                imported_file = ImportedFile(
                    file=filename,
                    is_valid=True
                )
                imported_file.save()
                
                # Парсим файл и сохраняем данные в базу
                try:
                    file_data = JSONFileProcessor.read_json_file(file_path)
                    
                    # Обрабатываем данные (может быть список или один объект)
                    if isinstance(file_data, list):
                        for item in file_data:
                            # Удаляем поля, которые не нужны для создания модели
                            item.pop('id', None)
                            item.pop('created_date', None)
                            PhotoMetadata.objects.create(**item)
                    else:
                        file_data.pop('id', None)
                        file_data.pop('created_date', None)
                        PhotoMetadata.objects.create(**file_data)
                    
                    messages.success(request, f'Файл {uploaded_file.name} успешно загружен и обработан!')
                except Exception as e:
                    messages.warning(request, f'Файл загружен, но возникли ошибки при обработке данных: {str(e)}')
            else:
                # Удаляем невалидный файл
                fs.delete(filename)
                messages.error(request, f'JSON файл не валиден: {message}')
            
            return redirect('upload_file')
    else:
        form = FileUploadForm()
    
    return render(request, 'photo_metadata/upload_file.html', {'form': form})

def view_files(request):
    """Просмотр всех JSON файлов"""
    json_dir = 'media/json_files'
    
    json_files = []
    
    # Получаем JSON файлы
    if os.path.exists(json_dir):
        for filename in os.listdir(json_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(json_dir, filename)
                file_size = os.path.getsize(file_path)
                json_files.append({
                    'name': filename,
                    'path': file_path,
                    'size': file_size,
                    'url': f'/media/json_files/{filename}'
                })
    
    context = {
        'json_files': json_files,
        'total_files': len(json_files)
    }
    
    return render(request, 'photo_metadata/view_files.html', context)

def view_file_content(request, filename):
    """Просмотр содержимого конкретного JSON файла"""
    safe_filename = os.path.basename(filename)  # Санитайзинг имени файла
    
    file_path = os.path.join('media', 'json_files', safe_filename)
    
    if not os.path.exists(file_path):
        return HttpResponse("Файл не найден", status=404)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
        return JsonResponse(content, safe=False, json_dumps_params={'ensure_ascii': False, 'indent': 2})
    except Exception as e:
        return HttpResponse(f"Ошибка при чтении файла: {str(e)}", status=500)

def view_database_records(request):
    """Просмотр всех записей из базы данных"""
    records = PhotoMetadata.objects.all().order_by('-created_date')
    return render(request, 'photo_metadata/database_records.html', {'records': records})