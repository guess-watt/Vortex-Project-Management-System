from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from .models import Task


@receiver(post_save, sender=Task)
def check_task_deadline(sender, instance, created, **kwargs):
    """
    Signal to automatically update task status based on due_date.
    Checks if task is overdue and updates status accordingly.
    """
    # Avoid recursive signal calls
    if kwargs.get('update_fields') and 'status' in kwargs.get('update_fields', []):
        return
    
    # Only process if task has a due_date
    if not instance.due_date:
        return
    
    # Get today's date (without time component)
    today = timezone.now().date()
    
    # Check if task is overdue (due_date < today and not done/completed)
    if instance.due_date < today and instance.status not in ['done', 'completed', 'overdue']:
        # Update status to overdue without triggering signal again
        Task.objects.filter(pk=instance.pk).update(status='overdue')

# Made with Bob
