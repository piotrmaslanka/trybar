from django import forms
from django.shortcuts import redirect
from trybar.core import render
from trybar.account.models import Account

def index(request):
    return render('main/index.html', request)