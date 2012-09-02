# coding=UTF-8
from django.db import models
from django.core.validators import MinLengthValidator, RegexValidator
from datetime import datetime
from hashlib import sha1
from trybar.core.fixtures import VOIVODESHIP_CHOICES
from trybar.photo.models import Photo
import itertools

class Account(models.Model):
    # Content
    name = models.CharField(max_length=20, verbose_name=u'Imię', blank=True)
    surname = models.CharField(max_length=25, verbose_name=u'Nazwisko', blank=True)
    login = models.CharField(max_length=25, verbose_name=u'Login', unique=True, validators=[MinLengthValidator(3)])
    password = models.CharField(max_length=40)  # SHA-1 hash of (login.encode('utf8')+password.encode('utf8'))
    city = models.CharField(max_length=25)
    voivodeship = models.CharField(max_length=30, choices=VOIVODESHIP_CHOICES)
    email = models.EmailField(max_length=254, verbose_name=u'Email')
    gadu = models.CharField(max_length=20, verbose_name=u'Nr GG', validators=[RegexValidator(r'\d+')], blank=True)
    phone = models.CharField(max_length=25, verbose_name=u'Nr tel.', blank=True)

    # Administratorial
    is_activated = models.BooleanField(default=False)
    created_on = models.DateTimeField(default=datetime.now)    
    avatar = models.ForeignKey(Photo, default=None, null=True)

    # Collective-ial
    familiar = models.ManyToManyField("Account", through='Familiar')

    def check_password(self, pwd):
        """Checks whether pwd matches current password"""
        return self.password == sha1(self.login.encode('utf8') + pwd.encode('utf8')).hexdigest()

    def set_password(self, new_pwd):
        """Sets password to a new password. Saves this instance"""
        self.password = sha1(self.login.encode('utf8') + new_pwd.encode('utf8')).hexdigest()        
        self.save()

    def activation_get_hash(self):
        """Returns an activation hash (the one that was sent in activation email).
        This string does not change during instance's lifetime - even if activated, or login changed.

        @return: a string representing the hash"""
        return sha1(self.created_on.strftime("%m.%Y-%d=%M:%H")+str(self.id)).hexdigest()

    def activate(self):
        """Perform everything needed to activate this user. Saves this instance."""
        self.is_activated = True
        self.save()

    @property
    def familiar_set(self):
        return itertools.chain(
          [acc.befriendee for acc in Familiar.objects.filter(befriender=self, confirmed=True) \
                                                    .select_related('befriendee')],
          [acc.befriender for acc in Familiar.objects.filter(befriendee=self, confirmed=True) \
                                                    .select_related('befriender')]
        )

class Familiar(models.Model):
    befriender = models.ForeignKey(Account, related_name='befriender_set')
    befriendee = models.ForeignKey(Account, related_name='befriendee_set')
    made_on = models.DateTimeField(default=datetime.now)
    confirmed = models.BooleanField(default=False)

class AccountMeta(models.Model):
    """Statistics"""
    account = models.OneToOneField(Account, related_name='meta')

    rank = models.IntegerField(null=True)    # null means 'totally outta ranking'
    score = models.IntegerField(default=0)

    @property
    def familiar_count(self):
        """Left as a property, as it may get cached in the DB in future"""
        return Familiar.objects.filter(befriender=self, confirmed=True).count() + \
               Familiar.objects.filter(befriender=self, confirmed=True).count()

    @property
    def frequenter_count(self):
        return self.account.frequenting_at.all().count()

    @property
    def bar_count(self):
        return self.account.bars_owned.all().count()

    def _dscore(self, score):
        """For usage by trybar.scoring"""
        self.score += score
        self.save()