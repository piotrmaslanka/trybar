# coding=UTF-8
from django import forms
from django.shortcuts import redirect
from trybar.core import render, gpinfo
from trybar.core.mail import send_mail
from datetime import datetime
from hashlib import sha1
from trybar.core import render
from django.http import Http404
from django.template.loader import render_to_string
from trybar.account import must_be_logged, standard_profile_page_dict
from trybar.account.models import Account
from random import randint
from trybar.main.models import News
from trybar.core.fixtures import VOIVODESHIP_CHOICES
from trybar.photo.models import Photo
from trybar.photo.upload import upload_as, RES_AVATAR
from trybar.accnews import RT_AVATAR_ADDED, accnews_for

class ProfileEditForm(forms.Form):
    name = forms.CharField(max_length=20, required=False)
    surname = forms.CharField(max_length=25, required=False)
    current_password = forms.CharField(widget=forms.PasswordInput, required=False)
    new_password = forms.CharField(widget=forms.PasswordInput, required=False)
    new_password2 = forms.CharField(widget=forms.PasswordInput, required=False)
    city = forms.CharField(max_length=25)
    voivodeship = forms.CharField(max_length=30, widget=forms.Select(choices=VOIVODESHIP_CHOICES, attrs={'class':'selectbox'}))
    gadu = forms.CharField(max_length=20, required=False)
    phone = forms.CharField(max_length=25, required=False)

    # Following has to be called "picture" - and by extensions have id of "id_picture"
    # Do not change, ON PAIN OF HUNTING CROSS-REFERENCES
    picture = forms.ImageField(required=False)

    def clean_picture(self):
        pict = self.cleaned_data['picture']
        if pict != None:
            if pict.size > 1024*100:
                raise forms.ValidationError(u'Rozmiar pliku przekracza 100 kB')
        return pict

    def clean_current_password(self):
        pwd = self.cleaned_data['current_password']
        if pwd == '': return pwd
        if not self.request.user.check_password(pwd):
            raise forms.ValidationError(u'Błędne hasło')

    def clean(self):
        cleaned_data = super(ProfileEditForm, self).clean()
        try:
            curpwd = cleaned_data.get('current_password')
            newpwd = cleaned_data.get('new_password')
            newpwd2 = cleaned_data.get('new_password2')
        except:
            return cleaned_data

        if curpwd != '':
            if newpwd == '': raise forms.ValidationError(u'Musisz podać nowe hasło')
            if newpwd != newpwd2: raise forms.ValidationError(u'Hasła nie zgadzają się')
            
        return cleaned_data

    def kickstart(self, request):
        self.request = request
        return self


@must_be_logged
def view(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES).kickstart(request)
        if form.is_valid():
            user = request.user
            data = form.cleaned_data
            # Change basic stuff
            user.name = data['name']
            user.surname = data['surname']
            user.city = data['city']
            user.voivodeship = data['voivodeship']
            user.gadu = data['gadu']
            user.phone = data['phone']

            # Check if password change needed
            if (data['current_password'] != '') and (data['new_password'] != ''):
                user.set_password(data['new_password'])


            # Check if avatar change needed
            if data['picture'] != None:
                if user.avatar != None:
                    avatar = user.avatar
                    user.avatar = None
                    user.save()
                    avatar.delete()
                user.avatar = upload_as(data['picture'], RES_AVATAR)
                accnews_for(user, RT_AVATAR_ADDED)

            # Save that shit
            user.save()
            return redirect('/profile/%s/' % (user.id, ))

    try:
        form
    except:     # We need to construct it
        form = ProfileEditForm(initial={'name':request.user.name,
                                        'surname':request.user.surname,
                                        'city':request.user.city,
                                        'voivodeship':request.user.voivodeship,
                                        'gadu':request.user.gadu,
                                        'phone':request.user.phone}).kickstart(request)

    spdict = standard_profile_page_dict(request)

    return render('account/edit_profile.html', request, form=form, **spdict)




