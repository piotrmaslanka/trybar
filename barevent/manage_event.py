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

class EditEventForm(forms.ModelForm):
    class Meta:
        model = Event
        exclude = ('name', 'name', 'miniature', 'slugname', 'bar',
                   'owner')

    # Following has to be called "poster" - and by extension have id of "id_poster"
    # Do not change, ON PAIN OF HUNTING CROSS-REFERENCES. You have been warned.
    poster = forms.ImageField(required=False)

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
        form = EditEventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.instance.save()

            if form.cleaned_data['poster'] != None:     # user submits a new poster
                if event.poster != None:    # there's an existing poster - pwn it
                  event.poster.delete()
                  event.poster = None

                event.poster = upload_as(form.cleaned_data['poster'], RES_EVENT_POSTER)
                event.save()
    try:
        form
    except:
        form = EditEventForm(instance=event)

    more_photos_than_6 = event.photos.count() > 6

    return render('barevent/manage.html', request, form=form, event=event, more_photos_than_6=more_photos_than_6)

@must_be_logged
def op(request, slugname):
    try:
        bar = Bar.objects.get(slugname=slugname)
    except Bar.DoesNotExist:
        return HttpResponse(status=404)

    if (bar.owner != request.user) and (not is_admin(request)):
        return HttpResponse(status=403)

    if 'op' not in request.GET: return HttpResponse(status=400)
    if request.GET['op'] == 'make_main':
      if not 'bpid' in request.GET: return HttpResponse(status=400)
      try:
        bp = BarPhoto.objects.get(id=int(request.GET['bpid']))
      except BarPhoto.DoesNotExist:
        return HttpResponse(status=404)
      except:
        return HttpResponse(status=400)
      if bp.bar != bar: return HttpResponse(status=403)
      for barphoto in bar.photos.all():
        barphoto.representative = False
        barphoto.save()
      bp.representative = True
      bp.save()
      return redirect('/bar/%s/manage/' % (slugname, ))
    elif request.GET['op'] == 'delete':
      if not 'bpid' in request.GET: return HttpResponse(status=400)
      try:
        bp = BarPhoto.objects.get(id=int(request.GET['bpid']))
      except BarPhoto.DoesNotExist:
        return HttpResponse(status=404)
      except:
        return HttpResponse(status=400)
      if bp.bar != bar: return HttpResponse(status=403)
      bp.photo.delete()
      bp.delete()
      return redirect('/bar/%s/' % (slugname, ))
    else:
      return HttpResponse(status=400)
