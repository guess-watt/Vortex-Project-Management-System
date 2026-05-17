from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.tasks.models import Task


class Command(BaseCommand):
    help = 'Check all tasks for overdue deadlines and update their status'

    def handle(self, *args, **options):
        """
        Scans all tasks where due_date < today and status not in ['done', 'completed', 'overdue']
        and bulk updates their status to 'overdue'.
        """
        today = timezone.now().date()
        
        # Find tasks that are overdue but not marked as such
        overdue_tasks = Task.objects.filter(
            due_date__lt=today
        ).exclude(
            status__in=['done', 'completed', 'overdue']
        )
        
        count = overdue_tasks.count()
        
        if count > 0:
            # Bulk update to overdue status
            overdue_tasks.update(status='overdue')
            self.stdout.write(
                self.style.SUCCESS(f'[OK] {count} task(s) marked as overdue')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('[OK] No tasks need to be marked as overdue')
            )
        
        return f'{count} tasks marked overdue'

# Made with Bob
