from trybar.scoring.models import *
from datetime import datetime

BAR_ADDED = 0
BAR_PHOTO_ADDED = 1
BAR_COMMENT_ADDED = 2
NEWS_COMMENT_ADDED = 3
ACCOUNT_PHOTO_ADDED = 4
ACCOUNT_PHOTO_COMMENT_ADDED = 5
BAR_EVENT_COMMENT_ADDED = 6
BAR_EVENT_ADDED = 7
BAR_EVENT_PHOTO_ADDED = 8

standard_pointing = {
	BAR_ADDED: 5,
	BAR_PHOTO_ADDED: 10,
	BAR_COMMENT_ADDED: 1,
	NEWS_COMMENT_ADDED: 1,
	ACCOUNT_PHOTO_ADDED: 3,
	ACCOUNT_PHOTO_COMMENT_ADDED: 1,	
	BAR_EVENT_COMMENT_ADDED: 1,
	BAR_EVENT_ADDED: 10,
	BAR_EVENT_PHOTO_ADDED: 5,
}

def recalculate_score_for(account):
	"""Performs a total score recalculation. Saves the meta"""
	meta = account.meta
	score = 0
	for s in BarAdded.objects.filter(account=account):
		score += s.score
	for s in BarPhotoAdded.objects.filter(account=account):
		score += s.score
	for s in BarCommentAdded.objects.filter(account=account):
		score += s.score
	for s in NewsCommentAdded.objects.filter(account=account):
		score += s.score
	for s in AccountPhotoAdded.objects.filter(account=account):
		score += s.score
	for s in AccountPhotoCommentAdded.objects.filter(account=account):
		score += s.score
	for s in BarEventCommentAdded.objects.filter(account=account):
		score += s.score
	for s in BarEventAdded.objects.filter(account=account):
		score += s.score
	for s in BarEventPhotoAdded.objects.filter(account=account):
		score += s.score
	for s in Manual.objects.filter(account=account):
		score += s.score

	meta.score = score
	meta.save()

def last_monthly_score_for(account):
	"""Calculate last month's score for given user"""
	k = datetime.now()
	sm = datetime(k.year, k.month, 1, 0, 0)

	score = 0
	for s in BarAdded.objects.filter(account=account).filter(scored_on__gt=sm):
		score += s.score
	for s in BarPhotoAdded.objects.filter(account=account).filter(scored_on__gt=sm):
		score += s.score
	for s in BarCommentAdded.objects.filter(account=account).filter(scored_on__gt=sm):
		score += s.score
	for s in NewsCommentAdded.objects.filter(account=account).filter(scored_on__gt=sm):
		score += s.score
	for s in AccountPhotoAdded.objects.filter(account=account).filter(scored_on__gt=sm):
		score += s.score
	for s in AccountPhotoCommentAdded.objects.filter(account=account).filter(scored_on__gt=sm):
		score += s.score
	for s in BarEventCommentAdded.objects.filter(account=account).filter(scored_on__gt=sm):
		score += s.score
	for s in BarEventAdded.objects.filter(account=account).filter(scored_on__gt=sm):
		score += s.score
	for s in BarEventPhotoAdded.objects.filter(account=account).filter(scored_on__gt=sm):
		score += s.score
	for s in Manual.objects.filter(account=account).filter(scored_on__gt=sm):
		score += s.score

	return score

def score_for(account, scoretype, *args, **kwargs):
	kwargs['account'] = account
	kwargs['score'] = standard_pointing[scoretype]
	if scoretype == BAR_ADDED:
		BarAdded(bar=args[0], **kwargs).save()
	elif scoretype == BAR_PHOTO_ADDED:
		BarPhotoAdded(barphoto=args[0], **kwargs).save()
	elif scoretype == BAR_COMMENT_ADDED:
		BarCommentAdded(barcomment=args[0], **kwargs).save()
	elif scoretype == NEWS_COMMENT_ADDED:
		NewsCommentAdded(newscomment=args[0], **kwargs).save()
	elif scoretype == ACCOUNT_PHOTO_ADDED:
		AccountPhotoAdded(accountphoto=args[0], **kwargs).save()
	elif scoretype == ACCOUNT_PHOTO_COMMENT_ADDED:
		AccountPhotoCommentAdded(comment=args[0], **kwargs).save()
	elif scoretype == BAR_EVENT_COMMENT_ADDED:
		BarEventCommentAdded(eventcomment=args[0], **kwargs).save()
	elif scoretype == BAR_EVENT_ADDED:
		BarEventAdded(event=args[0], **kwargs).save()
	elif scoretype == BAR_EVENT_PHOTO_ADDED:
		BarEventPhotoAdded(eventphoto=args[0], **kwargs).save()

	ranking_dirty()

	account.meta._dscore(kwargs['score'])


def ranking_dirty():
	# TEMPORARY MEASURES FOLLOW. WILL SCREW DATABASE IF LOAD IS BIGGER
	from trybar.cron.actions import regenerate_user_ranking
	regenerate_user_ranking(None)