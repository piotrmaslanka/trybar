from trybar.scoring.models import *

BAR_ADDED = 0
BAR_PHOTO_ADDED = 1
BAR_COMMENT_ADDED = 2
NEWS_COMMENT_ADDED = 3

standard_pointing = {
	BAR_ADDED: 5,
	BAR_PHOTO_ADDED: 10,
	BAR_COMMENT_ADDED: 1,
	NEWS_COMMENT_ADDED: 1,
}

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

	account.meta._dscore(kwargs['score'])
