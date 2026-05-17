from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .forms import RegisterForm, LoginForm, ProfileUpdateForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('accounts:dashboard')
    else:
        form = RegisterForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('accounts:dashboard')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('accounts:login')


@login_required
def dashboard_view(request):
    from apps.projects.models import Project
    from apps.tasks.models import Task
    from apps.projects.utils import calculate_project_health
    from apps.tasks.utils import get_deadline_context
    
    # Get user's projects
    all_projects = Project.objects.filter(
        Q(owner=request.user) | Q(members=request.user)
    ).distinct().prefetch_related('tasks')
    
    projects = all_projects[:5]  # Limit to 5 recent projects
    
    # Get project counts
    total_projects = all_projects.count()
    
    # Calculate health scores for all projects
    healthy_projects = 0
    at_risk_projects = 0
    
    for project in all_projects:
        health = calculate_project_health(project)
        if health['score'] >= 70:
            healthy_projects += 1
        elif health['score'] < 40:
            at_risk_projects += 1
    
    # Get task statistics for tasks assigned to the user
    assigned_tasks = Task.objects.filter(assigned_to=request.user)
    total_tasks = assigned_tasks.count()
    completed_tasks = assigned_tasks.filter(status='completed').count()
    pending_tasks = assigned_tasks.filter(status='pending').count()
    
    # Get recent pending tasks
    recent_pending_tasks = assigned_tasks.filter(
        Q(status='pending') | Q(status='not_started')
    ).select_related('project', 'created_by')[:5]
    
    # Get deadline context for alerts
    deadline_context = get_deadline_context(request.user)
    
    context = {
        'projects': projects,
        'total_projects': total_projects,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'recent_pending_tasks': recent_pending_tasks,
        'healthy_projects': healthy_projects,
        'at_risk_projects': at_risk_projects,
        **deadline_context,  # Add deadline alerts context
    }
    
    return render(request, 'accounts/dashboard.html', context)


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'accounts/profile.html', {'form': form})


@login_required
def toast_demo_view(request):
    """Demo page for the toast notification system"""
    return render(request, 'accounts/toast_demo.html')

# Made with Bob
