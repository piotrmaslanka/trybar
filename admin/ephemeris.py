# coding=UTF-8
from django import forms
from django.http import HttpResponse
from django.shortcuts import redirect
from trybar.account import must_be_logged
from trybar.adverts.models import AdBanner
from django.shortcuts import render_to_response
from trybar.admin import must_be_admin
from trybar.adverts.models import TARGET_PAGES
from trybar.main.models import EphemerisOtrzesiny
from trybar.photo.models import Photo
from trybar.photo.upload import RES_BARPHOTO, upload_as


class AddOtrzesinyPhoto(forms.Form):
    # Following has to be called "picture" - and by extension have id of "id_picture"
    # Do not change, ON PAIN OF HUNTING CROSS-REFERENCES. You have been warned.
    picture = forms.ImageField(required=False)

@must_be_logged
@must_be_admin
def add_otrzesiny_photo(request):
  if request.method == 'POST':
    form = AddOtrzesinyPhoto(request.POST, request.FILES)
    if form.is_valid():
          pic = upload_as(form.cleaned_data['picture'], RES_BARPHOTO)
          b = EphemerisOtrzesiny(photo=pic)
          b.save()
  try:
    form
  except:
    form = AddOtrzesinyPhoto()

  return render_to_response('admin/otrzesiny.html', {'form':form})

