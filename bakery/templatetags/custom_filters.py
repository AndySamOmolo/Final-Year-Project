from django import template

register = template.Library()

@register.filter
def sum_attribute(items, attr):
    """Sums up the specified attribute from a list of objects."""
    return sum(getattr(item, attr, 0) for item in items)
