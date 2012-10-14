# coding=UTF-8
from django import forms
from django.shortcuts import redirect
from trybar.core import render, gpinfo
from trybar.core.mail import send_mail
from datetime import datetime
from hashlib import sha1
from django.http import Http404
from django.template.loader import render_to_string
from trybar.account import must_be_logged, standard_profile_page_dict
from trybar.account.models import Account, PasswordRecoveryToken, Familiar
from random import randint
from trybar.main.models import News
from trybar.accnews import RT_UNBECAME_FAMILIAR, accnews_for

import string
import random

class LoginForm(forms.Form):
    login = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        login = cleaned_data.get('login')
        password = cleaned_data.get('password')

        if (login == None) or (password == None):
            return cleaned_data
        
        try:
            acc = Account.objects.get(login=login)
        except Account.DoesNotExist:
            raise forms.ValidationError(u"Błędne dane")

        if not acc.check_password(password):
            raise forms.ValidationError(u"Błędne dane")

        if not acc.is_activated:
            raise forms.ValidationError(u"Konto nieaktywne")

        cleaned_data['account'] = acc
        return cleaned_data
    
def login(request):
    # You cannot login if logged
    if request.user != None:
        return redirect('/')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            request.login(form.cleaned_data['account'])
            
            return redirect('/now/')
    else:
        form = LoginForm()

    return render('account/login.html', request, form=form)
    
def logout(request):
    if request.user != None:
        request.logout()
    
    return redirect('/')

def profile(request, uid):
    try:
        acc = Account.objects.get(id=int(uid))
    except:
        raise Http404

    # ascertain friend status
    friend = None
    if request.user != None:
        if acc.id != request.user.id:   # only here it makes sense
            for familiar in request.user.befriender_set.all():
                if familiar.befriendee == acc:
                    # Found this entry!
                    friend = familiar.confirmed
                    familiar_entry = familiar
                    break
            if friend == None:
                for familiar in request.user.befriendee_set.all():
                    if familiar.befriender == acc:
                        # Found this entry!
                        friend = familiar.confirmed
                        familiar_entry = familiar
                        break

        if 'op' in request.GET:
            if (request.GET['op'] == 'befriend') and (friend == None):
                Familiar(befriender=request.user, befriendee=acc).save()
                friend = False

            if (request.GET['op'] == 'unfriend') and (friend == True):
                accnews_for(request.user, RT_UNBECAME_FAMILIAR, acc)
                accnews_for(acc, RT_UNBECAME_FAMILIAR, request.user)
                familiar_entry.delete()
                friend = None

    spdict = standard_profile_page_dict(request) if request.user != None else {}

    return render('account/profile.html', request, account=acc, 
                                                   is_friend=friend,
                                                   certainly_not_friend=friend == None,
                                                   newsbar=News.get_news_for_sidebar(),
                                                   **spdict)

class PassRemindForm(forms.Form):
    login = forms.CharField()
    email = forms.EmailField()

    def clean(self):
        cleaned_data = super(PassRemindForm, self).clean()
        login = cleaned_data.get('login')
        email = cleaned_data.get('email')

        if (login == None) or (email == None):
            return cleaned_data
        
        try:
            acc = Account.objects.get(login=login)
        except Account.DoesNotExist:
            raise forms.ValidationError(u"Błędne dane")

        if not acc.is_activated:
            raise forms.ValidationError(u"Konto nieaktywne")

        if acc.email != email:
            raise forms.ValidationError(u"Zły email")

        cleaned_data['account'] = acc
        return cleaned_data

def passrecover(request):
    if 'code' not in request.GET: return redirect('/')

    try:
        pret = PasswordRecoveryToken.objects.get(token=request.GET['code'])
    except PasswordRecoveryToken.DoesNotExist:
        return redirect('/')

    f = lambda x, y: ''.join([x[random.randint(0,len(x)-1)] for i in xrange(y)])
    rpasswd = f(list(string.ascii_letters+string.digits), 12)

    acc = pret.account

    mail_content = render_to_string('account/password_email', {'login':acc.login,
                                                               'password':rpasswd})
    acc.set_password(rpasswd)

    send_mail(acc.email, u'Resetowanie hasła', mail_content)

    return gpinfo(request, u"""Odesłano e-mail z nowym hasłem na Twoją skrzynkę pocztową.""", '/login/')


def passremind(request):
    if request.method == 'POST':
        form = PassRemindForm(request.POST)
        if form.is_valid():
            acc = form.cleaned_data['account']
            try:
                pret = PasswordRecoveryToken.objects.get(account=acc)
            except PasswordRecoveryToken.DoesNotExist:
                pass
            else:
                pret.delete()

            ip = request.META['REMOTE_ADDR']
            
            while True: # generate unique token
                tokenhash = sha1('%s%s-%s' % (acc.login, randint(1, 1000000), datetime.now())).hexdigest()
                try:
                    PasswordRecoveryToken.objects.get(token=tokenhash)
                except PasswordRecoveryToken.DoesNotExist:
                    break

            prt = PasswordRecoveryToken(account=acc, token=tokenhash, sent_to=acc.email, ipreq=ip)
            prt.save()

            mail_content = render_to_string('account/passremind_email', {'login':acc.login,
                                                                         'ip':ip,
                                                                         'sent_to':acc.email,
                                                                         'hash_code':tokenhash,
                                                                         'now':datetime.now()})

            send_mail(acc.email, u'Resetowanie hasła', mail_content)

        return gpinfo(request, u"""Jeśli dane były poprawne to wysłano e-mail z linkiem
                                   który pozwoli na odzyskanie takiego hasła. <br><br>Jeśli dane były błędne,
                                   taki e-mail oczywiście nie został wysłany.<br><br>Dodatkowo,
                                   jeśli to konto było w trakcie odzyskiwania hasła, poprzedni
                                   e-mail z linkiem stracił ważność.""", '/login/')
    else:
        form = PassRemindForm()

    return render('account/passremind.html', request, form=form)
