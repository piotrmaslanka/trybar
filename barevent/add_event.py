# coding=UTF-8
from django import forms
from django.shortcuts import redirect
from trybar.core import render, slugify
from trybar.account import must_be_logged

from trybar.bar.models import Bar, BAR_OPEN_HOURS_FROM
from trybar.barevent.models import Event, EventMeta, EventArtist

from trybar.core.fixtures import VOIVODESHIP_CHOICES, YES_NO_CHOICES

from trybar.scoring import score_for, BAR_EVENT_ADDED
from trybar.accnews import accnews_for, RT_ADDED_EVENT

class AddEventForm(forms.Form):
    name = forms.CharField(max_length=40)
    date = forms.DateField(error_messages={'required':u'Pole wymagane', 'invalid':u'Wpisz poprawną datę. Format to ROK-MIESIĄC-DZIEŃ'})

    street = forms.CharField(max_length=40)
    city = forms.CharField(max_length=50)
    voivodeship = forms.ChoiceField(choices=VOIVODESHIP_CHOICES, 
                                    widget=forms.Select(attrs={'class':'selectbox', 
                                                               'id':'wojewodztwo'}))

    description = forms.CharField(required=False, widget=forms.Textarea())
    extra_info = forms.CharField(required=False, widget=forms.Textarea())

    entry = forms.IntegerField(initial=0)

    only_adults = forms.ChoiceField(choices=YES_NO_CHOICES, widget=forms.RadioSelect())

    start_at = forms.ChoiceField(choices=BAR_OPEN_HOURS_FROM, required=False,
                                 widget=forms.Select(attrs={'class':'godzina'}))


    artist_1 = forms.CharField(max_length=80, required=False)
    profile_1 = forms.CharField(max_length=100, required=False)

    artist_2 = forms.CharField(max_length=80, required=False)
    profile_2 = forms.CharField(max_length=100, required=False)

    artist_3 = forms.CharField(max_length=80, required=False)
    profile_3 = forms.CharField(max_length=100, required=False)

    artist_4 = forms.CharField(max_length=80, required=False)
    profile_4 = forms.CharField(max_length=100, required=False)

    artist_5 = forms.CharField(max_length=80, required=False)
    profile_5 = forms.CharField(max_length=100, required=False)

    def prime(self, bar):
        self.bar = bar
        return self


    def clean(self):
        cleaned_data = super(AddEventForm, self).clean()
        name = cleaned_data.get('name')

        try:
            b = Event.objects.filter(bar=self.bar).get(name=name)
        except Event.DoesNotExist:
            return cleaned_data
        else:
            raise forms.ValidationError(u'Taka impreza już istnieje')

@must_be_logged
def view(request, slugname):
    """@param slugname: bar's slugname"""
    try:
        bar = Bar.objects.get(slugname=slugname)
    except Bar.DoesNotExist:
        return HttpResponse(status=404)

    form = AddEventForm().prime(bar)
    if request.method == 'POST':
        form = AddEventForm(request.POST).prime(bar)
        if form.is_valid():
            data = form.cleaned_data

            def does_bar_event_exist_with_given_slugname(slugn):
                if slugn == 'add': return True
                try:
                    Event.objects.get(slugname=slugn)
                except Event.DoesNotExist:
                    return False
                return True

            # Ascertain proper slug name
            slugname = slugify(data['name'])
            if does_bar_event_exist_with_given_slugname(slugname):
                k = 2
                while does_bar_event_exist_with_given_slugname(slugname+str(k)): k += 1
                slugname = slugname + str(k)

            # Start constructing the 'thing'


            e = Event(bar=bar, owner=request.user,
                      description=data['description'], slugname=slugname,
                      entry_cost=data['entry'], age_limit=18 if data['only_adults'] else None,
                      extra_info=data['extra_info'], happens_on=data['date'],
                      starts_on=data['start_at'])

            e.save()

            EventMeta(event=e).save()

            # parse artists
            for aid in xrange(1, 6):
                if data['artist_'+str(aid)] != '':
                    # artist found
                    EventArtist(event=e, name=data['artist_'+str(aid)], profile=data['profile_'+str(aid)]).save()

            score_for(request.user, BAR_EVENT_ADDED, e)
            accnews_for(request.user, RT_ADDED_EVENT, e)

            return redirect('/bar/%s/%s/' % (bar.slugname, e.slugname))

    return render('barevent/add_event.html', request, form=form, bar=bar)