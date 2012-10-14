from django import template
register = template.Library()

@register.filter
def hThreeway(value, arg=''):
    if value == True: return u'TAK'
    elif value == False: return u'NIE'
    return arg


@register.filter
def word_slice(value, arg):
    table = value.split(' ')
    return u' '.join(eval('table['+arg+']'))

@register.filter
def round_float(value, places=None):
    try:
        if places == None:
            return round(value)
        else:
            return ('%.'+str(places)+'f') % (float(value), )
    except:
        return u'??'
