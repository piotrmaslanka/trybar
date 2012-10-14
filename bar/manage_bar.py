# coding=UTF-8
from django import forms
from django.shortcuts import redirect
from trybar.core import render
from trybar.account import must_be_logged, standard_profile_page_dict
from django.http import HttpResponse
from trybar.bar.models import Bar, BAR_OPEN_HOURS_FROM, BAR_OPEN_HOURS_TO, BarMeta, BarPhoto
from trybar.core.fixtures import VOIVODESHIP_CHOICES, YES_NO_CHOICES
from trybar.scoring import score_for, BAR_ADDED, BAR_PHOTO_ADDED
from trybar.accnews import accnews_for, RT_ADDED_BAR
from trybar.admin import is_admin
from django.core.paginator import Paginator
from trybar.main.models import News

class EditBarForm(forms.ModelForm):
    class Meta:
        model = Bar
        exclude = ('frontpage_type_display', 'name', 'street', 'city', 'voivodeship',
                   'owner', 'slugname', 'slugname_up_front', 'logo')
        widgets = {'accepts_credit_cards': forms.RadioSelect(choices=YES_NO_CHOICES),
                   'wifi': forms.RadioSelect(choices=YES_NO_CHOICES),
                   'handicapped': forms.RadioSelect(choices=YES_NO_CHOICES),
                    # ^ these were DRY in it's best rendition :/
                   'openhours_5_f':forms.Select(attrs={'class':'godzina'}),
                   'openhours_5_t':forms.Select(attrs={'class':'godzina'}),
                   'openhours_sat_f':forms.Select(attrs={'class':'godzina'}),
                   'openhours_sat_t':forms.Select(attrs={'class':'godzina'}),
                   'openhours_sun_f':forms.Select(attrs={'class':'godzina'}),
                   'openhours_sun_t':forms.Select(attrs={'class':'godzina'}),
                   'is_closed_sat':forms.CheckboxInput(),
                   'is_closed_sun':forms.CheckboxInput(),                   
                   }

    # Following has to be called "picture" - and by extension have id of "id_picture"
    # Do not change, ON PAIN OF HUNTING CROSS-REFERENCES. You have been warned.
    picture = forms.ImageField(required=False)

    def clean_picture(self):
        pict = self.cleaned_data['picture']
        if pict != None:
            if pict.size > 1024*1024:
                raise forms.ValidationError(u'Rozmiar pliku przekracza 1 MB')
        return pict

@must_be_logged
def view(request, slugname):
    try:
        bar = Bar.objects.get(slugname=slugname)
    except Bar.DoesNotExist:
        return HttpResponse(status=404)

    if (bar.owner != request.user) and (not is_admin(request)):
        return HttpResponse(status=403)

    rep_photo = bar.get_representative_photo()

    if request.method == 'POST':
        form = EditBarForm(request.POST, request.FILES, instance=bar)
        if form.is_valid():
            form.instance.save()

            if form.cleaned_data['picture'] != None:     # user wants us to submit a photo
                bp = BarPhoto.craft(form.cleaned_data['picture'], bar)
                score_for(request.user, BAR_PHOTO_ADDED, bp)

    try:
        form
    except:
        form = EditBarForm(instance=bar)

    more_photos_than_6 = bar.photos.count() > 6

    return render('bar/manage.html', request, form=form, bar=bar, more_photos_than_6=more_photos_than_6, rep_photo=rep_photo)

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

@must_be_logged
def list_of_bars(request, page=1):
    try:
        page_c = int(page)
    except:
        page_c = 1

    p = Paginator(request.user.bars_owned.order_by('name'), 10)
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

    return render('bar/bar_manage_list.html', request, page=page,
                                              page_iter=range(page_start, page_end+1),
                                              newsbar=News.get_news_for_sidebar(), **spdict)