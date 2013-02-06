# coding=UTF-8
from django import forms
from django.shortcuts import redirect
from trybar.core import render
from trybar.account import must_be_logged, standard_profile_page_dict
from trybar.account.models import Account
from trybar.bar.models import Bar
from trybar.main.models import News
from django.core.paginator import Paginator

def events(request, uid, page=None):
    raise NotImplementedError

def bars(request, uid, page=None):
    try:
        page_c = int(page)
    except:
        page_c = 1

    try:
        acc = Account.objects.get(id=int(uid))
    except:
        return redirect('/')

    p = Paginator(Bar.objects.filter(owner=acc).order_by('name'), 10)
    page = p.page(page_c)

    spdict = standard_profile_page_dict(request) if request.user != None else {}

    if page_c < 4:
        page_start = 1
    else:
        page_start = page_c - 2

    if page_c > (p.num_pages-3):
        page_end = p.num_pages
    else:
        page_end = page_c + 2

    return render('account/bars.html', request, page=page, 
                                                root_account=acc,
                                                newsbar=News.get_news_for_sidebar(),
                                                page_iter=range(page_start, page_end+1),
                                                **spdict)


def familiars(request, uid, page=None):
    try:
        page_c = int(page)
    except:
        page_c = 1

    try:
        acc = Account.objects.get(id=int(uid))
    except:
        return redirect('/')

    p = Paginator(list(acc.familiar_set), 10)
    page = p.page(page_c)

    spdict = standard_profile_page_dict(request) if request.user != None else {}

    if page_c < 4:
        page_start = 1
    else:
        page_start = page_c - 2

    if page_c > (p.num_pages-3):
        page_end = p.num_pages
    else:
        page_end = page_c + 2

    return render('account/familiars.html', request, page=page, 
                                                root_account=acc,
                                                newsbar=News.get_news_for_sidebar(),
                                                page_iter=range(page_start, page_end+1),
                                                **spdict)