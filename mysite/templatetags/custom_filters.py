from django import template

register = template.Library()

@register.filter
def has_attr(obj, attr_name):
    return hasattr(obj, attr_name)

@register.filter
def get(dictionary, key):
    """Get value from dictionary by key"""
    if dictionary and isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

@register.filter
def mul(value, arg):
    """Multiply value by arg"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
