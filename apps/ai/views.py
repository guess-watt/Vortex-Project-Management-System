from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from apps.projects.models import Project
from apps.tasks.models import Task
from .forms import AITaskGenerationForm
from .services import AITaskGenerator


@login_required
def generate_tasks_view(request, project_pk):
    """View for AI task generation page"""
    project = get_object_or_404(Project, pk=project_pk)
    
    # Check if user has access to the project
    if request.user != project.owner and request.user not in project.members.all():
        messages.error(request, 'You do not have access to this project.')
        return redirect('projects:project_list')
    
    if request.method == 'POST':
        form = AITaskGenerationForm(request.POST)
        if form.is_valid():
            project_description = form.cleaned_data['project_description']
            num_tasks = form.cleaned_data['num_tasks']
            
            try:
                # Generate tasks using AI
                ai_generator = AITaskGenerator()
                generated_tasks = ai_generator.generate_tasks(
                    project_description=project_description,
                    num_tasks=num_tasks
                )
                
                # Store generated tasks in session for preview
                request.session['generated_tasks'] = generated_tasks
                request.session['project_pk'] = str(project.pk)
                
                messages.success(
                    request, 
                    f'Successfully generated {len(generated_tasks)} tasks! Review and save them below.'
                )
                return redirect('ai:preview_tasks', project_pk=project.pk)
                
            except ValueError as e:
                messages.error(request, f'Configuration error: {str(e)}')
            except Exception as e:
                messages.error(request, f'Error generating tasks: {str(e)}')
    else:
        # Pre-fill with project description if available
        initial_data = {}
        if project.description:
            initial_data['project_description'] = project.description
        form = AITaskGenerationForm(initial=initial_data)
    
    context = {
        'form': form,
        'project': project,
    }
    return render(request, 'ai/generate_tasks.html', context)


@login_required
def preview_tasks_view(request, project_pk):
    """View for previewing and saving generated tasks"""
    project = get_object_or_404(Project, pk=project_pk)
    
    # Check if user has access to the project
    if request.user != project.owner and request.user not in project.members.all():
        messages.error(request, 'You do not have access to this project.')
        return redirect('projects:project_list')
    
    # Get generated tasks from session
    generated_tasks = request.session.get('generated_tasks', [])
    session_project_pk = request.session.get('project_pk')
    
    # Verify session data matches current project
    if not generated_tasks or session_project_pk != str(project.pk):
        messages.warning(request, 'No generated tasks found. Please generate tasks first.')
        return redirect('ai:generate_tasks', project_pk=project.pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'save_all':
            # Save all generated tasks to database
            tasks_created = 0
            for task_data in generated_tasks:
                Task.objects.create(
                    project=project,
                    title=task_data['title'],
                    description=task_data['description'],
                    status=task_data['status'],
                    created_by=request.user,
                    assigned_to=None  # Can be assigned later
                )
                tasks_created += 1
            
            # Clear session data
            request.session.pop('generated_tasks', None)
            request.session.pop('project_pk', None)
            
            messages.success(
                request, 
                f'Successfully created {tasks_created} tasks for {project.name}!'
            )
            return redirect('projects:project_detail', pk=project.pk)
        
        elif action == 'regenerate':
            # Clear session and go back to generation page
            request.session.pop('generated_tasks', None)
            request.session.pop('project_pk', None)
            messages.info(request, 'Generate new tasks with different parameters.')
            return redirect('ai:generate_tasks', project_pk=project.pk)
    
    context = {
        'project': project,
        'generated_tasks': generated_tasks,
    }
    return render(request, 'ai/preview_tasks.html', context)


@login_required
@require_http_methods(["POST"])
def remove_task_ajax(request, project_pk):
    """AJAX endpoint to remove a task from preview"""
    try:
        task_index = int(request.POST.get('task_index', -1))
        generated_tasks = request.session.get('generated_tasks', [])
        
        if 0 <= task_index < len(generated_tasks):
            removed_task = generated_tasks.pop(task_index)
            request.session['generated_tasks'] = generated_tasks
            request.session.modified = True
            
            return JsonResponse({
                'success': True,
                'message': f'Removed task: {removed_task["title"]}',
                'remaining_count': len(generated_tasks)
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Invalid task index'
            }, status=400)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# Made with Bob
