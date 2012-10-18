# coding=UTF-8
from django.shortcuts import redirect
from trybar.core import render
from trybar.account import must_be_logged
from trybar.bar.models import Bar, SingleBarMark, BarPhoto
from django.http import Http404, HttpResponse
from trybar.main.models import News
from django import forms
from trybar.account import must_be_logged, standard_profile_page_dict
from trybar.accnews import RT_BARPHOTO_ADDED, accnews_for
from trybar.scoring import BAR_PHOTO_ADDED, score_for
from django.core.paginator import Paginator
from trybar.main.models import EphemerisOtrzesiny

def otrzesiny(request):
    return render('ephemeris/otrzesiny.html', request, eos=EphemerisOtrzesiny.objects.all())    