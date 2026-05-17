#!/usr/bin/env python
"""Test script to create overdue tasks and verify the deadline system"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.tasks.models import Task
from apps.projects.models import Project
from apps.accounts.models import User
from datetime import date, timedelta

# Get first user and project
user = User.objects.first()
project = Project.objects.first()

if not user or not project:
    print("ERROR: No user or project found in database")
    exit(1)

print(f"Using user: {user.username}")
print(f"Using project: {project.name}")
print()

# Create test tasks with different due dates
test_tasks = [
    {
        'title': 'Overdue Task 1',
        'description': 'This task is 5 days overdue',
        'due_date': date.today() - timedelta(days=5),
        'status': 'pending'
    },
    {
        'title': 'Overdue Task 2',
        'description': 'This task is 10 days overdue',
        'due_date': date.today() - timedelta(days=10),
        'status': 'not_started'
    },
    {
        'title': 'Due Today Task',
        'description': 'This task is due today',
        'due_date': date.today(),
        'status': 'pending'
    },
    {
        'title': 'Due Tomorrow Task',
        'description': 'This task is due tomorrow',
        'due_date': date.today() + timedelta(days=1),
        'status': 'not_started'
    },
]

print("Creating test tasks...")
created_tasks = []
for task_data in test_tasks:
    task = Task.objects.create(
        title=task_data['title'],
        description=task_data['description'],
        project=project,
        created_by=user,
        assigned_to=user,
        status=task_data['status'],
        due_date=task_data['due_date']
    )
    created_tasks.append(task)
    print(f"[OK] Created: {task.title} | Due: {task.due_date} | Status: {task.status}")

print()
print("=" * 60)
print("Now run: python manage.py check_deadlines")
print("=" * 60)

# Made with Bob
