from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(value, arg):
    """Adds the given class to the widget"""
    return value.as_widget(attrs={'class': arg})
