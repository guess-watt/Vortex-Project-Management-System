from django import forms
from django.contrib.auth import get_user_model
from .models import Project, ProjectMember

User = get_user_model()


class ProjectForm(forms.ModelForm):
    """Form for creating and editing projects"""
    
    class Meta:
        model = Project
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter project name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your project'
            }),
        }


class InviteMemberForm(forms.Form):
    """Form for inviting members to a project"""
    
    user_search = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by email or username',
            'id': 'user-search-input'
        }),
        label='Search User'
    )
    
    user_id = forms.UUIDField(
        required=True,
        widget=forms.HiddenInput(attrs={
            'id': 'selected-user-id'
        })
    )
    
    role = forms.ChoiceField(
        choices=ProjectMember.ROLE_CHOICES,
        initial='member',
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Role'
    )
    
    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.project = project
    
    def clean_user_id(self):
        user_id = self.cleaned_data.get('user_id')
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise forms.ValidationError('Selected user does not exist.')
        
        # Check if user is already a member
        if self.project:
            if user == self.project.owner:
                raise forms.ValidationError('This user is the project owner.')
            
            if ProjectMember.objects.filter(project=self.project, user=user).exists():
                raise forms.ValidationError('This user is already a member of the project.')
        
        return user_id


class UpdateMemberRoleForm(forms.ModelForm):
    """Form for updating a member's role"""
    
    class Meta:
        model = ProjectMember
        fields = ['role']
        widgets = {
            'role': forms.Select(attrs={
                'class': 'form-select form-select-sm'
            })
        }


class TaskFormSet(forms.BaseFormSet):
    """Formset for creating multiple tasks when creating a project"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.forms:
            for field_name, field in form.fields.items():
                if field_name == 'title':
                    field.widget.attrs.update({
                        'class': 'form-control',
                        'placeholder': 'Task title'
                    })
                elif field_name == 'description':
                    field.widget.attrs.update({
                        'class': 'form-control',
                        'rows': 2,
                        'placeholder': 'Task description (optional)'
                    })
                elif field_name == 'assigned_to':
                    field.widget.attrs.update({
                        'class': 'form-select'
                    })


# Create the formset
TaskFormSet = forms.formset_factory(
    forms.Form,
    formset=TaskFormSet,
    extra=3,
    max_num=10
)

# Made with Bob
