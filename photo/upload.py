from __future__ import division
import Image, ImageOps
from trybar.photo.models import Photo
from trybar.settings import UPLOAD_ROOT
#from os import fchmod

RES_AVATAR = ((130, 130), (84, 84), (137, 97))         # res ident: avatar
RES_BARPHOTO = ((112, None), (84, 84), (137, 97))      # res ident: barphoto
RES_BAR_LOGO = ((84, 84),)                 # res ident: barlogo
RES_BAR_GUEST = ((112, None), (84, 84), (137, 97))     # res ident: barguest
RES_PRIZES = ((84, 84), )                   # res ident: prize

RES_EVENT_LOGO = ((84, 84), (222, 124), )   # res ident: eventlogo
RES_EVENT_PHOTO = ((112, None), (84, 84))   # res ident: eventphoto

RES_ACCOUNT_PHOTO = ((112, None), (84, 84), (137, 97)) # res ident: accphoto

RES_BANNER = ((980, 150), ) # res ident: banner

def upload_as(ufo, resolutions):
    """@type ufo: UploadedFile
    @type resolutions: sequence of tuple(int, int)"""

    photo = Photo()
    photo.save()

    original = Image.open(ufo)
    original.load()

    width, height = original.size

    for resolution in resolutions:
        rx, ry = resolution

        if rx == None:    # need to calculate width
            rx = int(round(width/height * ry))
        elif ry == None:
            ry = int(round(height/width * rx))

        cp = ImageOps.fit(original, (rx, ry), Image.ANTIALIAS)
        cp.save(UPLOAD_ROOT+photo.path_to(*resolution), 'JPEG')

 #       k = open(UPLOAD_ROOT+photo.path_to(*resolution), 'rb')        
 #       fchmod(k.fileno(), 777)
 #       k.close()

    original.save(UPLOAD_ROOT+photo.path_to(), 'JPEG')
#    k = open(UPLOAD_ROOT+photo.path_to(), 'rb')
#    fchmod(k.fileno(), 777)
#    k.close()

    return photo