# coding=UTF-8
from __future__ import division
from django.db import models
from datetime import datetime
from collections import defaultdict
from hashlib import sha1
from trybar.account.models import Account
from trybar.bar.models import Bar
from trybar.photo.models import Photo
from trybar.photo.upload import upload_as, RES_EVENT_POSTER, RES_EVENT_PHOTO, RES_EVENT_PARTNER

STARTING_AT = [ ('', 'Nieznane'),
 ('05:00', '05:00'), ('05:30', '05:30'), ('06:00', '06:00'), ('06:30', '06:30'),
 ('07:00', '07:00'), ('07:30', '07:30'), ('08:00', '08:00'), ('08:30', '08:30'),
 ('09:00', '09:00'), ('09:30', '09:30'), ('10:00', '10:00'), ('10:30', '10:30'),
 ('11:00', '11:00'), ('11:30', '11:30'), ('12:00', '12:00'), ('12:30', '12:30'),
 ('13:00', '13:00'), ('13:30', '13:30'), ('14:00', '14:00'), ('14:30', '14:30'),
 ('15:00', '15:00'), ('15:30', '15:30'), ('16:00', '16:00'), ('16:30', '16:30'),
 ('17:00', '17:00'), ('17:30', '17:30'), ('18:00', '18:00'), ('18:30', '18:30'),
 ('19:00', '19:00'), ('19:30', '19:30'), ('20:00', '20:00'), ('20:30', '20:30'),
 ('21:00', '21:00'), ('21:30', '21:30'), ('22:00', '22:00'), ('22:30', '22:30'),
 ('23:00', '23:00'), ('23:30', '23:30')]

class Event(models.Model):
    name = models.CharField(max_length=40, verbose_name=u'Nazwa imprezy')
    description = models.TextField(verbose_name=u'Opis')

    miniature = models.ForeignKey(Photo, related_name='DONTCARE1', default=None, null=True)

    slugname = models.SlugField(verbose_name=u'Nazwa URL')

    bar = models.ForeignKey(Bar, related_name='events')
    owner = models.ForeignKey(Account, related_name='events_owned')

    entry_cost = models.DecimalField(max_digits=4, decimal_places=2, default=0, verbose_name=u'Koszt wstepu')
    age_limit = models.IntegerField(null=True, default=None, verbose_name=u'Limit wieku')
    extra_info = models.TextField(verbose_name=u'Informacje dodatkowe')

    happens_on = models.DateField(verbose_name=u'Data startu')
    starts_on = models.CharField(max_length='5', blank=True, verbose_name=u'Czas startu')
    
    poster = models.ForeignKey(Photo, null=True, default=None, related_name='DONTCARE2')

class EventArtist(models.Model):
    event = models.ForeignKey(Event, related_name='artists')
    name = models.CharField(max_length=80)
    profile = models.CharField(max_length=100, blank=True, null=True, default=None)

# Marks are from 0 to 8, as is. Zero is not allowed. Use NULL if you need to signal "no mark"
EVENT_MARKS_COUNT = 9
   
class EventMeta(models.Model):    
    """This table contains data about a bar that will frequently change"""
    event = models.OneToOneField(Event, related_name='metadata')
    
    # Average marks
    mark_count = models.IntegerField(default=0)
    avg = models.FloatField(default=None, null=True)        # average from avg_o*

    avg_o0 = models.IntegerField(default=None, null=True)   # Muzyka
    avg_o1 = models.IntegerField(default=None, null=True)   # Występy
    avg_o2 = models.IntegerField(default=None, null=True)   # Bezpieczeństwo
    avg_o3 = models.IntegerField(default=None, null=True)   # Tłok
    avg_o4 = models.IntegerField(default=None, null=True)   # Klimat
    avg_o5 = models.IntegerField(default=None, null=True)   # Zabawa
    avg_o6 = models.IntegerField(default=None, null=True)   # Reklama
    avg_o7 = models.IntegerField(default=None, null=True)   # Dod. atrakcje
    avg_o8 = models.IntegerField(default=None, null=True)   # Prowadzący
    
    def recalculate_single_category(self, cat_id):
        """Recalculates single category. CAN BE DEPRECATED/REMOVED/RECODED. Saves instance."""
        marks = self.event.marks.all().only('o'+str(cat_id))
        vsum = 0
        vcnt = 0
        for vmark in [mark.__dict__['o'+str(cat_id)] for mark in marks]:
            if vmark == None: continue
            vsum += vmark
            vcnt += 1
        if vcnt < 0:        # TODO: remove on debug
            self.__dict__['avg_o'+str(cat_id)] = None
        else:
            self.__dict__['avg_o'+str(cat_id)] = round(vsum/vcnt)
            
        vsum = 0
        vcnt = 0
        for mark in [self.__dict__['avg_o'+str(x)] for x in xrange(0, EVENT_MARKS_COUNT)]:
            if mark != None:
                vsum += mark
                vcnt += 1
        if vcnt == 0:
            self.avg = None
        else:
            self.avg = vsum/vcnt
            
        self.save()
    
class SingleEventMark(models.Model):
    """Contains a single set of marks, issued by given user to a given bar"""

    event = models.ForeignKey(Event, related_name='marks')
    account = models.ForeignKey(Account, related_name='event_marks_issued')
    
    o0 = models.IntegerField(default=None, null=True)   # Muzyka
    o1 = models.IntegerField(default=None, null=True)   # Występy
    o2 = models.IntegerField(default=None, null=True)   # Bezpieczeństwo
    o3 = models.IntegerField(default=None, null=True)   # Tłok
    o4 = models.IntegerField(default=None, null=True)   # Klimat
    o5 = models.IntegerField(default=None, null=True)   # Zabawa
    o6 = models.IntegerField(default=None, null=True)   # Reklama
    o7 = models.IntegerField(default=None, null=True)   # Dod. atrakcje
    o8 = models.IntegerField(default=None, null=True)   # Prowadzący

class EventPhoto(models.Model):
    event = models.ForeignKey(Event, related_name='photos')
    photo = models.ForeignKey(Photo)

    @staticmethod
    def craft(ufo, event):
        """@type ufo: UploadedFileObject from a PictureField
        @type event: bound Event instance"""
        pic = upload_as(ufo, RES_EVENT_PHOTO)
        b = EventPhoto(event=event, photo=pic)
        b.save()
        return b

class Partner(models.Model):
    event = models.ForeignKey(Event, related_name='partners')
    website = models.CharField(max_length=255)        
    photo = models.ForeignKey(Photo)

    cache_photo_height = models.IntegerField(default=None, null=True)

    @staticmethod 
    def craft(ufo, event, url):
        pic = upload_as(ufo, RES_EVENT_PARTNER)
        b = Partner(event=event, website=url, photo=pic)
        b.save()
        return b


    def delete(self):
        self.photo.delete()
        super(Partner, self).delete()

class InterestedUser(models.Model):
    account = models.ForeignKey(Account, related_name='events_interested_in')
    event = models.ForeignKey(Event, related_name='interested_users')

class EventAbuse(models.Model):
    event = models.ForeignKey(Event, related_name='abuses')
    account = models.ForeignKey(Account, related_name='event_abuses_reported')
    reported = models.DateTimeField(default=datetime.now)
    description = models.TextField(blank=True)
    
class EventComment(models.Model):
    event = models.ForeignKey(Event, related_name='comments')
    account = models.ForeignKey(Account, related_name='event_comments_made')
    content = models.TextField()
    made_on = models.DateTimeField(default=datetime.now)
    
    class Meta:
        ordering = ['-made_on']    