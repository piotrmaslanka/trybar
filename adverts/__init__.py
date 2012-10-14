from trybar.adverts.models import AdBanner
from django.db.models import Q
from datetime import datetime

def get_ad_for(page_type):
	"""
	Invoke if you mean to display this page. This WILL increment viewing counter.
	@param page_type: Type of page, as discerned in trybar.adverts.models.TARGET_PAGES"""
	ad = AdBanner.objects.filter(target_page=page_type) \
						 .filter(Q(run_until__gt=datetime.now()) | Q(run_until__isnull=True)) \
						 .order_by('times_viewed')[0]

	ad.was_viewed()

	return ad