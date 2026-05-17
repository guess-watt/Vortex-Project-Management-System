"""
Burndown Chart Service
Provides analytics and data calculation for project burndown charts
"""
from datetime import datetime, timedelta
from django.db.models import Count, Q
from django.utils import timezone
from apps.tasks.models import Task


class BurndownChartService:
    """Service class for calculating burndown chart data"""
    
    def __init__(self, project):
        self.project = project
        
    def get_burndown_data(self, days=14):
        """
        Calculate burndown chart data for the specified number of days
        
        Args:
            days: Number of days to include in the burndown chart (default: 14)
            
        Returns:
            dict: Contains labels, ideal_line, actual_line, and statistics
        """
        # Get project start date (earliest task creation or project creation)
        earliest_task = self.project.tasks.order_by('created_at').first()
        if earliest_task:
            start_date = min(earliest_task.created_at.date(), self.project.created_at.date())
        else:
            start_date = self.project.created_at.date()
        
        # Calculate date range
        end_date = timezone.now().date()
        
        # If days parameter is provided, use it to limit the range
        if days:
            start_date = max(start_date, end_date - timedelta(days=days-1))
        
        # Generate date labels
        date_labels = []
        current_date = start_date
        while current_date <= end_date:
            date_labels.append(current_date)
            current_date += timedelta(days=1)
        
        # Get total tasks at start
        total_tasks = self.project.tasks.count()
        
        # Calculate ideal burndown line (linear decrease)
        ideal_line = []
        if len(date_labels) > 1:
            daily_decrease = total_tasks / (len(date_labels) - 1)
            for i in range(len(date_labels)):
                ideal_line.append(max(0, total_tasks - (i * daily_decrease)))
        else:
            ideal_line = [total_tasks]
        
        # Calculate actual burndown line (remaining tasks per day)
        actual_line = []
        for date in date_labels:
            # Count tasks that were NOT completed by this date
            remaining_tasks = self.project.tasks.filter(
                Q(status__in=['not_started', 'pending']) |
                Q(status='completed', updated_at__date__gt=date)
            ).filter(created_at__date__lte=date).count()
            
            actual_line.append(remaining_tasks)
        
        # Calculate statistics
        completed_tasks = self.project.tasks.filter(status='completed').count()
        pending_tasks = self.project.tasks.filter(status='pending').count()
        not_started_tasks = self.project.tasks.filter(status='not_started').count()
        
        completion_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Calculate velocity (tasks completed per day)
        days_elapsed = (end_date - start_date).days + 1
        velocity = completed_tasks / days_elapsed if days_elapsed > 0 else 0
        
        # Estimate completion date based on current velocity
        remaining_tasks = not_started_tasks + pending_tasks
        estimated_days_remaining = remaining_tasks / velocity if velocity > 0 else None
        estimated_completion_date = None
        if estimated_days_remaining:
            estimated_completion_date = end_date + timedelta(days=int(estimated_days_remaining))
        
        return {
            'labels': [date.strftime('%b %d') for date in date_labels],
            'dates': [date.isoformat() for date in date_labels],
            'ideal_line': [round(val, 1) for val in ideal_line],
            'actual_line': actual_line,
            'statistics': {
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'pending_tasks': pending_tasks,
                'not_started_tasks': not_started_tasks,
                'remaining_tasks': remaining_tasks,
                'completion_percentage': round(completion_percentage, 1),
                'velocity': round(velocity, 2),
                'estimated_completion_date': estimated_completion_date.strftime('%b %d, %Y') if estimated_completion_date else 'N/A',
                'days_elapsed': days_elapsed,
                'start_date': start_date.strftime('%b %d, %Y'),
                'current_date': end_date.strftime('%b %d, %Y'),
            }
        }
    
    def get_task_completion_timeline(self):
        """
        Get timeline of task completions
        
        Returns:
            list: List of dicts with date and count of completed tasks
        """
        completed_tasks = self.project.tasks.filter(
            status='completed'
        ).values('updated_at__date').annotate(
            count=Count('id')
        ).order_by('updated_at__date')
        
        return [
            {
                'date': item['updated_at__date'].strftime('%b %d, %Y'),
                'count': item['count']
            }
            for item in completed_tasks
        ]
    
    def get_status_distribution(self):
        """
        Get distribution of tasks by status
        
        Returns:
            dict: Count of tasks for each status
        """
        status_counts = self.project.tasks.values('status').annotate(
            count=Count('id')
        )
        
        distribution = {
            'not_started': 0,
            'pending': 0,
            'completed': 0
        }
        
        for item in status_counts:
            distribution[item['status']] = item['count']
        
        return distribution
    
    def get_assignee_performance(self):
        """
        Get performance metrics for each assignee
        
        Returns:
            list: List of dicts with assignee info and task counts
        """
        assignees = self.project.tasks.exclude(
            assigned_to__isnull=True
        ).values(
            'assigned_to__username',
            'assigned_to__email'
        ).annotate(
            total=Count('id'),
            completed=Count('id', filter=Q(status='completed')),
            pending=Count('id', filter=Q(status='pending')),
            not_started=Count('id', filter=Q(status='not_started'))
        ).order_by('-completed')
        
        return [
            {
                'username': item['assigned_to__username'],
                'email': item['assigned_to__email'],
                'total': item['total'],
                'completed': item['completed'],
                'pending': item['pending'],
                'not_started': item['not_started'],
                'completion_rate': round(item['completed'] / item['total'] * 100, 1) if item['total'] > 0 else 0
            }
            for item in assignees
        ]

# Made with Bob
