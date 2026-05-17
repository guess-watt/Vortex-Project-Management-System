# Generated migration for ProjectMember model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


def migrate_existing_members(apps, schema_editor):
    """Migrate existing project members to ProjectMember model"""
    Project = apps.get_model('projects', 'Project')
    ProjectMember = apps.get_model('projects', 'ProjectMember')
    
    for project in Project.objects.all():
        # Get existing members through the old M2M relationship
        for user in project.members.all():
            # Create ProjectMember entry with default 'member' role
            ProjectMember.objects.get_or_create(
                project=project,
                user=user,
                defaults={
                    'role': 'member',
                    'joined_at': django.utils.timezone.now(),
                    'invited_by': project.owner
                }
            )


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0001_initial'),
    ]

    operations = [
        # Step 1: Create ProjectMember model
        migrations.CreateModel(
            name='ProjectMember',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('role', models.CharField(choices=[('admin', 'Admin'), ('member', 'Member')], default='member', max_length=20)),
                ('joined_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('invited_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='invited_members', to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_members', to='projects.project')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_memberships', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-joined_at'],
                'unique_together': {('project', 'user')},
            },
        ),
        
        # Step 2: Migrate existing data
        migrations.RunPython(migrate_existing_members, reverse_code=migrations.RunPython.noop),
        
        # Step 3: Remove old M2M field
        migrations.RemoveField(
            model_name='project',
            name='members',
        ),
        
        # Step 4: Add new M2M field with through model
        migrations.AddField(
            model_name='project',
            name='members',
            field=models.ManyToManyField(blank=True, related_name='projects', through='projects.ProjectMember', through_fields=('project', 'user'), to=settings.AUTH_USER_MODEL),
        ),
    ]

# Made with Bob
