from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

urlpatterns = patterns('trybar',
    # Examples:
    url(r'^$', 'main.views.index'),
    url(r'^login/$', 'account.views.login'),
    url(r'^logout/$', 'account.views.logout'),
    url(r'^profile/$', 'account.views.profile'),
    url(r'^login/register/$', 'account.register.view'),
    url(r'^login/register/activate/$', 'account.register.activate'),
    
    # Actions for cron
    url(r'^admin/cron/regenerate_bar_ranking/', 'cron.actions.regenerate_bar_ranking'),
)

if settings.DEBUG:
    urlpatterns = patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    ) + urlpatterns

# Generic idea:
#       /           - page root
#       /login/, /logout/       -   verifying
#       /profile/x/             -   somebodys profile
#       /profile/               -   my profile
#       /now/                   -   aktualnosci
#       /bar/xx/                -   bar management stuff
#       /admin/                 -   admin shit