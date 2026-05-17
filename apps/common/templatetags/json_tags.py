"""
Custom template tags for JSON serialization
"""
import json
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name='safe_json')
def safe_json(value):
    """
    Convert Django messages to JSON format for JavaScript consumption.
    
    Usage in template:
        {{ messages|safe_json }}
    
    This filter serializes Django messages into a JSON array that can be
    safely embedded in HTML data attributes and parsed by JavaScript.
    """
    if not value:
        return mark_safe('[]')
    
    # Convert messages to a list of dictionaries
    messages_list = []
    for message in value:
        messages_list.append({
            'message': str(message),
            'tags': message.tags if hasattr(message, 'tags') else 'info',
            'level': message.level if hasattr(message, 'level') else 20,
        })
    
    # Serialize to JSON and mark as safe for template rendering
    return mark_safe(json.dumps(messages_list))

# Made with Bob
