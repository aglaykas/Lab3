import json
import os
import uuid
from django.core.files.storage import FileSystemStorage
from .models import PhotoMetadata

class JSONFileProcessor:
    @staticmethod
    def generate_safe_filename(original_name):
        """Генерирует безопасное имя файла"""
        ext = 'json'
        filename = f"{uuid.uuid4().hex}.{ext}"
        return filename
    
    @staticmethod
    def validate_json_file(file_path):
        """Проверяет валидность JSON файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Проверяем структуру данных
            if isinstance(data, list):
                for item in data:
                    if not JSONFileProcessor._validate_photo_metadata(item):
                        return False, "Неверная структура данных в JSON файле"
            elif isinstance(data, dict):
                if not JSONFileProcessor._validate_photo_metadata(data):
                    return False, "Неверная структура данных в JSON файле"
            else:
                return False, "Неподдерживаемая структура JSON файла"
            
            return True, "Файл валиден"
        except json.JSONDecodeError as e:
            return False, f"Ошибка парсинга JSON: {str(e)}"
        except Exception as e:
            return False, f"Ошибка при проверке файла: {str(e)}"
    
    @staticmethod
    def _validate_photo_metadata(data):
        """Проверяет структуру метаданных фотографии"""
        required_fields = ['filename', 'format', 'file_size', 'width', 'height']
        
        if not isinstance(data, dict):
            return False
        
        for field in required_fields:
            if field not in data:
                return False
        
        return True
    
    @staticmethod
    def save_to_json(data, filename):
        """Сохраняет данные в JSON файл"""
        file_path = os.path.join('media', 'json_files', filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return file_path
    
    @staticmethod
    def read_json_file(file_path):
        """Читает JSON файл"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)