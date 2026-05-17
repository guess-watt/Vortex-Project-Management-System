from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Task
from .forms import TaskForm
from apps.projects.models import Project


@login_required
def task_create(request, project_pk):
    """Create a new task for a project"""
    project = get_object_or_404(Project, pk=project_pk)
    
    # Check if user has access to the project
    if request.user != project.owner and request.user not in project.members.all():
        messages.error(request, 'You do not have access to this project.')
        return redirect('projects:project_list')
    
    if request.method == 'POST':
        form = TaskForm(request.POST, project=project)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.created_by = request.user
            task.save()
            messages.success(request, 'Task created successfully!')
            return redirect('projects:project_detail', pk=project.pk)
    else:
        form = TaskForm(project=project)
    
    return render(request, 'tasks/task_form.html', {
        'form': form,
        'project': project,
        'action': 'Create'
    })


@login_required
def task_edit(request, pk):
    """Edit an existing task"""
    task = get_object_or_404(Task, pk=pk)
    project = task.project
    
    # Check if user has access to the project
    if request.user != project.owner and request.user not in project.members.all():
        messages.error(request, 'You do not have access to this project.')
        return redirect('projects:project_list')
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, project=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully!')
            return redirect('projects:project_detail', pk=project.pk)
    else:
        form = TaskForm(instance=task, project=project)
    
    return render(request, 'tasks/task_form.html', {
        'form': form,
        'project': project,
        'task': task,
        'action': 'Edit'
    })


@login_required
def task_delete(request, pk):
    """Delete a task"""
    task = get_object_or_404(Task, pk=pk)
    project = task.project
    
    # Check if user has access to the project
    if request.user != project.owner and request.user not in project.members.all():
        messages.error(request, 'You do not have access to this project.')
        return redirect('projects:project_list')
    
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted successfully!')
        return redirect('projects:project_detail', pk=project.pk)
    
    return render(request, 'tasks/task_confirm_delete.html', {
        'task': task,
        'project': project
    })


@login_required
def task_update_status(request, pk):
    """Update task status via AJAX"""
    if request.method == 'POST':
        task = get_object_or_404(Task, pk=pk)
        project = task.project
        
        # Check if user has access to the project
        if request.user != project.owner and request.user not in project.members.all():
            return JsonResponse({'success': False, 'error': 'Access denied'}, status=403)
        
        new_status = request.POST.get('status')
        if new_status in dict(Task.STATUS_CHOICES):
            task.status = new_status
            task.save()
            return JsonResponse({
                'success': True,
                'status': task.get_status_display()
            })
        
        return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

# Made with Bob

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import Task
from .forms import TaskForm
from apps.projects.models import Project


@login_required
def task_list(request):
    """View all tasks assigned to the logged-in user"""
    # Get filter parameter
    status_filter = request.GET.get('status', 'all')
    
    # Base queryset - tasks assigned to user
    tasks = Task.objects.filter(assigned_to=request.user).select_related('project', 'created_by')
    
    # Apply status filter
    if status_filter == 'pending':
        tasks = tasks.filter(status='pending')
    elif status_filter == 'not_started':
        tasks = tasks.filter(status='not_started')
    elif status_filter == 'completed':
        tasks = tasks.filter(status='completed')
    
    # Get counts for each status
    all_count = Task.objects.filter(assigned_to=request.user).count()
    pending_count = Task.objects.filter(assigned_to=request.user, status='pending').count()
    not_started_count = Task.objects.filter(assigned_to=request.user, status='not_started').count()
    completed_count = Task.objects.filter(assigned_to=request.user, status='completed').count()
    
    context = {
        'tasks': tasks,
        'status_filter': status_filter,
        'all_count': all_count,
        'pending_count': pending_count,
        'not_started_count': not_started_count,
        'completed_count': completed_count,
    }
    
    return render(request, 'tasks/task_list.html', context)

