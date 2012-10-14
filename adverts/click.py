# coding=UTF-8
from __future__ import division
from trybar.adverts.models import AdBanner
from django.shortcuts import redirect

def click(request, id):
	try:
		ad = AdBanner.objects.get(id=int(id))
	except AdBanner.DoesNotExist:
		return redirect('/')

	ad.was_clicked()

	return redirect(ad.link)
