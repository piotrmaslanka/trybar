from django import template
from trybar.adverts import get_ad_for
from trybar.settings import UPLOAD_PATH
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def html_ad(page):
	page = int(page)
	try:
		ad = get_ad_for(page)
	except:	# Given banner not found
		html = u'<div style="background-color: green; text-align: center; line-height: 150px;">GTFO %s</div>' % (page, )
		return mark_safe(html)

	html = u'<a href="/admin/ad/click/%s/" target="_blank"><img src="%s"></a>' % (
				ad.id,
				UPLOAD_PATH+ad.photo.path_to(980, 150),
			)

	return mark_safe(html)