# coding=UTF-8
from django import forms
from django.shortcuts import redirect
from trybar.core import render
from trybar.account import must_be_logged, standard_profile_page_dict
from django.http import HttpResponse
from trybar.bar.models import BarFrequenter
from trybar.admin import is_admin
from trybar.account.models import Account
from django.core.paginator import Paginator
from trybar.main.models import News

def barlist(request, uid, page=1):
    try:
        user = Account.objects.get(id=int(uid))
    except:
        return HttpResponse(status=404)
    try:
        page_c = int(page)
    except:
        page_c = 1

    p = Paginator(BarFrequenter.objects.filter(account=user).order_by('bar__name').select_related('bar'), 10)
    page = p.page(page_c)

    spdict = standard_profile_page_dict(request) if request.user != None else {}

    page_c = p.num_pages

    if page_c < 4:
        page_start = 1
    else:
        page_start = page_c - 2

    if page_c > (p.num_pages-3):
        page_end = p.num_pages
    else:
        page_end = page_c + 2

    return render('account/frequenter_at.html', request, page=page, user=user,
                                              page_iter=range(page_start, page_end+1),
                                              newsbar=News.get_news_for_sidebar(), **spdict)