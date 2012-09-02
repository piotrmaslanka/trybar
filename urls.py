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
    url(r'^bar/add/$', 'bar.add_bar.view'),

    url(r'^ranking/bars/$', 'ranking.bars.ranking_bars'),
    url(r'^ranking/bars/(?P<page>\d+?)/$', 'ranking.bars.ranking_bars'),
    url(r'^ranking/users/$', 'ranking.users.ranking_users'),
    url(r'^ranking/users/(?P<page>\d+?)/$', 'ranking.users.ranking_users'),

    url(r'^bar/(?P<id>\d+?)/ajax/$', 'bar.ajax.op'),
    url(r'^bar/(?P<slugname>.+?)/$', 'bar.bar.view'),
    # Actions for cron
    url(r'^admin/cron/regenerate_bar_ranking/', 'cron.actions.regenerate_bar_ranking'),
)

if settings.DEBUG:
    urlpatterns = patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
        (r'^uploads/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.UPLOAD_ROOT}),
    ) + urlpatterns

# Generic idea:
#       /           - page root
#       /login/, /logout/       -   verifying
#       /profile/x/             -   somebodys profile
#       /profile/               -   my profile
#       /now/                   -   aktualnosci
#       /bar/xx/                -   bar management stuff
#       /admin/                 -   admin shit