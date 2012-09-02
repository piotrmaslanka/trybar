# coding=UTF-8
from django import forms
from django.shortcuts import redirect
from trybar.core import render, gpinfo
from trybar.core.mail import send_mail
from trybar.account import must_be_logged
from django.template.loader import render_to_string
from trybar.account.models import Account, AccountMeta
from hashlib import sha1
from trybar.core.fixtures import VOIVODESHIP_CHOICES

class RegisterForm(forms.ModelForm):
    class Meta:
        model = Account
        exclude = ('id', 'password', 'is_activated', 'created_on', 'familiar', 'avatar')
        widgets = {'voivodeship':forms.Select(attrs={'class':'selectbox'})}
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    regulamin = forms.BooleanField()

    def clean_login(self):
        login = self.cleaned_data['login']
        try:
            Account.objects.get(login=login)
        except Account.DoesNotExist:
            return login
        else: # account exists
            raise forms.ValidationError(u'Login zajęty')
    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            Account.objects.get(email=email)
        except Account.DoesNotExist:
            return email
        else: # account exists
            raise forms.ValidationError(u'Email zajęty')
    def clean(self):
        data = super(RegisterForm, self).clean()

        if data.get('password') != data.get('password2'):
            raise forms.ValidationError(u'Hasła niezgodne')

        return data

def view(request):
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            inst = form.instance

            inst.password = sha1(data['login'].encode('utf8')+data['password'].encode('utf8')).hexdigest()
            inst.save()

            AccountMeta(account=inst).save()

            mail_content = render_to_string('account/activation_email', {'login':inst.login,
                                                                         'password':data['password'],
                                                                         'hash_code':inst.activation_get_hash()})

            send_mail(inst.email, 'Rejestracja na Trybar', mail_content)

            return gpinfo(request, u'Konto zostało zarejestrowane. Za chwilę na twoją skrzynkę powinien przyjść e-mail z linkiem potwierdzającym', '/')
    return render('account/register.html', request, form=form)

def activate(request):
    acc = Account.objects.get(login=request.GET['login'])

    if acc.is_activated:
        return gpinfo(request, u'Konto już było aktywowane!', '/')            
    if acc.activation_get_hash() != request.GET['code']: raise Exception, acc.activation_get_hash()

    acc.activate()

    return gpinfo(request, u'Konto zostało aktywowane. Możesz teraz się zalogować.', '/login/')
