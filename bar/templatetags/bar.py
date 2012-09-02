from django import template
register = template.Library()

@register.filter
def hThreeway(value):
    if value == True: return u'TAK'
    elif value == False: return u'NIE'
    return u''