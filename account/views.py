# coding=UTF-8
from django import forms
from django.shortcuts import redirect
from trybar.core import render
from trybar.account import must_be_logged
from trybar.account.models import Account

class LoginForm(forms.Form):
    login = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        login = cleaned_data.get('login')
        password = cleaned_data.get('password')
        
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
            
            return redirect('/')
    else:
        form = LoginForm()

    return render('account/login.html', request, form=form)
    
def logout(request):
    if request.user != None:
        request.logout()
    
    return redirect('/')

# @must_be_logged
def profile(request):
    return render('account/profile.html', request)
        