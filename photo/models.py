# coding=UTF-8
from django.db import models
from django.core.validators import MinLengthValidator, RegexValidator
from datetime import datetime
from trybar.settings import UPLOAD_ROOT
from hashlib import sha1
import os

POSSIBLE_RESOLUTIONS = ((130, 130), (84, 84), (112, None), 
                        (222, 124), (137, 97), (980, 150), 
                        (233, None), (176, None), ())  
    # empty means 'native'
    # single None means 'any value to keep aspect ratio'

from django.db.models.signals import pre_delete
from django.dispatch import receiver

@receiver(pre_delete)
def delete_photo(sender, instance, **kwargs):
    if sender == Photo:
        for resolution in POSSIBLE_RESOLUTIONS:
            path = instance.path_to(*resolution)
            try:
                os.unlink(UPLOAD_ROOT+path)
            except: # It doesn't have to exist at all
                pass

class Photo(models.Model):
    created_on = models.DateTimeField(default=datetime.now)    
    
    def as_ufo(self):
        """Returns native self as uploaded filelike object"""
        return open(UPLOAD_ROOT+self.path_to(), 'rb')

    def path_to(self, *resolution):
        """Returns relative path to file with given resolution. It may not exist, depending on type of this photo.
        Invoke like:
            photo.path_to(130, 130)
        and it will return a string:
            130x130/2.jpg
        if this photo's ID was 2.
        Arguments(resolution) must be contained in POSSIBLE_RESOLUTIONS.        
        This is a private method, because path will need to be prefixed with either ROOT (if we mean to operate on it), 
        or PATH (if we mean to serve it via HTTP).
        """            
        if resolution not in POSSIBLE_RESOLUTIONS: raise Exception, 'Check that %s is a valid resolution' % (resolution, )
         
        if resolution == (): return 'native/%s.jpg' % (self.id, )
            
        resolution = ['A' if k == None else k for k in resolution]        
        return '%sx%s/%s.jpg' % (resolution[0], resolution[1], self.id)
 
    def save(self, *args, **kwargs):
        super(Photo, self).save(*args, **kwargs)
