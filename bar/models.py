# coding=UTF-8
from __future__ import division
from django.db import models
from django.core.validators import MinLengthValidator, RegexValidator
from datetime import datetime
from collections import defaultdict
from hashlib import sha1
from trybar.account.models import Account

# To be... improved. RTFM, Piotruś :)
BAR_OPEN_HOURS = (('00:00', '00:00'), ('00:30', '00:30'), ('01:00', '01:00'), ('01:30', '01:30'), ('02:00', '02:00'), 
                                      ('02:30', '02:30'), ('03:00', '03:00'), ('03:30', '03:30'), ('04:00', '04:00'),
                                      ('04:30', '04:30'), ('05:00', '05:00'), ('05:30', '05:30'), ('06:00', '06:00'),
                                      ('06:30', '06:30'), ('07:00', '07:00'), ('07:30', '07:30'), ('08:00', '08:00'),
                                      ('08:30', '08:30'), ('09:00', '09:00'), ('09:30', '09:30'), ('10:00', '10:00'),)
class Bar(models.Model):
    slugname = models.SlugField(verbose_name=u'Nazwa URL')
    frontpage_type_display = models.BooleanField(default=False, verbose_name=u'Adres bezpośrednio z /')

    name = models.CharField(max_length=40, verbose_name=u'Nazwa baru')
    street = models.CharField(max_length=50, verbose_name=u'Ulica')
    city = models.CharField(max_length=50, verbose_name=u'Miasto')
    voivodeship = models.CharField(max_length=30)   # use with django.contrib.localflavor.pl.forms.PLProvinceSelect
       
    accepts_credit_cards = models.NullBooleanField(default=None, verbose_name=u'Przyjmuje karty kredytowe')
    wifi = models.NullBooleanField(default=None, verbose_name=u'Jest Wi-Fi')
    handicapped = models.NullBooleanField(default=None, verbose_name=u'Udogodnienia dla niepełnosprawnych')
    website = models.CharField(max_length=40, blank=True)
    
    openhours_5_f = models.CharField(max_length=5, blank=True, null=True, choices=BAR_OPEN_HOURS, verbose_name=u'Otwarcie Pn-Pt')
    openhours_5_t = models.CharField(max_length=5, blank=True, null=True, choices=BAR_OPEN_HOURS, verbose_name=u'Zamknięcie Pn-Pt')
    openhours_sat_f = models.CharField(max_length=5, blank=True, null=True, choices=BAR_OPEN_HOURS, verbose_name=u'Otwarcie Sob')
    openhours_sat_t = models.CharField(max_length=5, blank=True, null=True, choices=BAR_OPEN_HOURS, verbose_name=u'Zamknięcie Sob')
    openhours_sun_f = models.CharField(max_length=5, blank=True, null=True, choices=BAR_OPEN_HOURS, verbose_name=u'Otwarcie Nie')
    openhours_sun_t = models.CharField(max_length=5, blank=True, null=True, choices=BAR_OPEN_HOURS, verbose_name=u'Zamknięcie Nie')
    
    is_darts = models.BooleanField(verbose_name=u'Rzutki')
    is_games = models.BooleanField(verbose_name=u'Gry')
    is_karaoke = models.BooleanField(verbose_name=u'Karaoke')
    is_dancing = models.BooleanField(verbose_name=u'Dancing')
    is_billard = models.BooleanField(verbose_name=u'Bilard')
    is_tv = models.BooleanField(verbose_name=u'TV')

    description = models.TextField(verbose_name=u'Opis')
    
    owner = models.ForeignKey(Account, related_name='bars_owned')

    slugname = models.SlugField(verbose_name=u'Nazwa URL')
        # not null if allowed to be displayed up front
    slugname_up_front = models.SlugField(verbose_name=u'Nazwa URL /', default=None, null=True)

    def delete(self):
        self.marks.delete()         # Delete all marks
        self.metadata.delete()   # Delete metadata
        super(Bar, self).delete()   # Delete self
    
# Mark IDs, and meaning   
# 0 Wystrój wnętrza
# 1 Wystrój na zewnątrz
# 2 Identyfikacja
# 3 Okolica
# 4 Muzyka
# 5 Ceny
# 6 Lokalizacja
# 7 Parking
# 8 Bezpieczeństwo
# 9 Personel
#10 Alkohol
#11 Jedzenie
#12 Czystość
#13 Tłok    

# Marks are from 1 to 10, as is. Zero is not allowed. Use NULL if you need to signal "no mark"
    
class BarMeta(models.Model):    
    """This table contains data about a bar that will frequently change"""
    bar = models.OneToOneField(Bar, parent_link='metadata')
    rank = models.IntegerField(verbose_name=u'Pozycja w rankingu', null=True)   # if null, bar won't be displayed in ranking    
    
    # Average marks
    avg = models.FloatField(default=None, null=True)        # average from avg_o*
    avg_o0 = models.IntegerField(default=None, null=True)
    avg_o1 = models.IntegerField(default=None, null=True)
    avg_o2 = models.IntegerField(default=None, null=True)
    avg_o3 = models.IntegerField(default=None, null=True)
    avg_o4 = models.IntegerField(default=None, null=True)
    avg_o5 = models.IntegerField(default=None, null=True)
    avg_o6 = models.IntegerField(default=None, null=True)
    avg_o7 = models.IntegerField(default=None, null=True)
    avg_o8 = models.IntegerField(default=None, null=True)
    avg_o9 = models.IntegerField(default=None, null=True)
    avg_o10 = models.IntegerField(default=None, null=True)
    avg_o11 = models.IntegerField(default=None, null=True)
    avg_o12 = models.IntegerField(default=None, null=True)
    avg_o13 = models.IntegerField(default=None, null=True)
    
    def regenerate_marks(self):
        """Loads all marks for given bar and regenerates it's avg_o* fields. Saves this instance"""
        indices = range(0, 14)      # indices for elements
        amounts = defaultdict(lambda: 0)   # dict (indice=>amount of occurences)
        sums = defaultdict(lambda: 0)   # dict (indice=>sum of marks)

        # Fill-in amounts and sums
        for mark in self.bar.marks.all():
            for index in indices:
                value = mark.__dict__['o'+str(index)]
                if value != None:
                    amounts[index] += 1
                    sums[index] += value
        
        # Calculate average marks, and write them to our fields
        avgmark = {}
        for index in indices:
            if amounts[index] > 3:      # Needs at least 4 marks for a meaningful average
                avgmark[index] = round(sums[index] / amounts[index])
            else:
                avgmark[index] = None
                
            self.__dict__['avg_o'+str(index)] = avgmark[index]
        
        # Calculate bar-average
        not_null_value_table = [value for index, value in avgmark.iteritems() if value != None]
        amount_of_marks = len(not_null_value_table) # Amount of not-null averages
        
        if amount_of_marks < 8:     # There is no meaningful average
            self.avg = None
        else:
            self.avg = sum(not_null_value_table) / amount_of_marks
        
        # Save this instance
        self.save()
    
class SingleBarMark(models.Model):
    """Contains a single set of marks, issued by given user to a given bar"""

    bar = models.ForeignKey(Bar, related_name='marks')
    account = models.ForeignKey(Account, related_name='marks_issued')
    
    o0 = models.IntegerField(default=None, null=True)
    o1 = models.IntegerField(default=None, null=True)
    o2 = models.IntegerField(default=None, null=True)
    o3 = models.IntegerField(default=None, null=True)
    o4 = models.IntegerField(default=None, null=True)
    o5 = models.IntegerField(default=None, null=True)
    o6 = models.IntegerField(default=None, null=True)
    o7 = models.IntegerField(default=None, null=True)
    o8 = models.IntegerField(default=None, null=True)
    o9 = models.IntegerField(default=None, null=True)
    o10 = models.IntegerField(default=None, null=True)
    o11 = models.IntegerField(default=None, null=True)
    o12 = models.IntegerField(default=None, null=True)
    o13 = models.IntegerField(default=None, null=True)
