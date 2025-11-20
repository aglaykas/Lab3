from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.db import IntegrityError
from django.db import models 
import os
import json

from .forms import PhotoMetadataForm, FileUploadForm, EditPhotoMetadataForm
from .models import PhotoMetadata, ImportedFile
from .utils import JSONFileProcessor

def home(request):
    
    return render(request, 'photo_metadata/index.html')
def input_form(request):
    if request.method == 'POST':
        form = PhotoMetadataForm(request.POST)
        if form.is_valid():
            save_option = form.cleaned_data['save_option']
            photo_data = form.cleaned_data.copy()
            photo_data.pop('save_option')  
            
            file_saved = False
            db_saved = False
            duplicate_found = False
            
            try:
                if save_option in ['file', 'both']:
                    file_processor = JSONFileProcessor()
                    json_filename = file_processor.generate_safe_filename(photo_data['filename'])
                    
                    data_for_json = {
                    'filename': photo_data['filename'],
                    'format': photo_data['format'],
                    'file_size': photo_data['file_size'],
                    'width': photo_data['width'],
                    'height': photo_data['height'],
                    'camera_make': photo_data['camera_make'],
                    'camera_model': photo_data['camera_model'],
                    'exposure_time': photo_data['exposure_time'],
                    'aperture': str(photo_data['aperture']) if photo_data['aperture'] else None,
                    'iso': photo_data['iso'],
                    'focal_length': str(photo_data['focal_length']) if photo_data['focal_length'] else None,
                    'latitude': str(photo_data['latitude']) if photo_data['latitude'] else None,
                    'longitude': str(photo_data['longitude']) if photo_data['longitude'] else None,
                    'capture_date': photo_data['capture_date'].isoformat() if photo_data['capture_date'] else None,
                    'description': photo_data['description'],
                    'tags': photo_data['tags'],
                    }
                    
                    data_for_json = {k: v for k, v in data_for_json.items() if v is not None}
                    file_processor.save_to_json(data_for_json, json_filename)
                    file_saved = True
                
                if save_option in ['db', 'both']:
                    # Убираем ручную проверку дубликатов - теперь это делает форма
                    photo_metadata = PhotoMetadata(**photo_data)
                    photo_metadata.full_clean()  # Дополнительная валидация
                    photo_metadata.save()
                    db_saved = True
                    
            except ValidationError as e:
                # Обрабатываем ошибки валидации модели
                duplicate_found = True
                messages.error(request, f'Ошибка валидации: {e}')
            except IntegrityError:
                # Ловим ошибку уникальности от базы данных
                duplicate_found = True
                messages.error(request, 'Запись с таким именем файла уже существует в базе данных!')
            
            # Сообщения об успехе/ошибке
            if file_saved and db_saved:
                messages.success(request, 'Данные успешно сохранены в файл и базу данных!')
            elif file_saved:
                messages.success(request, 'Данные успешно сохранены в файл JSON!')
            elif db_saved:
                messages.success(request, 'Данные успешно сохранены в базу данных!')
            elif duplicate_found and file_saved:
                messages.info(request, 'Данные сохранены только в файл (дубликат в БД)!')
            
            return redirect('input_form')
    else:
        form = PhotoMetadataForm()
    
    return render(request, 'photo_metadata/input_form.html', {'form': form})


def upload_file(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            
            if not uploaded_file.name.lower().endswith('.json'):
                messages.error(request, 'Пожалуйста, загружайте только JSON файлы')
                return redirect('upload_file')
            
            safe_filename = JSONFileProcessor.generate_safe_filename(uploaded_file.name)
            
            fs = FileSystemStorage()
            filename = fs.save(safe_filename, uploaded_file)
            file_path = fs.path(filename)
            
            is_valid, message = JSONFileProcessor.validate_json_file(file_path)
            
            if is_valid:
                imported_file = ImportedFile(
                    file=filename,
                    is_valid=True
                )
                imported_file.save()
                
                try:
                    file_data = JSONFileProcessor.read_json_file(file_path)
                    records_added = 0
                    duplicates_found = 0
                    
                    if isinstance(file_data, list):
                        for item in file_data:
                            item.pop('id', None)
                            item.pop('created_date', None)
                            
                            duplicate = PhotoMetadata.objects.filter(
                                filename=item.get('filename'),
                                format=item.get('format'),
                                file_size=item.get('file_size'),
                                width=item.get('width'),
                                height=item.get('height')
                            ).exists()
                            
                            if not duplicate:
                                PhotoMetadata.objects.create(**item)
                                records_added += 1
                            else:
                                duplicates_found += 1
                    else:
                        file_data.pop('id', None)
                        file_data.pop('created_date', None)
                        
                        duplicate = PhotoMetadata.objects.filter(
                            filename=file_data.get('filename'),
                            format=file_data.get('format'),
                            file_size=file_data.get('file_size'),
                            width=file_data.get('width'),
                            height=file_data.get('height')
                        ).exists()
                        
                        if not duplicate:
                            PhotoMetadata.objects.create(**file_data)
                            records_added += 1
                        else:
                            duplicates_found += 1
                    
                    if records_added > 0:
                        messages.success(request, f'Успешно добавлено {records_added} записей в базу данных!')
                    if duplicates_found > 0:
                        messages.warning(request, f'Найдено {duplicates_found} дубликатов (не добавлены в БД)')
                    
                except Exception as e:
                    messages.warning(request, f'Файл загружен, но возникли ошибки при обработке данных: {str(e)}')
            else:
                fs.delete(filename)
                messages.error(request, f'JSON файл не валиден: {message}')
            
            return redirect('upload_file')
    else:
        form = FileUploadForm()
    
    return render(request, 'photo_metadata/upload_file.html', {'form': form})

def view_files(request):
    source = request.GET.get('source', 'files')  
    
    context = {'source': source}
    
    if source == 'db':
        db_records = PhotoMetadata.objects.all().order_by('-created_date')
        context['db_records'] = db_records
        
    else:
        json_files_dir = 'media/json_files'
        json_uploads_dir = 'media/json_uploads'
        
        json_files = []
     
        if os.path.exists(json_files_dir):
            for filename in os.listdir(json_files_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(json_files_dir, filename)
                    file_size = os.path.getsize(file_path)
                    json_files.append({
                        'name': filename,
                        'path': file_path,
                        'size': file_size,
                        'url': f'/media/json_files/{filename}',
                        'type': 'created'
                    })
        
        if os.path.exists(json_uploads_dir):
            for filename in os.listdir(json_uploads_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(json_uploads_dir, filename)
                    file_size = os.path.getsize(file_path)
                    json_files.append({
                        'name': filename,
                        'path': file_path,
                        'size': file_size,
                        'url': f'/media/json_uploads/{filename}',
                        'type': 'uploaded'
                    })
        
        json_files.sort(key=lambda x: x['name'])
        context['json_files'] = json_files
    
    return render(request, 'photo_metadata/view_files.html', context)

def view_file_content(request, filename):
    safe_filename = os.path.basename(filename)
    
    file_paths = [
        os.path.join('media', 'json_files', safe_filename),
        os.path.join('media', 'json_uploads', safe_filename)
    ]
    
    file_path = None
    file_type = None
    
    for path in file_paths:
        if os.path.exists(path):
            file_path = path
            if 'json_files' in path:
                file_type = 'created'
            else:
                file_type = 'uploaded'
            break
    
    if not file_path:
        return HttpResponse("Файл не найден")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        context = {
            'filename': filename,
            'content': content,
            'file_type': file_type,
            'file_path': file_path
        }
        return render(request, 'photo_metadata/view_file_content.html', context)
        
    except Exception as e:
        return HttpResponse(f"Ошибка: {str(e)}")

def search_records(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        query = request.GET.get('q', '')
        
        if query:
            records = PhotoMetadata.objects.filter(
                models.Q(filename__icontains=query) |
                models.Q(camera_make__icontains=query) |
                models.Q(camera_model__icontains=query) |
                models.Q(description__icontains=query) |
                models.Q(tags__icontains=query)
            ).order_by('-created_date')
        else:
            records = PhotoMetadata.objects.all().order_by('-created_date')

        records_data = []
        for record in records:
            records_data.append({
                'id': record.id,
                'filename': record.filename,
                'format': record.format,
                'file_size': record.file_size,
                'width': record.width,
                'height': record.height,
                'camera_make': record.camera_make,
                'camera_model': record.camera_model,
                'description': record.description,
                'created_date': record.created_date.strftime('%d.%m.%Y %H:%M')
            })
        
        return JsonResponse({'records': records_data})
    
    return JsonResponse({'error': 'Invalid request'})

def edit_record(request, record_id):
    record = get_object_or_404(PhotoMetadata, id=record_id)
    
    if request.method == 'POST':
        form = EditPhotoMetadataForm(request.POST, instance=record)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Запись успешно обновлена!')
                return redirect('database_records')
            except IntegrityError:
                messages.error(request, 'Ошибка: запись с таким именем файла уже существует!')
            except ValidationError as e:
                messages.error(request, f'Ошибка валидации: {e}')
    else:
        form = EditPhotoMetadataForm(instance=record)
    
    context = {
        'form': form,
        'record': record
    }
    return render(request, 'photo_metadata/edit_record.html', context)

def delete_record(request, record_id):

    record = get_object_or_404(PhotoMetadata, id=record_id)
    
    if request.method == 'POST':
        record.delete()
        messages.success(request, 'Запись успешно удалена!')
        return redirect('database_records')
    
    context = {
        'record': record
    }
    return render(request, 'photo_metadata/delete_record.html', context)
def view_database_records(request):
    records = PhotoMetadata.objects.all().order_by('-created_date')
    
    
    search_query = request.GET.get('q', '')
    if search_query:
        records = records.filter(
            models.Q(filename__icontains=search_query) |
            models.Q(camera_make__icontains=search_query) |
            models.Q(camera_model__icontains=search_query) |
            models.Q(description__icontains=search_query) |
            models.Q(tags__icontains=search_query)
        )
    
    context = {
        'records': records,
        'search_query': search_query
    }
    return render(request, 'photo_metadata/database_records.html', context)
    
def view_record(request, record_id):
    record = get_object_or_404(PhotoMetadata, id=record_id)

    record_data = {
        'id': record.id,
        'filename': record.filename,
        'format': record.format,
        'file_size': record.file_size,
        'width': record.width,
        'height': record.height,
        'camera_make': record.camera_make,
        'camera_model': record.camera_model,
        'exposure_time': record.exposure_time,
        'aperture': str(record.aperture) if record.aperture else None,
        'iso': record.iso,
        'focal_length': str(record.focal_length) if record.focal_length else None,
        'latitude': str(record.latitude) if record.latitude else None,
        'longitude': str(record.longitude) if record.longitude else None,
        'capture_date': record.capture_date.isoformat() if record.capture_date else None,
        'description': record.description,
        'tags': record.tags,
        'created_date': record.created_date.isoformat(),
    }
    
    record_data = {k: v for k, v in record_data.items() if v is not None}

    formatted_json = json.dumps(record_data, ensure_ascii=False, indent=2)
    
    context = {
        'record': record,
        'content': formatted_json,
        'title': f'Запись: {record.filename}'
    }
    
    return render(request, 'photo_metadata/view_record.html', context)