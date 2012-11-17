# coding=UTF-8
from django.shortcuts import redirect
from trybar.core import render
from datetime import datetime, timedelta
from trybar.account import must_be_logged
from trybar.barevent.models import Event, EVENT_MARKS_COUNT, SingleEventMark, InterestedUser, \
                                   EventComment, EventAbuse
from django.http import Http404, HttpResponse
from trybar.main.models import News
from trybar.accnews import RT_INTRSTD_IN_EVENT, RT_NOT_INTRSTD_IN_EVENT, accnews_for, RT_COMMENT_EVENT
from trybar.scoring import BAR_EVENT_COMMENT_ADDED, score_for

DEFAULT_COMMENT_TEXT = u'Napisz co myślisz o tej imprezie...'

@must_be_logged
def op(request, slugname, evtname):
    try:
        event = Event.objects.filter(bar__slugname=slugname).get(slugname=evtname)
    except Event.DoesNotExist:
        raise Http404
    """
    if op == mark
    
        return JSON (current_average, current_mark_count, 
                     given_category_uservote, given_category_average)
    """
        
    if 'op' not in request.GET:     # must be op
        return HttpResponse(status=400)
        
    if request.GET['op'] == 'mark':
        try:
            cat_id = int(request.GET['o'])
            if not (0 <= cat_id < EVENT_MARKS_COUNT): raise Exception, 'Invalid category'            
            mark = request.GET['val']
            if mark == 'Z': mark = None
            else:
                mark = int(mark)            
                if not (1 <= mark <= 10): raise Exception, 'Invalid mark'
        except:
            return HttpResponse(status=400)
            
        meta = event.metadata
            
        try:
            sbm = SingleEventMark.objects.filter(event=event).get(account=request.user)
        except SingleBarMark.DoesNotExist:
            sbm = SingleEventMark(event=event, account=request.user)
            
            meta.mark_count += 1
        
        sbm.__dict__['o'+str(cat_id)] = mark
        sbm.save()
        
        meta.recalculate_single_category(cat_id)
        
        return HttpResponse(json.dumps((meta.avg, meta.mark_count,
                                        sbm.__dict__['o'+str(cat_id)], 
                                        meta.__dict__['avg_o'+str(cat_id)])),
                            mimetype='application/json')
    elif request.GET['op'] == 'interested':
        try:
            frq = event.interested_users.get(account=request.user)
        except InterestedUser.DoesNotExist:
            InterestedUser(event=event, account=request.user).save()
            accnews_for(request.user, RT_INTRSTD_IN_EVENT, event)
        else:
            frq.delete()
            accnews_for(request.user, RT_NOT_INTRSTD_IN_EVENT, event)
        return redirect('/bar/%s/%s/' % (event.bar.slugname, event.slugname))
    elif request.GET['op'] == 'abuse':
        if 'description' not in request.POST:
            return HttpResponse(status=400)
        EventAbuse(event=event, account=request.user, description=request.POST['description']).save()
        return HttpResponse('OK')
    elif request.GET['op'] == 'comment':
        if 'content' not in request.POST:
            return redirect('/bar/%s/%s/' % (event.bar.slugname, event.slugname))
        if request.POST['content'].strip() == DEFAULT_COMMENT_TEXT:
            return redirect('/bar/%s/%s/' % (event.bar.slugname, event.slugname))
        
        # Limit: no faster than 15s
        try:
            lbc = EventComment.objects.filter(event=event).filter(account=request.user)[0]
        except:
            pass
        else:
            if (datetime.now() - lbc.made_on) < timedelta(0, 15):
                # too soon, limit in effect
                request.session['err_comment_too_fast'] = True
                return redirect('/bar/%s/%s/' % (event.bar.slugname, event.slugname))

        bc = EventComment(event=event, account=request.user, content=request.POST['content'])
        try:
            bc.save()
        except:
            pass
        else:
            score_for(request.user, BAR_EVENT_COMMENT_ADDED, bc)
            accnews_for(request.user, RT_COMMENT_EVENT, event)
        return redirect('/bar/%s/%s/' % (event.bar.slugname, event.slugname))


def view_event(request, slugname, evtname):
    try:
        event = Event.objects.filter(bar__slugname=slugname).get(slugname=evtname)
    except Event.DoesNotExist:
        raise Http404


    evt_constants = (
        (u'Muzyka',  u'LOLO'),
        (u'Występy', u'HEHE'),
        (u'Bezpieczeństwo', u'OMGWTFY'),
        (u'Tłok', u'xaxa'),
        (u'Klimat', u'xoxo'),
        (u'Zabawa', u'ala ma kota'),
        (u'Reklama', u'trybar + events'),
        (u'Dod. atrakcje', u'Codename "losing my religion"'),
        (u'Prowadzący', u'znaczy że ktoś dostanie wpierdol...'),
    )


    # Annotate bar_constants with identifier and marks - user-given and global average
    try:
        if request.user == None: raise Exception
        usermark = event.marks.get(account=request.user)
    except:
        usermark = dict((('o'+str(x), None) for x in xrange(0, 14)))
    else:
        usermark = dict((('o'+str(x), usermark.__dict__['o'+str(x)]) for x in xrange(0, 14)))   

    avgmark = event.metadata

    x = -1
    category_info = []
    for mark_name, mark_description in evt_constants:
        x += 1
        category_info.append((x, mark_name, mark_description, usermark['o'+str(x)], 
                              avgmark.__dict__['avg_o'+str(x)]))

    try:                                        # Check whether user is interested in this event
        event.interested_users.get(account=request.user)
    except:
        is_interested = False
    else:
        is_interested = True

    interesteds = event.interested_users.order_by('?')[:12]

    if 'err_comment_too_fast' in request.session:
        del request.session['err_comment_too_fast']
        comment_too_fast = True
    else:
        comment_too_fast = False


    return render('barevent/event.html', request, event=event, is_interested=is_interested, CATEGORY_INFO=category_info,
                                                  l10r=range(1, 11), interesteds=interesteds, comment_too_fast=comment_too_fast)

