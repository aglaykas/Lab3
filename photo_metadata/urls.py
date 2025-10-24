
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('input/', views.input_form, name='input_form'),
    path('upload/', views.upload_file, name='upload_file'),
    path('files/', views.view_files, name='view_files'),  
    path('files/<str:filename>/', views.view_file_content, name='view_file_content'),
    path('database/', views.view_database_records, name='database_records'),
    path('edit/<int:record_id>/', views.edit_record, name='edit_record'),
    path('delete/<int:record_id>/', views.delete_record, name='delete_record'),
    path('search/', views.search_records, name='search_records'),
]