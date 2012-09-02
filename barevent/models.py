# coding=UTF-8
from __future__ import division
from django.db import models
from django.core.validators import MinLengthValidator, RegexValidator
from datetime import datetime
from collections import defaultdict
from hashlib import sha1
from trybar.account.models import Account
from trybar.bar.models import Bar
from trybar.photo.models import Photo
from trybar.photo.upload import upload_as, RES_EVENT_LOGO, RES_EVENT_PHOTO

class Event(models.Model):
    name = models.CharField(max_length=40, verbose_name=u'Nazwa baru')
    description = models.TextField(verbose_name=u'Opis')

    bar = models.ForeignKey(Bar, related_name='events')
    owner = models.ForeignKey(Account, related_name='events_owned')

    happens_on = models.DateTimeField()
    
    logo = models.ForeignKey(Photo)

    def delete(self):
        self.marks.delete()         # Delete all marks
        self.metadata.delete()   # Delete metadata
        super(Event, self).delete()   # Delete self
    
# Marks are from 1 to 10, as is. Zero is not allowed. Use NULL if you need to signal "no mark"
EVENT_MARKS_COUNT = 1
   
class EventMeta(models.Model):    
    """This table contains data about a bar that will frequently change"""
    event = models.OneToOneField(Event, related_name='metadata')
    
    # Average marks
    mark_count = models.IntegerField(default=0)
    avg = models.FloatField(default=None, null=True)        # average from avg_o*

    avg_o0 = models.IntegerField(default=None, null=True)   # Wystrój wnętrza
    
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
        for mark in [self.__dict__['avg_o'+str(x)] for x in xrange(0, 14)]:
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
    
    o0 = models.IntegerField(default=None, null=True)

class EventPhoto(models.Model):
    event = models.ForeignKey(Event, related_name='photos')
    photo = models.ForeignKey(Photo)

    @staticmethod
    def craft(ufo, bar):
        """@type ufo: UploadedFileObject from a PictureField
        @type bar: bound Event instance"""
        pic = upload_as(ufo, RES_EVENT_PHOTO)
        b = EventPhoto(event=event, photo=pic)
        b.save()
        return b