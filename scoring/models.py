from datetime import datetime
from django.db import models
from trybar.account.models import Account, AccountPhoto, AccountPhotoComment
from trybar.bar.models import Bar, BarPhoto, BarComment
from trybar.barevent.models import EventComment, Event, EventPhoto
from trybar.main.models import NewsComment

class Scoring(models.Model):
    account = models.ForeignKey(Account)
    score = models.IntegerField(default=0)
    scored_on = models.DateTimeField(default=datetime.now)

    class Meta:
    	abstract = True

class BarAdded(Scoring):
    bar = models.ForeignKey(Bar)

class BarPhotoAdded(Scoring):
	barphoto = models.ForeignKey(BarPhoto)

class AccountPhotoAdded(Scoring):
    accountphoto = models.ForeignKey(AccountPhoto)

class AccountPhotoCommentAdded(Scoring):
    comment = models.ForeignKey(AccountPhotoComment)

class BarCommentAdded(Scoring):
	barcomment = models.ForeignKey(BarComment)

class NewsCommentAdded(Scoring):
    newscomment = models.ForeignKey(NewsComment)

class BarEventCommentAdded(Scoring):
    eventcomment = models.ForeignKey(EventComment)

class BarEventAdded(Scoring):
    event = models.ForeignKey(Event)

class BarEventPhotoAdded(Scoring):
    eventphoto = models.ForeignKey(EventPhoto)

class Manual(Scoring):
    reason = models.TextField()

