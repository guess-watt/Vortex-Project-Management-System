from django import forms
from .models import Task


class TaskForm(forms.ModelForm):
    """Form for creating and editing tasks"""
    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'status']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter task title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter task description (optional)'
            }),
            'assigned_to': forms.Select(attrs={
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)
        
        # Set assigned_to choices based on project members
        if project:
            # Include project owner and members
            users = [project.owner] + list(project.members.all())
            self.fields['assigned_to'].queryset = self.fields['assigned_to'].queryset.filter(
                id__in=[u.id for u in users]
            )
            self.fields['assigned_to'].empty_label = "-- Unassigned --"

# Made with Bob