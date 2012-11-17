# coding=UTF-8
from __future__ import division
from django.db import models
from django.core.validators import MinLengthValidator, RegexValidator
from datetime import datetime
from collections import defaultdict
from trybar.account.models import Account
from trybar.photo.models import Photo
from trybar.photo.upload import upload_as, RES_BARPHOTO

# To be... improved. RTFM, Piotruś :)
BAR_OPEN_HOURS_FROM = [ ('', 'Nieznane'),
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
BAR_OPEN_HOURS_TO = [ ('', 'Nieznane'),
 ('17:00', '17:00'), ('17:30', '17:30'), ('18:00', '18:00'), ('18:30', '18:30'),
 ('19:00', '19:00'), ('19:30', '19:30'), ('20:00', '20:00'), ('20:30', '20:30'),
 ('21:00', '21:00'), ('21:30', '21:30'), ('22:00', '22:00'), ('22:30', '22:30'),
 ('23:00', '23:00'), ('23:30', '23:30'), ('00:00', '00:00'), ('00:30', '00:30'),
 ('01:00', '01:00'), ('01:30', '01:30'), ('02:00', '02:00'), ('02:30', '02:30'),
 ('03:00', '03:00'), ('03:30', '03:30'), ('04:00', '04:00'), ('04:30', '04:30'),
 ('05:00', '05:00'), ('05:30', '05:30'), ('06:00', '06:00')]

class Bar(models.Model):
    frontpage_type_display = models.BooleanField(default=False, verbose_name=u'Adres bezpośrednio z /')
        # DEPRECATED ^

    name = models.CharField(max_length=40, verbose_name=u'Nazwa baru')
    street = models.CharField(max_length=50, verbose_name=u'Ulica')
    city = models.CharField(max_length=50, verbose_name=u'Miasto')
    voivodeship = models.CharField(max_length=30)   # use with django.contrib.localflavor.pl.forms.PLProvinceSelect
       
    accepts_credit_cards = models.NullBooleanField(default=None, verbose_name=u'Przyjmuje karty kredytowe')
    wifi = models.NullBooleanField(default=None, verbose_name=u'Jest Wi-Fi')
    handicapped = models.NullBooleanField(default=None, verbose_name=u'Udogodnienia dla niepełnosprawnych')
    website = models.CharField(max_length=40, blank=True)
    
    openhours_5_f = models.CharField(max_length=5, blank=True, null=True, choices=BAR_OPEN_HOURS_FROM, verbose_name=u'Otwarcie Pn-Pt')
    openhours_5_t = models.CharField(max_length=5, blank=True, null=True, choices=BAR_OPEN_HOURS_TO, verbose_name=u'Zamknięcie Pn-Pt')
    openhours_sat_f = models.CharField(max_length=5, blank=True, null=True, choices=BAR_OPEN_HOURS_FROM, verbose_name=u'Otwarcie Sob')
    openhours_sat_t = models.CharField(max_length=5, blank=True, null=True, choices=BAR_OPEN_HOURS_TO, verbose_name=u'Zamknięcie Sob')
    is_closed_sat = models.NullBooleanField(verbose_name=u'Zamknięty w soboty', default=None)
    openhours_sun_f = models.CharField(max_length=5, blank=True, null=True, choices=BAR_OPEN_HOURS_FROM, verbose_name=u'Otwarcie Nie')
    openhours_sun_t = models.CharField(max_length=5, blank=True, null=True, choices=BAR_OPEN_HOURS_TO, verbose_name=u'Zamknięcie Nie')
    is_closed_sun = models.NullBooleanField(verbose_name=u'Zamknięty w niedziele', default=None)
    
    is_darts = models.BooleanField(verbose_name=u'Rzutki')
    is_games = models.BooleanField(verbose_name=u'Gry')
    is_karaoke = models.BooleanField(verbose_name=u'Karaoke')
    is_dancing = models.BooleanField(verbose_name=u'Dancing')
    is_billard = models.BooleanField(verbose_name=u'Bilard')
    is_tv = models.BooleanField(verbose_name=u'TV')

    description = models.TextField(verbose_name=u'Opis', blank=True)
    
    owner = models.ForeignKey(Account, related_name='bars_owned')

    slugname = models.SlugField(verbose_name=u'Nazwa URL')
        # not null if allowed to be displayed up front
    slugname_up_front = models.SlugField(verbose_name=u'Nazwa URL /', default=None, null=True)

    logo = models.ForeignKey(Photo, default=None, null=True)

    def delete(self):
        self.marks.delete()         # Delete all marks
        self.metadata.delete()   # Delete metadata
        super(Bar, self).delete()   # Delete self
    
    def get_representative_photo(self):
        """Returns a Photo object or None"""
        photos = self.photos.all()
        if photos.count() == 0: return None
        try:
            return photos.get(representative=True).photo
        except:
            return photos[0].photo

# Mark IDs, and meaning   
BAR_MARKS_COUNT = 14
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

# Marks are from 0 to 13, as is. Zero is not allowed. Use NULL if you need to signal "no mark"
    
class BarMeta(models.Model):    
    """This table contains data about a bar that will frequently change"""
    bar = models.OneToOneField(Bar, related_name='meta')
    rank = models.IntegerField(verbose_name=u'Pozycja w rankingu', null=True)   # if null, bar won't be displayed in ranking    
    
    # Average marks
    mark_count = models.IntegerField(default=0)
    avg = models.FloatField(default=None, null=True)        # average from avg_o*

    avg_o0 = models.IntegerField(default=None, null=True)   # Wystrój wnętrza
    avg_o1 = models.IntegerField(default=None, null=True)   # Wystrój na zewnątrz
    avg_o2 = models.IntegerField(default=None, null=True)   # Identyfikacja
    avg_o3 = models.IntegerField(default=None, null=True)   # Okolica
    avg_o4 = models.IntegerField(default=None, null=True)   # Muzyka
    avg_o5 = models.IntegerField(default=None, null=True)   # Ceny
    avg_o6 = models.IntegerField(default=None, null=True)   # Lokalizacja
    avg_o7 = models.IntegerField(default=None, null=True)   # Parking
    avg_o8 = models.IntegerField(default=None, null=True)   # Bezpieczeństwo
    avg_o9 = models.IntegerField(default=None, null=True)   # Personel
    avg_o10 = models.IntegerField(default=None, null=True)  # Alkohol
    avg_o11 = models.IntegerField(default=None, null=True)  # Jedzenie
    avg_o12 = models.IntegerField(default=None, null=True)  # Czystość
    avg_o13 = models.IntegerField(default=None, null=True)  # Tłok
    
    def regenerate_marks(self):
        """Loads all marks for given bar and regenerates it's avg_o* fields. Saves this instance.
        USED ONLY BY CRON, AND VERY VERY POSSIBLE THAT IT WILL BE EVICTED REAL SOON"""
        indices = range(0, BAR_MARKS_COUNT)      # indices for elements
        amounts = defaultdict(lambda: 0)   # dict (indice=>amount of occurences)
        sums = defaultdict(lambda: 0)   # dict (indice=>sum of marks)


        self.mark_count = self.bar.marks.all().count()
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
            if amounts[index] > 0:      # Average can (almost) always be calculated
                avgmark[index] = round(sums[index] / amounts[index])
            else:
                avgmark[index] = None
                
            self.__dict__['avg_o'+str(index)] = avgmark[index]
        
        # Calculate bar-average
        not_null_value_table = [value for index, value in avgmark.iteritems() if value != None]
        amount_of_marks = len(not_null_value_table) # Amount of not-null averages
        
        if amount_of_marks < 1:     # There is no meaningful averages
            self.avg = None
        else:
            self.avg = sum(not_null_value_table) / amount_of_marks

        # Save this instance
        self.save()
    
    def recalculate_single_category(self, cat_id):
        """Recalculates single category. CAN BE DEPRECATED/REMOVED/RECODED. Saves instance."""
        marks = self.bar.marks.all().only('o'+str(cat_id))
        vsum = 0
        vcnt = 0
        for vmark in [mark.__dict__['o'+str(cat_id)] for mark in marks]:
            if vmark == None: continue
            vsum += vmark
            vcnt += 1
        if vcnt == 0:        # TODO: remove on debug
            self.__dict__['avg_o'+str(cat_id)] = None
        else:
            self.__dict__['avg_o'+str(cat_id)] = round(vsum/vcnt)
            
        vsum = 0
        vcnt = 0
        for mark in [self.__dict__['avg_o'+str(x)] for x in xrange(0, BAR_MARKS_COUNT)]:
            if mark != None:
                vsum += mark
                vcnt += 1
        if vcnt == 0:
            self.avg = None
        else:
            self.avg = vsum/vcnt
            
        self.save()
    
class SingleBarMark(models.Model):
    """Contains a single set of marks, issued by given user to a given bar"""

    bar = models.ForeignKey(Bar, related_name='marks')
    account = models.ForeignKey(Account, related_name='bar_marks_issued')
    
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

class BarPhoto(models.Model):
    bar = models.ForeignKey(Bar, related_name='photos')
    photo = models.ForeignKey(Photo)

    representative = models.BooleanField(default=False)

    @staticmethod
    def craft(ufo, bar):
        """@type ufo: UploadedFileObject from a PictureField
        @type bar: bound Bar instance"""
        pic = upload_as(ufo, RES_BARPHOTO)
        b = BarPhoto(bar=bar, photo=pic)
        b.save()
        return b
        
class BarFrequenter(models.Model):
    bar = models.ForeignKey(Bar, related_name='frequenters')
    account = models.ForeignKey(Account, related_name='frequenting_at')
    since = models.DateTimeField(default=datetime.now)
    
class BarAbuse(models.Model):
    bar = models.ForeignKey(Bar, related_name='abuses')
    account = models.ForeignKey(Account, related_name='bar_abuses_reported')
    reported = models.DateTimeField(default=datetime.now)
    description = models.TextField(blank=True)
    
class BarComment(models.Model):
    bar = models.ForeignKey(Bar, related_name='comments')
    account = models.ForeignKey(Account, related_name='bar_comments_made')
    content = models.TextField()
    made_on = models.DateTimeField(default=datetime.now)
    
    class Meta:
        ordering = ['-made_on']