# coding=UTF-8
from django import forms
from django.shortcuts import redirect
from trybar.core import render
from trybar.account import must_be_logged, standard_profile_page_dict
from django.http import HttpResponse
from trybar.bar.models import Bar, BAR_OPEN_HOURS_FROM, BAR_OPEN_HOURS_TO, BarMeta, BarPhoto
from trybar.barevent.models import Event, EventPhoto, Partner
from trybar.core.fixtures import VOIVODESHIP_CHOICES, YES_NO_CHOICES
from trybar.scoring import score_for, BAR_ADDED, BAR_PHOTO_ADDED
from trybar.accnews import accnews_for, RT_ADDED_BAR
from trybar.admin import is_admin
from django.core.paginator import Paginator
from trybar.main.models import News
from trybar.photo.upload import upload_as, RES_EVENT_POSTER, RES_EVENT_MINIATURE, RES_EVENT_PHOTO, RES_EVENT_PARTNER
from trybar.scoring import BAR_EVENT_PHOTO_ADDED, score_for

class EditEventForm(forms.ModelForm):
    class Meta:
        model = Event
        exclude = ('name', 'miniature', 'slugname', 'bar',
                   'owner', 'poster', 'age_limit')

    only_adults = forms.BooleanField(widget=forms.RadioSelect(choices=((0, u'Nie'), (1, u'Tak'))))

    poster = forms.ImageField(required=False)
    partner = forms.ImageField(required=False)
    partner_url = forms.URLField(required=False)
    photo = forms.ImageField(required=False)

    def clean_poster(self):
        pict = self.cleaned_data['poster']
        if pict != None:
            if pict.size > 1024*1024:
                raise forms.ValidationError(u'Rozmiar pliku przekracza 1 MB')
        return pict

@must_be_logged
def view(request, slugname, evtname):
    try:
        event = Event.objects.filter(bar__slugname=slugname).get(slugname=evtname)
    except Event.DoesNotExist:
        raise Http404

    if (event.owner != request.user) and (not is_admin(request)):
        return HttpResponse(status=403)

    if request.method == 'POST':
        form = EditEventForm(request.POST, request.FILES, instance=event, initial={'only_adults': int(event.age_limit == 18)})
        if form.is_valid():
            form.instance.age_limit = 18 if form['only_adults'] else 0
            form.instance.save()

            if form.cleaned_data['poster'] != None:     # user submits a new poster            
                if event.poster != None:    # there's an existing poster - pwn it
                  # if you do event.poster.delete() shits comes down on you hard
                  poster = event.poster
                  event.poster = None
                  event.save()

                  poster.delete()

                event.poster = upload_as(form.cleaned_data['poster'], RES_EVENT_POSTER)
                event.save()

            if form.cleaned_data['photo'] != None:
              ep = EventPhoto.craft(form.cleaned_data['photo'], event)
              score_for(request.user, BAR_EVENT_PHOTO_ADDED, ep)

            if form.cleaned_data['partner'] != None:
              Partner.craft(form.cleaned_data['partner'], event, form.cleaned_data['partner_url'])

    try:
        form
    except:
        form = EditEventForm(instance=event, initial={'only_adults': int(event.age_limit == 18)})

    more_photos_than_6 = event.photos.count() > 6

    return render('barevent/manage.html', request, form=form, event=event, 
            more_photos_than_6=more_photos_than_6, current_poster=event.poster)

@must_be_logged
def op(request, slugname, evtname):
    try:
        event = Event.objects.filter(bar__slugname=slugname).get(slugname=evtname)
    except Event.DoesNotExist:
        raise Http404

    if (event.owner != request.user) and (not is_admin(request)):
        return HttpResponse(status=403)

    if 'op' not in request.GET: return HttpResponse(status=400)

    if request.GET['op'] == 'delete_photo':
      if not 'pid' in request.GET: return HttpResponse(status=400)
      try:
        bp = EventPhoto.objects.get(id=int(request.GET['pid']))
      except EventPhoto.DoesNotExist:
        return HttpResponse(status=404)
      except:
        return HttpResponse(status=400)

      if bp.event != event: return HttpResponse(status=403)

      bp.delete()
      return redirect('/bar/%s/%s/manage/' % (slugname, evtname))
    elif request.GET['op'] == 'delete_partner':
      if not 'pid' in request.GET: return HttpResponse(status=400)
      try:
        bp = Partner.objects.get(id=int(request.GET['pid']))
      except:
        return HttpResponse(status=404)

      if bp.event != event: return HttpResponse(status=403)
      bp.delete()
      return redirect('/bar/%s/%s/manage/' % (slugname, evtname))
    else:
      return HttpResponse(status=400)