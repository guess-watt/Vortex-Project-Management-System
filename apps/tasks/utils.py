from django.utils import timezone
from datetime import timedelta
from .models import Task


def get_deadline_context(user):
    """
    Get deadline-related context for a user's tasks.
    
    Returns a dictionary with:
    - overdue_tasks: queryset of user's overdue tasks
    - due_today_tasks: queryset of tasks due today
    - due_soon_tasks: queryset of tasks due tomorrow
    - overdue_count: count of overdue tasks
    - due_today_count: count of tasks due today
    - due_soon_count: count of tasks due tomorrow
    """
    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)
    
    # Get all tasks assigned to the user
    user_tasks = Task.objects.filter(assigned_to=user).select_related('project', 'created_by')
    
    # Overdue tasks (due_date < today and status is overdue)
    overdue_tasks = user_tasks.filter(
        due_date__lt=today,
        status='overdue'
    ).order_by('due_date')
    
    # Tasks due today
    due_today_tasks = user_tasks.filter(
        due_date=today
    ).exclude(status__in=['done', 'completed']).order_by('priority')
    
    # Tasks due tomorrow
    due_soon_tasks = user_tasks.filter(
        due_date=tomorrow
    ).exclude(status__in=['done', 'completed']).order_by('priority')
    
    return {
        'overdue_tasks': overdue_tasks,
        'due_today_tasks': due_today_tasks,
        'due_soon_tasks': due_soon_tasks,
        'overdue_count': overdue_tasks.count(),
        'due_today_count': due_today_tasks.count(),
        'due_soon_count': due_soon_tasks.count(),
    }


def get_days_overdue(task):
    """
    Calculate how many days a task is overdue.
    Returns 0 if not overdue.
    """
    if not task.due_date:
        return 0
    
    today = timezone.now().date()
    if task.due_date < today:
        return (today - task.due_date).days
    return 0

# Made with Bob
