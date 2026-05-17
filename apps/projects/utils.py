from datetime import datetime, timedelta
from django.utils import timezone


def calculate_project_health(project):
    """
    Calculate project health score (0-100) based on task metrics.
    
    Returns:
        dict: {
            'score': int (0-100),
            'label': str ('Excellent', 'Stable', 'Risky', 'Critical'),
            'color': str ('green', 'yellow', 'red'),
            'emoji': str ('🟢', '🟡', '🔴'),
            'breakdown': dict with score components
        }
    """
    tasks = project.tasks.all()
    total_tasks = tasks.count()
    
    # Initialize score and breakdown
    score = 0
    breakdown = {
        'tasks_done': 0,
        'no_overdue': 0,
        'all_assigned': 0,
        'overdue_penalty': 0,
        'recent_activity': 0,
    }
    
    if total_tasks == 0:
        # No tasks means neutral health
        return {
            'score': 50,
            'label': 'Risky',
            'color': 'yellow',
            'emoji': '🟡',
            'breakdown': breakdown
        }
    
    # Get current date (timezone aware)
    today = timezone.now().date()
    
    # 1. +40 if more than 50% of tasks are 'done'
    done_tasks = tasks.filter(status='done').count()
    done_percentage = (done_tasks / total_tasks) * 100
    if done_percentage > 50:
        score += 40
        breakdown['tasks_done'] = 40
    
    # 2. +30 if no tasks are overdue (due_date < today and status != 'done')
    overdue_tasks = tasks.filter(
        due_date__lt=today
    ).exclude(status='done').count()
    
    if overdue_tasks == 0:
        score += 30
        breakdown['no_overdue'] = 30
    
    # 3. +30 if all tasks have assigned_to set (not null)
    unassigned_tasks = tasks.filter(assigned_to__isnull=True).count()
    if unassigned_tasks == 0:
        score += 30
        breakdown['all_assigned'] = 30
    
    # 4. -10 for each high-priority or urgent overdue task (max -30)
    high_priority_overdue = tasks.filter(
        due_date__lt=today,
        priority__in=['high', 'urgent']
    ).exclude(status='done').count()
    
    penalty = min(high_priority_overdue * 10, 30)
    score -= penalty
    breakdown['overdue_penalty'] = -penalty
    
    # 5. +5 bonus if any task was updated in the last 48 hours
    two_days_ago = timezone.now() - timedelta(hours=48)
    recent_updates = tasks.filter(updated_at__gte=two_days_ago).exists()
    if recent_updates:
        score += 5
        breakdown['recent_activity'] = 5
    
    # Ensure score is within 0-100 range
    score = max(0, min(100, score))
    
    # Determine label, color, and emoji
    if score >= 85:
        label = 'Excellent'
        color = 'green'
        emoji = '🟢'
    elif score >= 70:
        label = 'Stable'
        color = 'green'
        emoji = '🟢'
    elif score >= 40:
        label = 'Risky'
        color = 'yellow'
        emoji = '🟡'
    else:
        label = 'Critical'
        color = 'red'
        emoji = '🔴'
    
    return {
        'score': score,
        'label': label,
        'color': color,
        'emoji': emoji,
        'breakdown': breakdown,
        'total_tasks': total_tasks,
        'done_tasks': done_tasks,
        'overdue_tasks': overdue_tasks,
        'unassigned_tasks': unassigned_tasks,
        'high_priority_overdue': high_priority_overdue,
    }


# Made with Bob