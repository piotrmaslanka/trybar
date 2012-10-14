# coding=UTF-8
from django import forms
from django.shortcuts import redirect
from trybar.core import render
from trybar.account import must_be_logged, standard_profile_page_dict
from trybar.bar.models import Account
from trybar.main.models import News
from django.core.paginator import Paginator
from django.db.models import Q

def view(request, page=None):
    try:
        page_c = int(page)
    except:
        page_c = 1


    try:
        q = request.GET['q'].strip()
    except:
        result_set = None       # need proper query
        page_iter = None
        q = None
        nothing_found = False
    else:
        result_set = Account.objects.filter(login__icontains=q).order_by('login').order_by('-meta__score')

        p = Paginator(result_set, 10)
        page = p.page(page_c)

        if page_c < 4:
            page_start = 1
        else:
            page_start = page_c - 2

        if page_c > (p.num_pages-3):
            page_end = p.num_pages
        else:
            page_end = page_c + 2

        page_iter = range(page_start, page_end+1)
        nothing_found = p.count == 0


    spdict = standard_profile_page_dict(request) if request.user != None else {}

    return render('search/users.html', request, page=page, 
                                               query=q,
                                               nothing_found=nothing_found,
                                               page_iter=page_iter,
                                               newsbar=News.get_news_for_sidebar(), **spdict)