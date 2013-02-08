# coding=UTF-8
from django import forms
from django.shortcuts import redirect
from trybar.core import render
from django.http import HttpResponse, Http404
from trybar.account import must_be_logged, standard_profile_page_dict
from trybar.barevent.models import Event, EventPhoto
from trybar.scoring import BAR_EVENT_PHOTO_ADDED, score_for
from trybar.accnews import accnews_for
from trybar.accnews.models import RT_EVENTPHOTO_ADDED

class AddPhotoForm(forms.Form):
    # Following has to be called "picture" - and by extensions have id of "id_picture"
    # Do not change, ON PAIN OF HUNTING CROSS-REFERENCES
    picture = forms.ImageField(required=False)

    def clean_picture(self):
        pict = self.cleaned_data['picture']
        if pict != None:
            if pict.size > 1024*1024:
                raise forms.ValidationError(u'Rozmiar pliku przekracza 1 MB')
        return pict

@must_be_logged
def view(request, slugname, evtname):
    try:
        evt = Event.objects.get(slugname=evtname, bar__slugname=slugname)
    except Event.DoesNotExist:
        raise Http404

    if request.method == 'POST':
        form = AddPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            bp = EventPhoto.craft(form.cleaned_data['picture'], evt)
            score_for(request.user, BAR_EVENT_PHOTO_ADDED, bp)
            if evt.photos.all().count() == 1:
                bp.mark_as_mini()

            accnews_for(request.user, RT_EVENTPHOTO_ADDED, bp, evt)

            return redirect('/bar/%s/%s/' % (evt.bar.slugname, evt.slugname))

    try:
        form
    except:
        form = AddPhotoForm()

    return render('barevent/add_photo.html', request, form=form, event=evt,
                                                 **standard_profile_page_dict(request))