# coding=UTF-8
from django.shortcuts import redirect
from trybar.core import render
from trybar.account import must_be_logged
from trybar.bar.models import Bar, SingleBarMark, BarPhoto
from django.http import Http404, HttpResponse
from trybar.main.models import News
from django import forms
from trybar.account import must_be_logged, standard_profile_page_dict
from trybar.accnews import RT_BARPHOTO_ADDED, accnews_for
from trybar.scoring import BAR_PHOTO_ADDED, score_for
from django.core.paginator import Paginator

DEFAULT_COMMENT_TEXT = u'Napisz co myślisz o tym lokalu...'

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

def frequenters(request, slugname, page=1):
    try:
        bar = Bar.objects.get(slugname=slugname)
    except Bar.DoesNotExist:
        raise Http404

    p = Paginator(bar.frequenters.all(), 10)
    page = p.page(page)

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

    spdict = standard_profile_page_dict(request) if request.user != None else {}
    return render('bar/frequenters.html', request, page=page, bar=bar,
                                                   page_iter=range(page_start, page_end+1),
                                                   newsbar=News.get_news_for_sidebar(), **spdict)


@must_be_logged
def add_photo(request, slugname):
    try:
        bar = Bar.objects.get(slugname=slugname)
    except Bar.DoesNotExist:
        raise Http404

    if request.method == 'POST':
        form = AddPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            bp = BarPhoto.craft(form.cleaned_data['picture'], bar)
            score_for(request.user, BAR_PHOTO_ADDED, bp)
            accnews_for(request.user, RT_BARPHOTO_ADDED, bp, bar)
            return redirect('/bar/%s/' % (bar.slugname, ))

    try:
        form
    except:
        form = AddPhotoForm()

    return render('bar/add_photo.html', request, form=form, bar=bar,
                                                 **standard_profile_page_dict(request))

def refer(request, slugname):
    if slugname[-1] == '/': slugname = slugname[:-1]
    try:
        bar = Bar.objects.get(slugname_up_front=slugname)
    except Bar.DoesNotExist:
        raise Http404

    return redirect('/bar/'+bar.slugname+'/')

def view(request, slugname):
    try:
        bar = Bar.objects.get(slugname=slugname)
    except Bar.DoesNotExist:
        raise Http404

    bar_constants = (
        (u'Wystrój wnętrza',  u'Oceń czy wnętrze lokalu jest zrobione gustownie i ze smakiem. Czy wystrój odpycha czy przyciąga swym wyglądem? 1 oznacza obskurny wygląd, a 10 miejsce na którym można zawiesić oko.'),
        (u'Wystrój na zewnątrz', u'Oceń czy elewacja budynku jest zadbana. Czy budynek  zachęca do wejścia do środka? 1 oznacza obskurny wygląd, a 10 budynek do którego aż się chce wejść.'),
        (u'Identyfikacja', u'Oceń czy lokal rzuca się w oczy. Czy od razu wiadomo o jaki lokal chodzi będąc w jego pobliżu? 1 oznacza, że lokal można znaleźć tylko z czyjąś pomocą, a 10 że już z daleka wiadomo, w które miejsce się kierować.'),
        (u'Okolica', u'Oceń czy lokal znajduje się w okolicy miłej dla oka lub pozwalającej na komfortowe spędzenie wieczoru. Czy w okolicy są inne lokale, w których można spotkać znajomych, są sklepy, przystanki i postoje taksówkowe ułatwiające pobyt w lokalu? 1 oznacza, że lokal jest w mało korzystnej okolicy gdzie jest brzydko lub po za lokalem nie ma nic innego, a 10 że lokal znajduje się w okolicy, która tętni swym własnym życiem.'),
        (u'Muzyka', u'Oceń puszczaną muzykę. Czy nie jest za głośna, niestosowna lub nie pasująca do klimatu lokalu? 1 oznacza, że muzyka jest kompletnie nie na miejscu, jest bardzo głośna lub nie pasuje do lokalu, a 10 że puszczana muzyka jest idealnym tłem dla lokalu.'),
        (u'Ceny', u'Oceń czy ceny w lokalu są do zaakceptowania. Czy ceny są konkurencyjne w porównaniu do innych lokali? 1 oznacza, że ceny są całkowicie nie do zaakceptowania, a 10 że ceny w lokalu są bardzo niskie.'),
        (u'Lokalizacja', u'Oceń czy do lokalu można trafić w łatwy sposób. Czy można tam dotrzeć komunikacją miejską lub samochodem? 1 oznacza, że do lokalu można trafić tylko z mapą w rękach i jedynie na piechotę, a 10 że każdy kto chce trafić do lokalu zrobi to za pierwszym razem.'),
        (u'Parking', u'Oceń czy lokal posiada własny parking lub czy można w jego okolicy zaparkować. 1 oznacza, że parkingu nie ma i nie ma gdzie zostawić auta, a 10 że lokal posiada własny parking, na którym zawsze znajdzie się miejsce.'),
        (u'Bezpieczeństwo', u'Oceń czy w lokalu jest bezpiecznie. Czy lokal zatrudnia ochronę i czy w ogóle jest taka potrzeba? 1 oznacza, że w lokalu regularnie mają miejsce zamieszki i bójki, a 10 że w lokalu nigdy nie dochodzi do żadnych incydentów bez względu na to czy ochrona jest czy jej nie ma.'),
        (u'Personel', u'Oceń czy obsługa jest miła i profesjonalna. Czy personel jest przeszkolony i daje klientowi poczucie, że jest mile widziany? 1 oznacza, że zachowanie personelu jest dosłownie przykre, a 10 że pracujący w lokalu ludzie są świetną wizytówką lokalu.'),
        (u'Alkohol', u'Oceń serwowany alkohol w lokalu. Czy oprócz piwa są dostępne inne alkohole i czy jest możliwość zamówienia drinka? 1 oznacza, że w lokalu nie ma alkoholu lub to co jest do wyboru nie powala na kolana, a 10 że wybór jest tak szeroki, że każdy znajdzie coś dla siebie.'),
        (u'Jedzenie', u'Oceń jedzenie serwowane w lokalu. Czy w ogóle można coś przekąsić, a jeśli tak to czy jedzenie jest dobre, a wybór duży? 1 oznacza, że lokal nie oferuje żadnego rodzaju przekąsek ani jedzenia, a 10 że oprócz baru lokal posiada bardzo dobrą i bogatą kuchnię.'),
        (u'Czystość', u'Oceń czy personel lokalu dba o jego czystość. Czy stoliki są regularnie ścierane, a ubikacja nie odpycha swym wyglądem? 1 oznacza, że czystość lokalu ma wiele do życzenia, a 10 że panującej higienie nic nie można zarzucić.'),
        (u'Tłok', u'Oceń dostępne miejsce w lokalu. Czy w lokalu często przebywa dużo ludzi? 1 oznacza, że trzeba mieć szczęście by trafić na wolne stoliki, a 10 że zawsze znajdzie się miejsce dla kolejnych klientów.'),
    )


    # Annotate bar_constants with identifier and marks - user-given and global average
    try:
        if request.user == None: raise Exception
        usermark = bar.marks.get(account=request.user)
    except:
        usermark = dict((('o'+str(x), None) for x in xrange(0, 14)))
    else:
        usermark = dict((('o'+str(x), usermark.__dict__['o'+str(x)]) for x in xrange(0, 14)))   

    avgmark = bar.meta

    x = -1
    category_info = []
    for mark_name, mark_description in bar_constants:
        x += 1
        category_info.append((x, mark_name, mark_description, usermark['o'+str(x)], 
                              avgmark.__dict__['avg_o'+str(x)]))

    l10r = range(1, 11)
    
    
    events = bar.events.order_by('happens_on')[:3]
    frequenters = bar.frequenters.order_by('?')[:6]

    # Check if frequenter
    try:
        bar.frequenters.get(account=request.user)
    except:
        is_frequenter = False
    else:
        is_frequenter = True

    unknown_pnpt = bar.openhours_5_f == bar.openhours_5_t == ''
    unknown_sob = bar.openhours_sat_f == bar.openhours_sat_t == ''
    unknown_nie = bar.openhours_sun_f == bar.openhours_sun_t == ''


    if 'err_comment_too_fast' in request.session:
        del request.session['err_comment_too_fast']
        comment_too_fast = True
    else:
        comment_too_fast = False

    return render('bar/bar.html', request, bar=bar, CATEGORY_INFO=category_info, 
                  l10r=l10r, events=events, frequenters=frequenters,
                  unknown_mf=unknown_pnpt, unknown_sat=unknown_sob, unknown_sun=unknown_nie,
                  logged_in=request.user != None, is_frequenter=is_frequenter,
                  default_comment_text=DEFAULT_COMMENT_TEXT, comment_too_fast=comment_too_fast)
    
