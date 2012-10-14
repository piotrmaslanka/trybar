# coding=UTF-8
from django import forms
from django.shortcuts import redirect
from trybar.core import render
from trybar.account import must_be_logged, standard_profile_page_dict
from trybar.account.models import Account
from django.core.paginator import Paginator

def ranking_users(request, page=None):
    try:
        page_c = int(page)
    except:
        page_c = 1

    p = Paginator(Account.objects.order_by('meta__rank'), 10)
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

    return render('ranking/users.html', request, page=page, 
                                                page_iter=range(page_start, page_end+1),
                                                **spdict)