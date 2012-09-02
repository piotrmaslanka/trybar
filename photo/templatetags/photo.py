from trybar.settings import UPLOAD_PATH
from trybar.photo.models import Photo
from django import template
register = template.Library()

@register.filter
def path(photo, res_str=''):
    """Samples of proper syntax:
        res_str=''          for native
        res_str="89,"       for autoadjust height
        res_str=",89"       for autoadjust width
        res_str="89,89"     for given width/height
    """
    
    if res_str.find(':') > -1:
        prev, res_str = res_str.split(':')
        # see photo/upload.py for nomenclature
    
    if photo in (None, ''):
        photo = Photo(id=prev)
    
    if res_str == '':
        return UPLOAD_PATH + photo.path_to()
       
    rx, ry = res_str.split(',')
    rx = None if rx == '' else int(rx)
    ry = None if ry == '' else int(ry)
    
    return UPLOAD_PATH + photo.path_to(rx, ry)
    
