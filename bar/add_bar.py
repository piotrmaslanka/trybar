# coding=UTF-8
from django import forms
from django.shortcuts import redirect
from trybar.core import render, slugify
from trybar.account import must_be_logged
from trybar.bar.models import Bar, BAR_OPEN_HOURS_FROM, BAR_OPEN_HOURS_TO, BarMeta, BarPhoto
from trybar.core.fixtures import VOIVODESHIP_CHOICES, YES_NO_CHOICES
from trybar.scoring import score_for, BAR_ADDED, BAR_PHOTO_ADDED
from trybar.accnews import accnews_for, RT_ADDED_BAR

class AddBarForm(forms.Form):
    name = forms.CharField(max_length=40)
    street = forms.CharField(max_length=40)
    city = forms.CharField(max_length=50)
    voivodeship = forms.ChoiceField(choices=VOIVODESHIP_CHOICES, 
                                    widget=forms.Select(attrs={'class':'selectbox', 
                                                               'id':'wojewodztwo'}))
    description = forms.CharField(required=False, widget=forms.Textarea())

    credit_card = forms.ChoiceField(choices=YES_NO_CHOICES, widget=forms.RadioSelect(), required=False)
    wifi = forms.ChoiceField(choices=YES_NO_CHOICES, widget=forms.RadioSelect(), required=False)
    handicapped = forms.ChoiceField(choices=YES_NO_CHOICES, widget=forms.RadioSelect(), required=False)

    website = forms.CharField(required=False)

    openhours_5_f = forms.ChoiceField(choices=BAR_OPEN_HOURS_FROM, required=False,
                                      widget=forms.Select(attrs={'class':'godzina'}))
    openhours_5_t = forms.ChoiceField(choices=BAR_OPEN_HOURS_TO, required=False, 
                                      widget=forms.Select(attrs={'class':'godzina'}))
    openhours_sat_f = forms.ChoiceField(choices=BAR_OPEN_HOURS_FROM, required=False, 
                                        widget=forms.Select(attrs={'class':'godzina'}))
    openhours_sat_t = forms.ChoiceField(choices=BAR_OPEN_HOURS_TO, required=False, 
                                        widget=forms.Select(attrs={'class':'godzina'}))
    openhours_sun_f = forms.ChoiceField(choices=BAR_OPEN_HOURS_FROM, required=False, 
                                        widget=forms.Select(attrs={'class':'godzina'}))
    openhours_sun_t = forms.ChoiceField(choices=BAR_OPEN_HOURS_TO, required=False, 
                                        widget=forms.Select(attrs={'class':'godzina'}))

    is_closed_sat = forms.BooleanField(required=False)
    is_closed_sun = forms.BooleanField(required=False)

    is_darts = forms.BooleanField(required=False)
    is_games = forms.BooleanField(required=False)
    is_karaoke = forms.BooleanField(required=False)
    is_dancing = forms.BooleanField(required=False)
    is_billard = forms.BooleanField(required=False)
    is_tv = forms.BooleanField(required=False)

    # Following has to be called "picture" - and by extension have id of "id_picture"
    # Do not change, ON PAIN OF HUNTING CROSS-REFERENCES. You have been warned.
    picture = forms.ImageField(required=False)

    def clean_picture(self):
        pict = self.cleaned_data['picture']
        if pict != None:
            if pict.size > 1024*1024:
                raise forms.ValidationError(u'Rozmiar pliku przekracza 1 MB')
        return pict

    def clean_wifi(self):
        wifi = self.cleaned_data['wifi']
        if wifi == '': return None
        return bool(int(wifi))
    def clean_handicapped(self):
        handicapped = self.cleaned_data['handicapped']
        if handicapped == '': return None
        return bool(int(handicapped))
    def clean_credit_card(self):
        credit_card = self.cleaned_data['credit_card']
        if credit_card == '': return None
        return bool(int(credit_card))
    def clean_voivodeship(self):
        if self.cleaned_data['voivodeship'] in (None, u'None'):
            raise forms.ValidationError(u'Wybierz województwo')
        return self.cleaned_data['voivodeship']
    def clean(self):
        cleaned_data = super(AddBarForm, self).clean()
        name = cleaned_data.get('name')
        street = cleaned_data.get('street')
        city = cleaned_data.get('city')
        street = cleaned_data.get('street')
        voivodeship = cleaned_data.get('voivodeship')

        try:
            b = Bar.objects.get(name=name)
        except Bar.DoesNotExist:
            return cleaned_data

        if (b.street == street) and (b.city == city) and (b.voivodeship == voivodeship):
            raise forms.ValidationError(u'Ten bar już istnieje')
        else:
            return cleaned_data

@must_be_logged
def view(request):
    form = AddBarForm()
    if request.method == 'POST':
        form = AddBarForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data

            def does_bar_exist_with_given_slugname(slugn):
                if slugn == 'add': return True
                try:
                    Bar.objects.get(slugname=slugn)
                except Bar.DoesNotExist:
                    return False
                return True

            # Ascertain proper slug name
            slugname = slugify(data['name'])
            if does_bar_exist_with_given_slugname(slugname):
                k = 2
                while does_bar_exist_with_given_slugname(slugname+str(k)): k += 1
                slugname = slugname + str(k)

            # Start constructing the 'thing'
            b = Bar(slugname=slugname, owner=request.user, 

                    name=data['name'], street=data['street'], city=data['city'], 
                    voivodeship=data['voivodeship'], accepts_credit_cards=data['credit_card'],
                    wifi=data['wifi'], handicapped=data['handicapped'], website=data['website'],
                    description=data['description'],

                    is_darts=data['is_darts'], is_games=data['is_games'], is_karaoke=data['is_karaoke'],
                    is_dancing=data['is_dancing'], is_billard=data['is_billard'], is_tv=data['is_tv'],

                    openhours_5_f=data['openhours_5_f'], openhours_5_t=data['openhours_5_t'],
                    openhours_sat_f=data['openhours_sat_f'], openhours_sat_t=data['openhours_sat_t'],
                    openhours_sun_f=data['openhours_sun_f'], openhours_sun_t=data['openhours_sun_t'],
                    is_closed_sat=data['is_closed_sat'], is_closed_sun=data['is_closed_sun'],
                    )

            b.save()

            BarMeta(bar=b).save()

            score_for(request.user, BAR_ADDED, b)
            accnews_for(request.user, RT_ADDED_BAR, b)

            if data['picture'] != None:     # user wants us to submit a photo
                bp = BarPhoto.craft(data['picture'], b)
                score_for(request.user, BAR_PHOTO_ADDED, bp)

            return redirect('/bar/%s/' % (b.slugname, ))

    return render('bar/add_bar.html', request, form=form)