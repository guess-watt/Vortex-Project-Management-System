import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField()
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_projects'
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ProjectMember',
        through_fields=('project', 'user'),
        related_name='projects',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name
    
    def get_member_role(self, user):
        """Get the role of a user in this project"""
        if user == self.owner:
            return 'owner'
        try:
            member = self.projectmember_set.get(user=user)
            return member.role
        except ProjectMember.DoesNotExist:
            return None
    
    def is_admin(self, user):
        """Check if user is owner or admin"""
        if user == self.owner:
            return True
        role = self.get_member_role(user)
        return role == 'admin'
    
    def can_manage_members(self, user):
        """Check if user can manage members (owner or admin)"""
        return self.is_admin(user)
    
    def can_manage_tasks(self, user):
        """Check if user can manage tasks (owner, admin, or member)"""
        if user == self.owner:
            return True
        role = self.get_member_role(user)
        return role in ['admin', 'member']


class ProjectMember(models.Model):
    """Through model for Project-User relationship with roles"""
    
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('member', 'Member'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='project_members'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='project_memberships'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='member'
    )
    joined_at = models.DateTimeField(default=timezone.now)
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invited_members'
    )
    
    class Meta:
        unique_together = ['project', 'user']
        ordering = ['-joined_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.project.name} ({self.role})"
    
    def get_assigned_tasks_count(self):
        """Get count of tasks assigned to this member"""
        return self.user.assigned_tasks.filter(project=self.project).count()

# Made with Bob
