# coding=UTF-8
from __future__ import division
from django.db import models
from datetime import datetime
from trybar.account.models import Account

class News(models.Model):
    title = models.CharField(max_length=80)
    content = models.TextField()
    published_on = models.DateTimeField(default=datetime.now)

    class Meta:
        ordering = ['-published_on']

    @staticmethod
    def get_news_for_sidebar():
        """Returns 3 latest news"""
        return News.objects.all()[:3]

class NewsComment(models.Model):
    account = models.ForeignKey(Account, related_name='news_comments_made')
    made_for = models.ForeignKey(News, related_name='comments')
    content = models.TextField()
    made_on = models.DateTimeField(default=datetime.now)

    class Meta:
        ordering = ['-made_on']
