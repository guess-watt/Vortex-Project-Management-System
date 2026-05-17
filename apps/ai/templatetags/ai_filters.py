from django import template

register = template.Library()


@register.filter(name='replace')
def replace(value, args):
    """
    Replace occurrences of a substring with another substring.
    Usage: {{ value|replace:"old,new" }}
    """
    if not args or ',' not in args:
        return value
    
    old, new = args.split(',', 1)
    return str(value).replace(old, new)

# Made with Bob
