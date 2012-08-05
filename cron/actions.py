"""
To be executed periodically
"""
from trybar.bar.models import BarMeta
from django.http import HttpResponse

def regenerate_bar_ranking(request):
    ranked_metas = list(BarMeta.objects.exclude(avg__isnull=True).only('avg').order_by('-avg'))
    
    def update_if_makes_sense(meta, new_rank):
        if meta.rank != new_rank:
            meta.rank = new_rank
            meta.save()
    
    # Rank ranked bars
    for rank, meta in enumerate(ranked_metas):
        update_if_makes_sense(meta, rank+1)
        
    return HttpResponse('OK')