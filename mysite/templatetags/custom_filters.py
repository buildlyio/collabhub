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

@register.filter
def split(value, delimiter=','):
    """Split a string into a list using the delimiter"""
    if value is None:
        return []
    return [item.strip() for item in str(value).split(delimiter) if item.strip()]

@register.filter
def strip(value):
    """Trim whitespace from both ends of a string"""
    if value is None:
        return ''
    try:
        return str(value).strip()
    except Exception:
        return ''

@register.filter
def filter_by(items, arg):
    """Filter an iterable/queryset by field,value provided in arg"""
    if not items:
        return []
    try:
        field, value = [part.strip() for part in str(arg).split(',', 1)]
    except ValueError:
        return items
    if hasattr(items, 'filter'):
        try:
            return items.filter(**{field: value})
        except Exception:
            pass
    filtered = []
    for item in items:
        attr = getattr(item, field, None)
        if callable(attr):
            attr = attr()
        if str(attr) == value:
            filtered.append(item)
    return filtered
