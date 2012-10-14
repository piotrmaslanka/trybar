# coding=UTF-8
from django.shortcuts import redirect
from trybar.core import render, gpinfo
from trybar.bar.models import Bar
from django import forms
from trybar.main.models import News
from trybar.account import must_be_logged, standard_profile_page_dict
from trybar.core.mail import send_mail

def what_is_trybar(request):
    request.session['seen_whatis'] = True
    if 'disable' in request.GET:
        rdo = redirect('/')
        rdo.set_cookie('force_whatis', 'dont')
        return rdo

    return render('main/what_is_trybar.html', request)

def building(request):
    return gpinfo(request, u'Strona w budowie', 'javascript:history.go(-1)')

class ContactFormWithEmail(forms.Form):
    email = forms.EmailField(max_length=100)
    title = forms.CharField(max_length=80)
    content = forms.CharField(widget=forms.Textarea())
class ContactFormWithoutEmail(forms.Form):
    title = forms.CharField(max_length=80)
    content = forms.CharField(widget=forms.Textarea())

def contact_form(request):
    form = ContactFormWithEmail() if request.user == None else ContactFormWithoutEmail()
    success = False
    if request.method == 'POST':
        form = ContactFormWithEmail(request.POST) if request.user == None else ContactFormWithoutEmail(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']
            if request.user == None:
                email = form.cleaned_data['email']
                k = u'Wysłano mail z formularza kontaktowego\nEmail: %s\nTytuł: %s\n\nTreść:\n%s\n' % (email, title, content)
            else:
                k = u'Wysłano mail z formularza kontaktowego\nLogin: %s\nTytuł: %s\n\nTreść:\n%s\n' % (request.user.login, title, content)
            send_mail('kontakt@trybar.pl', u'[AUTOMAT] Formularz kontaktowy', k)            
            success = True
    spdict = {} if request.user == None else standard_profile_page_dict(request)
    return render('main/contact_form.html', request, form=form, newsbar=News.get_news_for_sidebar(), success=success, **spdict)

def regulamin(request):
    spdict = {} if request.user == None else standard_profile_page_dict(request)
    return render('main/regulamin.html', request, newsbar=News.get_news_for_sidebar(), **spdict)

def birthday(request):
    rootbars = [Bar.objects.filter(slugname='alibi'), 
                Bar.objects.filter(slugname='billkros'),
                Bar.objects.filter(slugname='capone'),
                Bar.objects.filter(slugname='corleone'),
                Bar.objects.filter(slugname='joker')]
    rootbars = reduce(lambda x,y:x+y, map(list, rootbars), [])

    afterp = [Bar.objects.filter(slugname='carmel-club-caffe'),
              Bar.objects.filter(slugname='joker')]
    afterp = reduce(lambda x,y:x+y, map(list, afterp), [])

    return render('main/birthday.html', request, afterparty=afterp, promo_bary=rootbars)

def http404(request):
    return render('http_errors/404.html', request)    
def http500(request):
    return render('http_errors/500.html', request)