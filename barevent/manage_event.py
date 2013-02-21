# coding=UTF-8
from django import forms
from django.shortcuts import redirect
from trybar.core import render
from trybar.account import must_be_logged, standard_profile_page_dict
from django.http import HttpResponse, Http404
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
from trybar.accnews import accnews_for
from trybar.accnews.models import RT_EVENTPHOTO_ADDED

from datetime import date
from trybar.barevent.add_event import DD, MM, RR

class EditEventForm(forms.ModelForm):
    class Meta:
        model = Event
        exclude = ('name', 'miniature', 'slugname', 'bar',
                   'owner', 'poster', 'age_limit')

    happens_on_d = forms.ChoiceField(choices=DD, required=False, widget=forms.Select(attrs={'class':'godzina'}))
    happens_on_m = forms.ChoiceField(choices=MM, required=False, widget=forms.Select(attrs={'class':'godzina'}))
    happens_on_y = forms.ChoiceField(choices=RR, required=False, widget=forms.Select(attrs={'class':'godzina'}))

    starts_on = forms.ChoiceField(choices=BAR_OPEN_HOURS_FROM, required=False,
                                 widget=forms.Select(attrs={'class':'godzina'}))

    only_adults = forms.BooleanField(widget=forms.RadioSelect(choices=((False, u'Nie'), (True, u'Tak'))), required=False)

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

    def clean_happens_on_y(self):
        if int(self.cleaned_data['happens_on_y']) == 0:
            raise forms.ValidationError(u'Wybierz rok')
        return self.cleaned_data['happens_on_y']

    def clean_happens_on_m(self):
        if int(self.cleaned_data['happens_on_m']) == 0:
            raise forms.ValidationError(u'Wybierz miesiąc')
        return self.cleaned_data['happens_on_m']

    def clean_happens_on_d(self):
        if int(self.cleaned_data['happens_on_d']) == 0:
            raise forms.ValidationError(u'Wybierz dzień')
        return self.cleaned_data['happens_on_d']

    def clean(self):
      cleaned_data = super(EditEventForm, self).clean()
      try:
          date(int(self.cleaned_data['happens_on_y']), int(self.cleaned_data['happens_on_m']), int(self.cleaned_data['happens_on_d']))
      except ValueError:
          return forms.ValidationError(u'Niepoprawna data rozpoczęcia')
      return cleaned_data

@must_be_logged
def view(request, slugname, evtname):
    try:
        event = Event.objects.filter(bar__slugname=slugname).get(slugname=evtname)
    except Event.DoesNotExist:
        raise Http404

    if (event.owner != request.user) and (not is_admin(request)):
        return HttpResponse(status=403)

    if request.method == 'POST':
        form = EditEventForm(request.POST, request.FILES, instance=event, initial={'only_adults': event.age_limit == 18})
        if form.is_valid():
            form.instance.age_limit = 18 if form.cleaned_data['only_adults'] else 0
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
              accnews_for(request.user, RT_EVENTPHOTO_ADDED, ep, event)

              if len(event.photos.all()) == 1:
                ep.mark_as_mini()

            if form.cleaned_data['partner'] != None:              
              Partner.craft(form.cleaned_data['partner'], event, form.cleaned_data['partner_url'])

    try:
        form
    except:
        form = EditEventForm(instance=event, initial={'only_adults': event.age_limit == 18})

    more_photos_than_6 = event.photos.count() > 6


    # check if can manage
    can_manage = (event.owner == request.user) or ()

    return render('barevent/manage.html', request, form=form, event=event, 
            more_photos_than_6=more_photos_than_6, current_poster=event.poster,
            can_manage=can_manage)

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
    elif request.GET['op'] == 'make_main':
      if not 'pid' in request.GET: return HttpResponse(status=400)
      try:
        bp = EventPhoto.objects.get(id=int(request.GET['pid']))
      except EventPhoto.DoesNotExist:
        return HttpResponse(status=404)
      else:
        bp.mark_as_mini()
        return redirect('/bar/%s/%s/manage/' % (slugname, evtname))
    else:
      return HttpResponse(status=400)



@must_be_logged
def list_of_events(request, page=1):
    try:
        page_c = int(page)
    except:
        page_c = 1

    p = Paginator(request.user.events_owned.order_by('name'), 10)
    page = p.page(page_c)

    spdict = standard_profile_page_dict(request) if request.user != None else {}

    page_c = p.num_pages

    if page_c < 4:
        page_start = 1
    else:
        page_start = page_c - 2

    if page_c > (p.num_pages-3):
        page_end = p.num_pages
    else:
        page_end = page_c + 2

    return render('barevent/event_manage_list.html', request, page=page,
                                              page_iter=range(page_start, page_end+1),
                                              newsbar=News.get_news_for_sidebar(), **spdict)