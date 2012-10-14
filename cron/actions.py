"""
To be executed periodically
"""
from trybar.bar.models import BarMeta
from trybar.account.models import AccountMeta
from django.http import HttpResponse

def regenerate_bar_ranking(request):

    for meta in BarMeta.objects.all():
        meta.rank = None
        meta.save()

    ranked_metas = BarMeta.objects.filter(avg__isnull=False) \
                                  .exclude(mark_count__lt=3).only('avg').order_by('-avg')

    ranked_metas = list(ranked_metas)
    
    def update_if_makes_sense(meta, new_rank):
        if meta.rank != new_rank:
            meta.rank = new_rank
            meta.save()
    
    # Rank ranked bars
    for rank, meta in enumerate(ranked_metas):
        update_if_makes_sense(meta, rank+1)
        
    return HttpResponse('OK')

def regenerate_user_ranking(request):
    for meta in AccountMeta.objects.all():
        meta.rank = None
        meta.save()

    ranked_metas = AccountMeta.objects.only('score').order_by('-score')

    ranked_metas = list(ranked_metas)
    
    def update_if_makes_sense(meta, new_rank):
        if meta.rank != new_rank:
            meta.rank = new_rank
            meta.save()
    
    # Rank ranked bars
    for rank, meta in enumerate(ranked_metas):
        update_if_makes_sense(meta, rank+1)
        
    return HttpResponse('OK')    