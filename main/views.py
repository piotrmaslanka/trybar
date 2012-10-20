from django import forms
from django.shortcuts import redirect
from trybar.core import render
from trybar.account.models import Account
from trybar.bar.models import Bar, BarPhoto
from trybar.main.models import News
from trybar.account import must_be_logged, standard_profile_page_dict
from trybar.barevent.models import Event
from trybar.accnews.models import *
from trybar.photo.templatetags.photo import path

def index(request):

    force_to_what_is_trybar = True
    if 'seen_whatis' in request.session: force_to_what_is_trybar = False
    if 'force_whatis' in request.COOKIES: force_to_what_is_trybar = False
    if force_to_what_is_trybar: return redirect('/what_is_trybar/')

    news = News.objects.all()[:3]

    top_3_bars = Bar.objects.filter(meta__mark_count__gt=2).order_by('meta__rank')[:3] 

    return render('main/index.html', request, news=News.objects.all()[:3],
                                              top_3_bars=top_3_bars)


RT_ADDED_EVENT = 6          # arg1:Target Event                 -   dodano impreze
RT_EVENTPHOTO_ADDED = 7     # arg1:Target EventPhoto, arg2:Target Event

@must_be_logged
def now(request):    
    spdict = standard_profile_page_dict(request) if request.user != None else {}

    entries = []    # list of tuple (AccNews object, arg1 or None, arg2 or None)
                    # those args are objectified first
    # Here we delete more than 30 last entries - because limiting this set 'on insertion'
    # would be too slow
    for olditem in request.user.account_news.all()[30:]: olditem.delete()
    # analyze now list and repack stuff
    for an in request.user.account_news.all():
        rt = an.report_type

        if rt in (RT_AVATAR_ADDED, ):
            stuff = ()
        elif rt in (RT_PRIVPHOTO_ADDED, RT_COMMENT_PRIVGAL):
            stuff = (AccountPhoto.objects.get(id=an.arg1), )
        elif rt in (RT_BECAME_FAMILIAR,
                    RT_UNBECAME_FAMILIAR):
            stuff = (Account.objects.get(id=an.arg1), )
        elif rt in (RT_COMMENT_BAR, RT_IS_FREQUENTER, RT_NOT_FREQUENTER, RT_ADDED_BAR):
            stuff = (Bar.objects.get(id=an.arg1), )
        elif rt in (RT_ADDED_EVENT, RT_COMMENT_EVENT, RT_WILL_GO_EVENT, RT_WONT_GO_EVENT, 
                    RT_WAS_ON_EVENT, RT_WASNT_ON_EVENT, ):
            stuff = (Event.objects.get(id=an.arg1), )
        elif rt in (RT_BARPHOTO_ADDED, ):
            stuff = (BarPhoto(id=an.arg1), Bar(id=an.arg2))
        elif rt in (RT_EVENTPHOTO_ADDED, ):
            raise NotImplementedError
        else:
            stuff = ()

        if len(stuff) == 0:
            entries.append((an, None, None))
        elif len(stuff) == 1:
            entries.append((an, stuff[0], None))
        elif len(stuff) == 2:
            entries.append((an, stuff[0], stuff[1]))
        else:
            raise Exception, '[Should never happen] You sick fuck'

    return render('main/now.html', request, accnew_items=entries,
                                            newsbar=News.get_news_for_sidebar(),
RT_AVATAR_ADDED = RT_AVATAR_ADDED, RT_PRIVPHOTO_ADDED= RT_PRIVPHOTO_ADDED, 
RT_COMMENT_PRIVGAL = RT_COMMENT_PRIVGAL, RT_COMMENT_BAR= RT_COMMENT_BAR,
RT_IS_FREQUENTER = RT_IS_FREQUENTER, RT_NOT_FREQUENTER= RT_NOT_FREQUENTER,
RT_ADDED_EVENT = RT_ADDED_EVENT, RT_EVENTPHOTO_ADDED = RT_EVENTPHOTO_ADDED,
RT_BARPHOTO_ADDED = RT_BARPHOTO_ADDED, RT_COMMENT_EVENT = RT_COMMENT_EVENT,
RT_WILL_GO_EVENT= RT_WILL_GO_EVENT, RT_WONT_GO_EVENT= RT_WONT_GO_EVENT, 
RT_WAS_ON_EVENT = RT_WAS_ON_EVENT, RT_WASNT_ON_EVENT = RT_WASNT_ON_EVENT,
RT_ADDED_BAR = RT_ADDED_BAR, RT_BECAME_FAMILIAR= RT_BECAME_FAMILIAR,
RT_UNBECAME_FAMILIAR = RT_UNBECAME_FAMILIAR, **spdict)