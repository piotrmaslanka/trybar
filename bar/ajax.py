# coding=UTF-8
from django import forms
from django.http import HttpResponse
from django.shortcuts import redirect
from trybar.account import must_be_logged
from trybar.account.models import Account
from datetime import datetime, timedelta
from trybar.bar.models import SingleBarMark, Bar, BAR_MARKS_COUNT, BarFrequenter, BarAbuse, BarComment
from trybar.bar.bar import DEFAULT_COMMENT_TEXT
from trybar.scoring import BAR_COMMENT_ADDED, score_for
from trybar.accnews import RT_IS_FREQUENTER, RT_NOT_FREQUENTER, RT_COMMENT_BAR, accnews_for
import json

@must_be_logged
def op(request, id):
    """
    if op == mark
    
        return JSON (current_average, current_mark_count, 
                     given_category_uservote, given_category_average)
    """
    try:
        bar = Bar.objects.get(id=id)
    except Bar.DoesNotExist:
        raise Http404    
        
    if 'op' not in request.GET:     # must be op
        return HttpResponse(status=400)
        
    if request.GET['op'] == 'mark':
        try:
            cat_id = int(request.GET['o'])
            if not (0 <= cat_id < BAR_MARKS_COUNT): raise Exception, 'Invalid category'            
            mark = request.GET['val']
            if mark == 'Z': mark = None
            else:
                mark = int(mark)            
                if not (1 <= mark <= 10): raise Exception, 'Invalid mark'
        except:
            return HttpResponse(status=400)
            
        meta = bar.meta
            
        try:
            sbm = SingleBarMark.objects.filter(bar=bar).get(account=request.user)
        except SingleBarMark.DoesNotExist:
            sbm = SingleBarMark(bar=bar, account=request.user)
            
            meta.mark_count += 1
        
        sbm.__dict__['o'+str(cat_id)] = mark
        sbm.save()
        
        meta.recalculate_single_category(cat_id)
        
        # WARNING! TEMPORARY MEASURE FOLLOWS
        from trybar.cron.actions import regenerate_bar_ranking
        regenerate_bar_ranking(None)

        return HttpResponse(json.dumps((meta.avg, meta.mark_count,
                                        sbm.__dict__['o'+str(cat_id)], 
                                        meta.__dict__['avg_o'+str(cat_id)])),
                            mimetype='application/json')
    elif request.GET['op'] == 'frequent':
        try:
            frq = bar.frequenters.get(account=request.user)
        except BarFrequenter.DoesNotExist:
            BarFrequenter(bar=bar, account=request.user).save()
            accnews_for(request.user, RT_IS_FREQUENTER, bar)
        else:
            frq.delete()
            accnews_for(request.user, RT_NOT_FREQUENTER, bar)
        return redirect('/bar/%s/' % (bar.slugname, ))
    elif request.GET['op'] == 'abuse':
        if 'description' not in request.POST:
            return HttpResponse(status=400)
        BarAbuse(bar=bar, account=request.user, description=request.POST['description']).save()
        return HttpResponse('OK')
    elif request.GET['op'] == 'comment':
        if 'content' not in request.POST:
            return redirect('/bar/%s/' % (bar.slugname, ))
        if request.POST['content'].strip() == DEFAULT_COMMENT_TEXT:
            return redirect('/bar/%s/' % (bar.slugname, ))
        
        # Limit: no faster than 15s
        try:
            lbc = BarComment.objects.filter(bar=bar).filter(account=request.user)[0]
        except:
            pass
        else:
            if (datetime.now() - lbc.made_on) < timedelta(0, 15):
                # too soon, limit in effect
                request.session['err_comment_too_fast'] = True
                return redirect('/bar/%s/' % (bar.slugname, ))

        bc = BarComment(bar=bar, account=request.user, content=request.POST['content'])
        try:
            bc.save()
        except:
            pass
        else:
            score_for(request.user, BAR_COMMENT_ADDED, bc)
            accnews_for(request.user, RT_COMMENT_BAR, bar)
        return redirect('/bar/%s/' % (bar.slugname, ))