from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.project_list, name='project_list'),
    path('create/', views.project_create, name='project_create'),
    path('<uuid:pk>/', views.project_detail, name='project_detail'),
    path('<uuid:pk>/edit/', views.project_edit, name='project_edit'),
    path('<uuid:pk>/delete/', views.project_delete, name='project_delete'),
    path('<uuid:pk>/kanban/', views.project_kanban, name='project_kanban'),
    path('<uuid:pk>/burndown/', views.project_burndown, name='project_burndown'),
    path('<uuid:pk>/team/', views.project_team, name='project_team'),
    path('<uuid:pk>/team/invite/', views.invite_member, name='invite_member'),
    path('<uuid:pk>/team/remove/<uuid:member_id>/', views.remove_member, name='remove_member'),
    path('<uuid:pk>/team/update-role/<uuid:member_id>/', views.update_member_role, name='update_member_role'),
    path('search-users/', views.search_users, name='search_users'),
    path('kanban/<uuid:pk>/update-status/', views.kanban_update_status, name='kanban_update_status'),
    path('<uuid:pk>/workload-balance/', views.workload_balance, name='workload_balance'),
    path('<uuid:pk>/assign-task/', views.assign_task_to_member, name='assign_task_to_member'),
]

# Made with Bob
