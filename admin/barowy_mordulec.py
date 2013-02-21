# coding=UTF-8
from django.http import HttpResponse
from django.shortcuts import redirect
from trybar.account import must_be_logged
from trybar.bar.models import Bar
from django.shortcuts import render_to_response
from trybar.admin import must_be_admin


@must_be_logged
@must_be_admin
def kill(request, bid):
    bid = int(bid)
    try:
        b = Bar.objects.get(id=bid)
    except:
        return HttpResponse('NIE ZNAM TAKIEGO')
    else:
        b.delete()
        return HttpResponse('UBILEM GADA')

@must_be_logged
@must_be_admin
def view(request):
    return render_to_response('admin/barowski_mordulec.html', {'bars': Bar.objects.all()})