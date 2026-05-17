from django.urls import path
from . import views

app_name = 'ai'

urlpatterns = [
    path('projects/<uuid:project_pk>/generate/', views.generate_tasks_view, name='generate_tasks'),
    path('projects/<uuid:project_pk>/preview/', views.preview_tasks_view, name='preview_tasks'),
    path('projects/<uuid:project_pk>/remove-task/', views.remove_task_ajax, name='remove_task_ajax'),
]

# Made with Bob
