# coding=UTF-8
from django import forms
from django.shortcuts import redirect
from trybar.core import render, gpinfo
from datetime import datetime
from hashlib import sha1
from django.http import Http404
from django.template.loader import render_to_string
from trybar.account import must_be_logged, standard_profile_page_dict
from trybar.account.models import Account, PasswordRecoveryToken, Familiar
from trybar.main.models import News

def view_user_gallery(request):