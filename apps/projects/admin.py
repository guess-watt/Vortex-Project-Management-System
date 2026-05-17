from django.contrib import admin
from .models import Project, ProjectMember


class ProjectMemberInline(admin.TabularInline):
    model = ProjectMember
    extra = 1
    fields = ['user', 'role', 'joined_at', 'invited_by']
    readonly_fields = ['joined_at']
    autocomplete_fields = ['user', 'invited_by']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['name', 'description', 'owner__email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [ProjectMemberInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'description')
        }),
        ('Ownership', {
            'fields': ('owner',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'project', 'role', 'joined_at']
    list_filter = ['role', 'joined_at']
    search_fields = ['user__email', 'user__username', 'project__name']
    readonly_fields = ['id', 'joined_at']
    autocomplete_fields = ['user', 'project', 'invited_by']
    
    fieldsets = (
        ('Member Information', {
            'fields': ('id', 'user', 'project', 'role')
        }),
        ('Invitation Details', {
            'fields': ('invited_by', 'joined_at')
        }),
    )

# Made with Bob
