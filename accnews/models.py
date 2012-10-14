# coding=UTF-8
from datetime import datetime
from django.db import models
from trybar.account.models import Account

RT_AVATAR_ADDED = 0			#									-	dodano avatar
RT_PRIVPHOTO_ADDED = 1		# arg1:<some private photo thingy>	-	dodano zdjecie prywatne
RT_COMMENT_PRIVGAL = 2		# arg1:Target Account 				-	skomentowano prywatna galerie
RT_COMMENT_BAR = 3			# arg1:Target Bar 					-	skomentowano bar
RT_IS_FREQUENTER = 4		# arg1:Target Bar 					-	user jest bywalcem
RT_NOT_FREQUENTER = 5		# arg1:Target Bar 					-	user nie jest bywalcem
RT_ADDED_EVENT = 6			# arg1:Target Event 				-	dodano impreze
RT_EVENTPHOTO_ADDED = 7		# arg1:Target EventPhoto, arg2:Target Event
							# dodano zdjecie do imprezy
RT_BARPHOTO_ADDED = 8		# arg1:Target BarPhoto, arg2: Target Bar
							# dodano zdjecie do baru
RT_COMMENT_EVENT = 9		# arg1:Target Event 				-	skomentowano impreze
RT_WILL_GO_EVENT = 10		# arg1:Target Event 				-	zaznaczyl ze idzie na impreze
RT_WONT_GO_EVENT = 11		# arg1:Target Event 				-	zaznaczyl ze nie idzie na impreze
RT_WAS_ON_EVENT	= 12		# arg1:Target Event 				-	zaznaczyl ze byl na imprezie
RT_WASNT_ON_EVENT = 13		# arg1:Target Event 				-	zaznaczyl ze nie byl na imprezie												
RT_ADDED_BAR = 14			# arg1:Target Bar 					-	dodano bar
RT_BECAME_FAMILIAR = 15		# arg1:Target Account 				-	zawarł znajomość z 
RT_UNBECAME_FAMILIAR = 16	# arg1:Target Account 				-	zerwano znajomość z

class AccNews(models.Model):
    whom = models.ForeignKey(Account, related_name='account_news')
    when = models.DateTimeField(default=datetime.now)
    who = models.ForeignKey(Account, related_name='_accnews_causer')

    report_type = models.PositiveSmallIntegerField()

    arg1 = models.PositiveIntegerField(default=0)
    arg2 = models.PositiveIntegerField(default=0)

    readed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-when']

    def was_readed(self):
        self.readed = True
        self.save()
        return u''