from django import template

register = template.Library()

@register.filter
def has_punchlisthunter(user):
    return hasattr(user, 'punchlisthunter')
