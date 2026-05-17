from django import forms


class AITaskGenerationForm(forms.Form):
    """Form for AI task generation"""
    
    project_description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 6,
            'placeholder': 'Describe your project or feature in detail...\n\nExample: "Build an e-commerce website with user authentication, product catalog, shopping cart, payment integration, and order management system."',
        }),
        label='Project Description',
        help_text='Provide a detailed description of your project or feature. The more specific you are, the better the AI can generate relevant tasks.',
        max_length=2000
    )
    
    num_tasks = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 3,
            'max': 15,
            'value': 5
        }),
        label='Number of Tasks',
        help_text='How many tasks should the AI generate? (3-15)',
        min_value=3,
        max_value=15,
        initial=5
    )

# Made with Bob