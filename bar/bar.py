# coding=UTF-8
from django.shortcuts import redirect
from trybar.core import render
from trybar.account import must_be_logged
from trybar.bar.models import Bar, SingleBarMark
from django.http import Http404

def view(request, slugname):
    try:
        bar = Bar.objects.get(slugname=slugname)
    except Bar.DoesNotExist:
        raise Http404

    bar_constants = (
        (u'Wystrój wnętrza',  u'Pornodeutsch'),
        (u'Wystrój na zewnątrz', u'PD'),
        (u'Identyfikacja', u''),
        (u'Okolica', u''),
        (u'Muzyka', u''),
        (u'Ceny', u''),
        (u'Lokalizacja', u''),
        (u'Bezpieczeństwo', u''),
        (u'Personel', u''),
        (u'Alkohol', u''),
        (u'Jedzenie', u''),
        (u'Czystość', u''),
        (u'Tłok', u''))


    # Annotate bar_constants with identifier and marks - user-given and global average
    try:
        if request.user == None: raise Exception
        usermark = bar.marks.get(account=request.user)
    except:
        usermark = dict((('o'+str(x), None) for x in xrange(0, 14)))
    else:
        usermark = dict((('o'+str(x), usermark.__dict__['o'+str(x)]) for x in xrange(0, 14)))   

    avgmark = bar.meta

    x = -1
    category_info = []
    for mark_name, mark_description in bar_constants:
        x += 1
        category_info.append((x, mark_name, mark_description, usermark['o'+str(x)], 
                              avgmark.__dict__['avg_o'+str(x)]))

    l10r = range(1, 11)
    
    
    events = bar.events.order_by('happens_on')[:3]
    frequenters = bar.frequenters.order_by('?')[:6]

    # Check if frequenter
    try:
        bar.frequenters.get(account=request.user)
    except:
        is_frequenter = False
    else:
        is_frequenter = True

    return render('bar/bar.html', request, bar=bar, CATEGORY_INFO=category_info, 
                  l10r=l10r, events=events, frequenters=frequenters,
                  logged_in=request.user != None, is_frequenter=is_frequenter)
    
