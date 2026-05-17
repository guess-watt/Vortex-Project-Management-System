from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import models
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_http_methods
from .models import Project, ProjectMember
from .forms import ProjectForm, TaskFormSet, InviteMemberForm
from .services import BurndownChartService
from .utils import calculate_project_health
from apps.tasks.models import Task
from apps.ai.workload_service import WorkloadBalancerService

User = get_user_model()


@login_required
def project_list(request):
    projects = Project.objects.filter(
        models.Q(owner=request.user) | models.Q(members=request.user)
    ).distinct().prefetch_related('tasks')
    
    # Calculate health score for each project
    projects_with_health = []
    for project in projects:
        health = calculate_project_health(project)
        projects_with_health.append({
            'project': project,
            'health': health
        })
    
    # Get sort parameter (default: health score ascending - worst first)
    sort_by = request.GET.get('sort', 'health')
    
    if sort_by == 'name':
        projects_with_health.sort(key=lambda x: x['project'].name.lower())
    elif sort_by == 'date':
        projects_with_health.sort(key=lambda x: x['project'].created_at, reverse=True)
    else:  # sort by health (default)
        projects_with_health.sort(key=lambda x: x['health']['score'])
    
    # Calculate analytics for dashboard
    healthy_count = sum(1 for p in projects_with_health if p['health']['score'] >= 70)
    at_risk_count = sum(1 for p in projects_with_health if p['health']['score'] < 40)
    
    context = {
        'projects_with_health': projects_with_health,
        'sort_by': sort_by,
        'healthy_count': healthy_count,
        'at_risk_count': at_risk_count,
    }
    
    return render(request, 'projects/project_list.html', context)


@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    # Check if user has access
    if request.user != project.owner and request.user not in project.members.all():
        messages.error(request, 'You do not have access to this project.')
        return redirect('projects:project_list')
    return render(request, 'projects/project_detail.html', {'project': project})


@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        task_formset = TaskFormSet(request.POST, prefix='tasks')
        
        if form.is_valid() and task_formset.is_valid():
            # Save the project
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            form.save_m2m()  # Save many-to-many relationships
            
            # Create tasks for the project
            tasks_created = 0
            for task_form in task_formset:
                task_title = task_form.cleaned_data.get('title')
                if task_title:  # Only create task if title is provided
                    task_description = task_form.cleaned_data.get('description', '')
                    assigned_to_id = task_form.cleaned_data.get('assigned_to')
                    
                    # Get assigned user if provided
                    assigned_to = None
                    if assigned_to_id:
                        try:
                            assigned_to = User.objects.get(id=assigned_to_id)
                        except User.DoesNotExist:
                            pass
                    
                    # Create the task
                    Task.objects.create(
                        project=project,
                        title=task_title,
                        description=task_description,
                        assigned_to=assigned_to,
                        created_by=request.user,
                        status='not_started'
                    )
                    tasks_created += 1
            
            if tasks_created > 0:
                messages.success(request, f'Project created successfully with {tasks_created} task(s)!')
            else:
                messages.success(request, 'Project created successfully!')
            return redirect('projects:project_detail', pk=project.pk)
    else:
        form = ProjectForm()
        task_formset = TaskFormSet(prefix='tasks')
    
    return render(request, 'projects/project_form.html', {
        'form': form,
        'task_formset': task_formset,
        'action': 'Create'
    })


@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    # Only owner can edit
    if request.user != project.owner:
        messages.error(request, 'Only the project owner can edit this project.')
        return redirect('projects:project_detail', pk=project.pk)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully!')
            return redirect('projects:project_detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)
    return render(request, 'projects/project_form.html', {'form': form, 'action': 'Edit', 'project': project})


@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    # Only owner can delete
    if request.user != project.owner:
        messages.error(request, 'Only the project owner can delete this project.')
        return redirect('projects:project_detail', pk=project.pk)
    
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project deleted successfully!')
        return redirect('projects:project_list')
    return render(request, 'projects/project_detail.html', {'project': project})


@login_required
def project_kanban(request, pk):
    """Display Kanban board for a project"""
    project = get_object_or_404(Project, pk=pk)
    
    # Check if user has access
    if request.user != project.owner and request.user not in project.members.all():
        messages.error(request, 'You do not have access to this project.')
        return redirect('projects:project_list')
    
    # Get tasks organized by status
    tasks_not_started = project.tasks.filter(status='not_started').select_related('assigned_to', 'created_by')
    tasks_pending = project.tasks.filter(status='pending').select_related('assigned_to', 'created_by')
    tasks_completed = project.tasks.filter(status='completed').select_related('assigned_to', 'created_by')
    
    context = {
        'project': project,
        'tasks_not_started': tasks_not_started,
        'tasks_pending': tasks_pending,
        'tasks_completed': tasks_completed,
    }
    
    return render(request, 'projects/project_kanban.html', context)


@login_required
def kanban_update_status(request, pk):
    """Update task status via AJAX for Kanban board"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)
    
    task = get_object_or_404(Task, pk=pk)
    project = task.project
    
    # Check if user has access to the project
    if request.user != project.owner and request.user not in project.members.all():
        return JsonResponse({'success': False, 'error': 'Access denied'}, status=403)
    
    new_status = request.POST.get('status')
    
    # Validate status
    valid_statuses = dict(Task.STATUS_CHOICES).keys()
    if new_status not in valid_statuses:
        return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)
    
    # Update task status
    task.status = new_status
    task.save()
    
    return JsonResponse({
        'success': True,
        'task_id': str(task.id),
        'status': task.status,
        'status_display': task.get_status_display()
    })

@login_required
def project_burndown(request, pk):
    """Display burndown chart for a project"""
    project = get_object_or_404(Project, pk=pk)
    
    # Check if user has access
    if request.user != project.owner and request.user not in project.members.all():
        messages.error(request, 'You do not have access to this project.')
        return redirect('projects:project_list')
    
    # Get days parameter from query string (default: 14 days)
    days = request.GET.get('days', 14)
    try:
        days = int(days)
        if days < 7:
            days = 7
        elif days > 90:
            days = 90
    except (ValueError, TypeError):
        days = 14
    
    # Initialize burndown service
    burndown_service = BurndownChartService(project)
    
    # Get burndown data
    burndown_data = burndown_service.get_burndown_data(days=days)
    
    # Get additional analytics
    status_distribution = burndown_service.get_status_distribution()
    assignee_performance = burndown_service.get_assignee_performance()
    completion_timeline = burndown_service.get_task_completion_timeline()
    
    context = {
        'project': project,
        'burndown_data': burndown_data,
        'status_distribution': status_distribution,
        'assignee_performance': assignee_performance,
        'completion_timeline': completion_timeline,
        'selected_days': days,
    }
    
    return render(request, 'projects/project_burndown.html', context)


@login_required
def project_team(request, pk):
    """Display and manage project team members"""
    project = get_object_or_404(Project, pk=pk)
    
    # Check if user has access
    if request.user != project.owner and request.user not in project.members.all():
        messages.error(request, 'You do not have access to this project.')
        return redirect('projects:project_list')
    
    # Get all team members with their details
    team_members = project.project_members.select_related('user', 'invited_by').all()
    
    # Check if user can manage members
    can_manage = project.can_manage_members(request.user)
    
    context = {
        'project': project,
        'team_members': team_members,
        'can_manage': can_manage,
        'is_owner': request.user == project.owner,
    }
    
    return render(request, 'projects/project_team.html', context)


@login_required
def invite_member(request, pk):
    """Invite a new member to the project"""
    project = get_object_or_404(Project, pk=pk)
    
    # Check if user can manage members
    if not project.can_manage_members(request.user):
        messages.error(request, 'You do not have permission to invite members.')
        return redirect('projects:project_team', pk=project.pk)
    
    if request.method == 'POST':
        from .forms import InviteMemberForm
        form = InviteMemberForm(request.POST, project=project)
        
        if form.is_valid():
            user_id = form.cleaned_data['user_id']
            role = form.cleaned_data['role']
            
            try:
                user = User.objects.get(id=user_id)
                
                # Create ProjectMember
                from .models import ProjectMember
                ProjectMember.objects.create(
                    project=project,
                    user=user,
                    role=role,
                    invited_by=request.user
                )
                
                messages.success(
                    request,
                    f'{user.username} has been added to the project as {role}.'
                )
                return redirect('projects:project_team', pk=project.pk)
                
            except User.DoesNotExist:
                messages.error(request, 'User not found.')
            except Exception as e:
                messages.error(request, f'Error adding member: {str(e)}')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    
    return redirect('projects:project_team', pk=project.pk)


@login_required
def remove_member(request, pk, member_id):
    """Remove a member from the project"""
    project = get_object_or_404(Project, pk=pk)
    
    # Check if user can manage members
    if not project.can_manage_members(request.user):
        messages.error(request, 'You do not have permission to remove members.')
        return redirect('projects:project_team', pk=project.pk)
    
    if request.method == 'POST':
        from .models import ProjectMember
        
        try:
            member = ProjectMember.objects.get(id=member_id, project=project)
            
            # Cannot remove the owner
            if member.user == project.owner:
                messages.error(request, 'Cannot remove the project owner.')
                return redirect('projects:project_team', pk=project.pk)
            
            username = member.user.username
            member.delete()
            
            messages.success(request, f'{username} has been removed from the project.')
            
        except ProjectMember.DoesNotExist:
            messages.error(request, 'Member not found.')
    
    return redirect('projects:project_team', pk=project.pk)


@login_required
def update_member_role(request, pk, member_id):
    """Update a member's role in the project"""
    project = get_object_or_404(Project, pk=pk)
    
    # Only owner can change roles
    if request.user != project.owner:
        messages.error(request, 'Only the project owner can change member roles.')
        return redirect('projects:project_team', pk=project.pk)
    
    if request.method == 'POST':
        from .models import ProjectMember
        
        try:
            member = ProjectMember.objects.get(id=member_id, project=project)
            new_role = request.POST.get('role')
            
            if new_role in dict(ProjectMember.ROLE_CHOICES).keys():
                old_role = member.role
                member.role = new_role
                member.save()
                
                messages.success(
                    request,
                    f'{member.user.username}\'s role changed from {old_role} to {new_role}.'
                )
            else:
                messages.error(request, 'Invalid role selected.')
                
        except ProjectMember.DoesNotExist:
            messages.error(request, 'Member not found.')
    
    return redirect('projects:project_team', pk=project.pk)


@login_required
def search_users(request):
    """AJAX endpoint to search for users to invite"""
    query = request.GET.get('q', '').strip()
    project_id = request.GET.get('project_id')
    
    if not query or len(query) < 2:
        return JsonResponse({'users': []})
    
    try:
        project = Project.objects.get(pk=project_id)
        
        # Check if user can manage members
        if not project.can_manage_members(request.user):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        # Search for users by email or username
        users = User.objects.filter(
            models.Q(email__icontains=query) | models.Q(username__icontains=query)
        ).exclude(
            id=project.owner.id
        ).exclude(
            id__in=project.members.values_list('id', flat=True)
        )[:10]
        
        user_list = [
            {
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'full_name': user.get_full_name() or user.username
            }
            for user in users
        ]
        
        return JsonResponse({'users': user_list})
        
    except Project.DoesNotExist:
        return JsonResponse({'error': 'Project not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Made with Bob


@login_required
@require_http_methods(["POST"])
def workload_balance(request, pk):
    """
    AI-powered workload balancing endpoint
    Analyzes team workload and suggests optimal task assignments
    """
    project = get_object_or_404(Project, pk=pk)
    
    # Check if user has access and can manage tasks
    if not project.can_manage_members(request.user):
        return JsonResponse({
            'success': False,
            'error': 'You do not have permission to manage team workload'
        }, status=403)
    
    try:
        # Initialize workload balancer service
        balancer = WorkloadBalancerService()
        
        # Get AI suggestions
        result = balancer.balance_workload(project)
        
        if result['success']:
            return JsonResponse({
                'success': True,
                'suggestions': result.get('suggestions', []),
                'team_data': result.get('team_data', []),
                'unassigned_count': result.get('unassigned_count', 0),
                'message': result.get('message', 'Workload analysis complete')
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result.get('error', 'Failed to analyze workload')
            }, status=500)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error analyzing workload: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def assign_task_to_member(request, pk):
    """
    Assign a specific task to a team member
    Used by the AI workload balancer UI
    """
    project = get_object_or_404(Project, pk=pk)
    
    # Check if user has access and can manage tasks
    if not project.can_manage_tasks(request.user):
        return JsonResponse({
            'success': False,
            'error': 'You do not have permission to assign tasks'
        }, status=403)
    
    try:
        task_id = request.POST.get('task_id')
        user_id = request.POST.get('user_id')
        
        if not task_id or not user_id:
            return JsonResponse({
                'success': False,
                'error': 'Missing task_id or user_id'
            }, status=400)
        
        # Get the task
        task = get_object_or_404(Task, id=task_id, project=project)
        
        # Get the user
        user = get_object_or_404(User, id=user_id)
        
        # Verify user is a team member
        if user != project.owner and user not in project.members.all():
            return JsonResponse({
                'success': False,
                'error': 'User is not a member of this project'
            }, status=400)
        
        # Assign the task
        task.assigned_to = user
        task.save()
        
        return JsonResponse({
            'success': True,
            'task_id': str(task.id),
            'task_title': task.title,
            'assigned_to': user.username,
            'message': f'Task assigned to {user.username}'
        })
        
    except Task.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Task not found'
        }, status=404)
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'User not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error assigning task: {str(e)}'
        }, status=500)

# Made with Bob
