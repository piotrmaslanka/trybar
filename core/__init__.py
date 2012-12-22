# coding=UTF-8
from django.shortcuts import render_to_response
from django.template.defaultfilters import slugify as _slugify

def render(template_path, request, **extras):
    pte = {'request': request}
    pte.update(extras)
    return render_to_response(template_path, pte)
    
def gpinfo(request, info, url_next):
    return render('gpinfo.html', request, info=info, next_url=url_next)    

def slugify(name):
    POLISH_DIACRITIC_LOOKUP = {u'Ą':u'A', u'ą':u'a', u'Ć':u'C', u'ć':u'c', u'Ę':u'E', u'ę':u'e', u'Ż':u'Z', u'ż':u'z',
                             u'Ź':u'Z', u'ź':u'z', u'Ó':u'O', u'ó':u'o', u'Ł':u'l', u'ł':u'l', u'Ś':u'S', u'ś':u's',
                             u'Ń':u'N', u'ń':u'n'}      
    for fr, t in POLISH_DIACRITIC_LOOKUP.iteritems():
        name = name.replace(fr, t)    
    return _slugify(name)    