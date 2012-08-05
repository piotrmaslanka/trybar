# coding=UTF-8
from django.db import models
from django.core.validators import MinLengthValidator, RegexValidator
from datetime import datetime
from hashlib import sha1
from trybar.core.fixtures import VOIVODESHIP_CHOICES

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

class Familiar(models.Model):
    befriender = models.ForeignKey(Account, related_name='befriender_set')
    befriendee = models.ForeignKey(Account, related_name='befriendee_set')
    made_on = models.DateTimeField(default=datetime.now)
    confirmed = models.BooleanField(default=False)


class AccountMeta(models.Model):
    account = models.ForeignKey(Account, related_name='metadata')

    rank = models.IntegerField()    # 0 means 'totally outta ranking'
    score = models.IntegerField()

    def regenerate_score(self):
        """Recalculates score field. Saves this instance"""
        self.score = sum([x.amount for x in self.account.scores], 0)
        self.save()

class Score(models.Model):          # handled by trybar.account.scoring, refer there for docs
    scorer = models.ForeignKey(Account, related_name='scores')
    scored_for = models.IntegerField()
    amount = models.IntegerField()
    scored_on = models.DateTimeField(default=datetime.now)
    refer_1 = models.IntegerField()         # Universal Foreign Key #1
    refer_2 = models.IntegerField()         # Universal Foreign Key #2