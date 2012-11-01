# coding=UTF-8
from django import forms
from django.http import HttpResponse
from django.shortcuts import redirect
from trybar.account import must_be_logged
from trybar.adverts.models import AdBanner
from django.shortcuts import render_to_response
from trybar.admin import must_be_admin
from trybar.adverts.models import TARGET_PAGES
from trybar.photo.models import Photo
from trybar.photo.upload import RES_BANNER, upload_as

class AddBannerForm(forms.Form):
    target_page = forms.ChoiceField(choices=TARGET_PAGES, label=u'Strona docelowa')
    link = forms.CharField(label=u'Hiperłącze (wraz z http://))')
    picture = forms.ImageField(label=u'Baner (980x150)')

@must_be_logged
@must_be_admin
def delete(request, id):
    try:
        ad = AdBanner.objects.get(id=int(id))
    except AdBanner.DoesNotExist:
        return redirect('/admin/adpanel/')
    photo = ad.photo
    ad.delete()
    photo.delete()

    return redirect('/admin/adpanel/')

@must_be_logged
@must_be_admin
def view_banners(request):
    banners = AdBanner.objects.all()
    form = AddBannerForm()

    if request.method == 'POST':
        form = AddBannerForm(request.POST, request.FILES)
        if form.is_valid():
            target_page_set = (int(form.cleaned_data['target_page']), )

            for target_page in target_page_set:
                photo = upload_as(form.cleaned_data['picture'], RES_BANNER)
                ab = AdBanner(target_page=target_page, link=form.cleaned_data['link'],
                              photo=photo)
                ab.save()

            # null all banners
            for banner in AdBanner.objects.all():
                banner.times_viewed = 0
                banner.save()
                     
    return render_to_response('admin/adpanel.html', {'banners': banners,
													 'form': form})


