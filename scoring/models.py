from datetime import datetime
from django.db import models
from trybar.account.models import Account
from trybar.bar.models import Bar, BarPhoto, BarComment
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

class BarCommentAdded(Scoring):
	barcomment = models.ForeignKey(BarComment)

class NewsCommentAdded(Scoring):
    newscomment = models.ForeignKey(NewsComment)
