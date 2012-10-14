from trybar.account.models import Account, AccountMeta, Shout
import json
from django.http import HttpResponse
from datetime import datetime, timedelta


def shout(request):
    if request.user == None: return HttpResponse(status=403)
    if 'content' not in request.POST: return HttpResponse(status=400)
    if len(request.POST['content'].strip()) == 0: return HttpResponse(status=400)

    # Update last-ping
    meta = request.user.meta
    meta.last_ping = datetime.now()
    meta.save()

    for familiar in request.user.familiar_set:
        Shout(sender=request.user, recipient=familiar, content=request.POST['content'].strip()).save()

    Shout(sender=request.user, recipient=request.user, content=request.POST['content'].strip()).save()

    return HttpResponse(status=200)


def ask(request):
    if request.user == None: return HttpResponse(status=403)

    # Update last-ping
    meta = request.user.meta
    meta.last_ping = datetime.now()
    meta.save()

    if 'since' in request.GET:
        try:
            try:
                datefrom = datetime.strptime(request.GET['since'], '%Y-%m-%dT%H:%M:%S.%f')
            except:
                datefrom = datetime.strptime(request.GET['since'], '%Y-%m-%dT%H:%M:%S')
            shouts = request.user.shouts_to.filter(when_made__gt=datefrom)
        except:
            shouts = request.user.shouts_to
    else:
        shouts = request.user.shouts_to

    shouts = shouts.order_by('-when_made')[:10].select_related('sender')
    # What an entry needs?
        # when-sent
        # content
        # sender's login
        # sender's ping state

    results = []
    for shout in shouts:
        results.append((shout.when_made.strftime("%H:%M"), shout.content, shout.sender.login, 
                (datetime.now() - shout.sender.meta.last_ping) < timedelta(0, 60*5)))

    results.reverse()

    if len(results) == 0:
        return HttpResponse(json.dumps((datetime.now().isoformat(), None)), content_type='application/json')
    else:
        return HttpResponse(json.dumps((shouts[0].when_made.isoformat(), results)), content_type='application/json')
        