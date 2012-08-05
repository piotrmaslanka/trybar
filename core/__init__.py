from django.shortcuts import render_to_response

def render(template_path, request, **extras):
    pte = {'request': request}
    pte.update(extras)
    return render_to_response(template_path, pte)
    
    