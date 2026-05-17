from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('', views.task_list, name='task_list'),
    path('project/<uuid:project_pk>/create/', views.task_create, name='task_create'),
    path('<uuid:pk>/edit/', views.task_edit, name='task_edit'),
    path('<uuid:pk>/delete/', views.task_delete, name='task_delete'),
    path('<uuid:pk>/update-status/', views.task_update_status, name='task_update_status'),
]

# Made with Bob
