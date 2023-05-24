from django import template

register = template.Library()

@register.filter
def has_bountyhunter(user):
    return hasattr(user, 'bountyhunter')
