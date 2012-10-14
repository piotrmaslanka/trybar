# coding=UTF-8
from django import forms
from django.shortcuts import redirect
from django.core.paginator import Paginator
from trybar.core import render
from django.http import HttpResponse
from trybar.main.models import News
from django.template.loader import render_to_string
from trybar.account import must_be_logged, standard_profile_page_dict
from trybar.account.models import Account, AccountMail, Familiar
from trybar.accnews import RT_BECAME_FAMILIAR, accnews_for

class SendMessageForm(forms.Form):
    send_to = forms.CharField(max_length=25, widget=forms.TextInput(attrs={'id':'send_to'}))
    title = forms.CharField(max_length=80)
    content = forms.CharField(widget=forms.Textarea())

    def clean_send_to(self):
        send_to = self.cleaned_data['send_to']
        try:
            a = Account.objects.get(login=send_to)
        except:
            raise forms.ValidationError(u'Nie ma takiego użytkownika')
        if a == self.meta_user: 
            raise forms.ValidationError(u'Często rozmawiasz z samym sobą?')

        return a

@must_be_logged
def send(request):
    success = False
    if 'to' in request.GET:
        form = SendMessageForm(initial={'send_to':request.GET['to']})
    else:
        form = SendMessageForm()
    form.meta_user = request.user
    if request.method == 'POST':
        form = SendMessageForm(request.POST)
        form.meta_user = request.user
        if form.is_valid():
            AccountMail(sender=request.user, recipient=form.cleaned_data['send_to'], 
                        title=form.cleaned_data['title'], content=form.cleaned_data['content']).save()
            success = True

    spdict = standard_profile_page_dict(request) if request.user != None else {}
    return render('account/send_message.html', request, form=form, success=success, 
                                                        newsbar=News.get_news_for_sidebar(), **spdict)

@must_be_logged
def view_message(request, id):
    try:
        msg = AccountMail.objects.get(id=id)
        if msg.recipient != request.user: raise Exception
    except:
        return HttpResponse(status=404)

    msg.readed_yet = True
    msg.save()

    spdict = standard_profile_page_dict(request) if request.user != None else {}
    return render('account/view_message_message.html', request, newsbar=News.get_news_for_sidebar(), message=msg, **spdict)

@must_be_logged
def view_familiar(request, id):
    try:
        msg = Familiar.objects.get(id=id)
        if msg.confirmed: raise Exception
        if msg.befriendee != request.user: raise Exception
    except:
        return HttpResponse(status=404)

    if 'accept' in request.GET:
        msg.confirmed = True
        msg.save()
        accnews_for(msg.befriendee, RT_BECAME_FAMILIAR, msg.befriender)
        accnews_for(msg.befriender, RT_BECAME_FAMILIAR, msg.befriendee)
        return redirect('/profile/messages/')
    else:
        msg.readed_yet = True
        msg.save()

        spdict = standard_profile_page_dict(request) if request.user != None else {}
        return render('account/view_message_familiar.html', request, newsbar=News.get_news_for_sidebar(), invitation=msg, **spdict)    

@must_be_logged
def inbox(request, page=1, delete=False):

    if delete:
        # Create list of stuff to whack
        stuff_to_whack = []
        for key, value in request.GET.iteritems():
            if value != 'del': continue
            if key[0] not in ('m', 'f'): continue
            stuff_to_whack.append(key)
        for key, value in request.POST.iteritems():
            if value != 'del': continue
            if key[0] not in ('m', 'f'): continue
            stuff_to_whack.append(key)
        try:
            for arg in stuff_to_whack:
                if arg[0] not in ('m', 'f'): raise Exception
                if arg[0] == 'm':
                    obj = AccountMail.objects.get(id=int(arg[1:]))
                    if obj.recipient != request.user: raise Exception
                elif arg[0] == 'f':
                    obj = Familiar.objects.get(id=int(arg[1:]))
                    if obj.befriendee != request.user: raise Exception
                else:
                    raise Exception
                obj.delete()
        except:
            pass

    try:
        page = int(page)
    except:
        page = 1

    mailen = request.user.mail_received.all().select_related('sender__login', 'sender__id')
    frequesten = request.user.befriendee_set.all().filter(confirmed=False).select_related('befriender__login', 'befriender__id')

    def tupleify(obj):
        if type(obj) == AccountMail:
            return (obj.id, obj.sender.login, obj.sent_on, obj.title, 'm', obj.readed_yet)
        elif type(obj) == Familiar:
            return (obj.id, obj.befriender.login, obj.made_on, u'Zaproszenie', 'f', obj.readed_yet)
        else:
            raise Exception, 'Unknown object type'

    stuff = []
    for mail in mailen: stuff.append(tupleify(mail))
    for frequest in frequesten: stuff.append(tupleify(frequest))

    stuff.sort(key=lambda x: x[2], reverse=True)
    paginator = Paginator(stuff, 10)
    try:
        page = paginator.page(page)
    except:
        page = paginator.page(1)

    page_c = page.number

    if page_c < 4:
        page_start = 1
    else:
        page_start = page_c - 2

    if page_c > (paginator.num_pages-3):
        page_end = paginator.num_pages
    else:
        page_end = page_c + 2    

    spdict = standard_profile_page_dict(request) if request.user != None else {}
    return render('account/inbox.html', request, page=page, newsbar=News.get_news_for_sidebar(),
                                        page_iter=range(page_start, page_end+1),
                                        **spdict)
    