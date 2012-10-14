from django import forms
from django.shortcuts import redirect
from trybar.core import render
from trybar.account.models import Account
from trybar.main.models import News, NewsComment
from django.http import HttpResponse
from datetime import datetime, timedelta
from trybar.scoring import score_for, NEWS_COMMENT_ADDED


def view_all(request):
    news = News.objects.all()

    return render('main/list_of_news.html', request, news=news)

def view(request, id):
    try:
        news = News.objects.get(id=int(id))
    except:
        return HttpResponse(status=404)

    if request.method == 'POST':
        if 'content' in request.POST:
            if request.user != None:
                # Limit: no faster than 15s
                try:
                    lbc = NewsComment.objects.filter(made_for=news).filter(account=request.user)[0]
                except:
                    pass
                else:
                    if (datetime.now() - lbc.made_on) < timedelta(0, 15):
                        # too soon, limit in effect
                        return render('main/news.html', request, news=news, comment_too_fast=True)

                nc = NewsComment(account=request.user, content=request.POST['content'], made_for=news)
                nc.save()
                score_for(request.user, NEWS_COMMENT_ADDED, nc)

    return render('main/news.html', request, news=news)