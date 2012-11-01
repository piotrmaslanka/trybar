# coding=UTF-8
from __future__ import division
from django.db import models
from trybar.photo.models import Photo
from datetime import datetime

TARGET_PAGES = (
	(0, u'Strona główna'),
	(1, u'Ranking użytkowników'),
	(2, u'Wyszukiwarka'),
	(3, u'Strona baru'),
	(4, u'Ranking barów'),
	(5, u'Rejestracja'),
	(6, u'Nagrody'),
	(7, u'Profil użytkownika'),
	(8, u'Logowanie, przypominanie hasła'),
	(9, u'Strony okazjonalne'),
	(10, u'FAQ, czym jest i kontakt'),
	(11, u'Niusy wszelakie'),
	(12, u'GPInfo'),
)

class AdBanner(models.Model):
	target_page = models.IntegerField(choices=TARGET_PAGES)
	link = models.TextField()
	times_viewed = models.IntegerField(default=0)
	times_clicked = models.IntegerField(default=0)
	run_until = models.DateTimeField(default=None, null=True)
	photo = models.ForeignKey(Photo)

	def was_viewed(self):
		"""Increments times_viewed. Saves this instance"""
		self.times_viewed += 1
		self.save()

	def was_clicked(self):
		"""Increments times_clicked. Saves this instance"""
		self.times_clicked += 1
		self.save()
