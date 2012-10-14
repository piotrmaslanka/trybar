from django.shortcuts import render_to_response

def render(template_path, request, **extras):
    pte = {'request': request}
    pte.update(extras)
    return render_to_response(template_path, pte)
    
def gpinfo(request, info, url_next):
    return render('gpinfo.html', request, info=info, next_url=url_next)    