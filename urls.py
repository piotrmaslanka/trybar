from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

urlpatterns = patterns('trybar',
    url(r'^$', 'main.views.index'),
    url(r'^admin/otrzesiny/$', 'admin.ephemeris.add_otrzesiny_photo'),
    url(r'^otrzesiny/$', 'main.ephemeris.otrzesiny'),
    url(r'^building/$', 'main.static.building'),
    url(r'^rules/$', 'main.static.regulamin'),
    url(r'^contact/$', 'main.static.contact_form'),
    url(r'^what_is_trybar/$', 'main.static.what_is_trybar'),
    url(r'^urodziny/$', 'main.static.birthday'),
    url(r'^urodziny$', 'main.static.birthday'),
    url(r'^now/$', 'main.views.now'),
    url(r'^news/(?P<id>\d+?)/$', 'main.news.view'),
    url(r'^news/$', 'main.news.view_all'),
    url(r'^login/$', 'account.views.login'),
    url(r'^logout/$', 'account.views.logout'),
    url(r'^profile/$', 'account.views.profile'),
    url(r'^profile/ajax/ask/$', 'account.shoutbox.ask'),
    url(r'^profile/ajax/shout/$', 'account.shoutbox.shout'),
    url(r'^profile/edit/$', 'account.edit_profile.view'),
    url(r'^profile/messages/remove/(?P<page>\d+?)/$', 'account.messages.inbox', {'delete': True}),
    url(r'^profile/messages/remove/$', 'account.messages.inbox', {'delete': True}),
    url(r'^profile/bars/(?P<page>\d+?)/$', 'bar.manage_bar.list_of_bars'),
    url(r'^profile/bars/$', 'bar.manage_bar.list_of_bars'),
    url(r'^profile/messages/$', 'account.messages.inbox'),
    url(r'^profile/message/m(?P<id>\d+?)/$', 'account.messages.view_message'),
    url(r'^profile/message/f(?P<id>\d+?)/$', 'account.messages.view_familiar'),
    url(r'^profile/messages/(?P<page>\d+?)/$', 'account.messages.inbox'),    
    url(r'^profile/message/send/$', 'account.messages.send'),
    url(r'^profile/(?P<uid>\d+?)/frequenter_at/(?P<page>\d+?)/$', 'account.frequenter_at.barlist'),    
    url(r'^profile/(?P<uid>\d+?)/frequenter_at/$', 'account.frequenter_at.barlist'),    
    url(r'^profile/(?P<uid>\d+?)/familiars/(?P<page>\d+?)/$', 'account.lists.familiars'),    
    url(r'^profile/(?P<uid>\d+?)/familiars/$', 'account.lists.familiars'),    
    url(r'^profile/(?P<uid>\d+?)/bars/(?P<page>\d+?)/$', 'account.lists.bars'),    
    url(r'^profile/(?P<uid>\d+?)/bars/$', 'account.lists.bars'),    
    url(r'^profile/(?P<uid>\d+?)/$', 'account.views.profile'),
    url(r'^profile/(?P<uid>\d+?)/gallery/$', 'account.gallery.view_user_gallery'),
    url(r'^profile/(?P<uid>\d+?)/gallery/friendstatus/$', 'account.gallery.change_friend_status'),
    url(r'^profile/gallery/comments/(?P<uphid>\d+?)/$', 'account.gallery.ajax_get_comments'),
    url(r'^profile/gallery/comment/(?P<uphid>\d+?)/$', 'account.gallery.ajax_push_comment'),
    url(r'^profile/gallery/manage/$', 'account.gallery.manage'),
    url(r'^login/remind/$', 'account.views.passremind'),
    url(r'^login/recover/$', 'account.views.passrecover'),
    url(r'^login/register/$', 'account.register.view'),
    url(r'^login/register/activate/$', 'account.register.activate'),
    url(r'^bar/add/$', 'bar.add_bar.view'),

    url(r'^search/users/$', 'search.users.view'),
    url(r'^search/users/(?P<page>\d+?)/$', 'search.users.view'),
    url(r'^search/bars/$', 'search.bars.view'),
    url(r'^search/bars/(?P<page>\d+?)/$', 'search.bars.view'),

    url(r'^ranking/bars/$', 'ranking.bars.ranking_bars'),
    url(r'^ranking/bars/(?P<page>\d+?)/$', 'ranking.bars.ranking_bars'),
    url(r'^ranking/users/$', 'ranking.users.ranking_users'),
    url(r'^ranking/users/(?P<page>\d+?)/$', 'ranking.users.ranking_users'),

    url(r'^bar/(?P<id>\d+?)/ajax/$', 'bar.ajax.op'),
    url(r'^bar/(?P<slugname>.+?)/add_photo/$', 'bar.bar.add_photo'),
    url(r'^bar/(?P<slugname>.+?)/frequenters/(?P<page>\d+?)/$', 'bar.bar.frequenters'),
    url(r'^bar/(?P<slugname>.+?)/frequenters/$', 'bar.bar.frequenters'),
    url(r'^bar/(?P<slugname>.+?)/manage/$', 'bar.manage_bar.view'),
    url(r'^bar/(?P<slugname>.+?)/add_event/$', 'barevent.add_event.view'),
    url(r'^bar/(?P<slugname>.+?)/manage/op/$', 'bar.manage_bar.op'),
    url(r'^bar/(?P<slugname>.+?)/(?P<evtname>.+?)/op/$', 'barevent.view.op'),
    url(r'^bar/(?P<slugname>.+?)/(?P<evtname>.+?)/$', 'barevent.view.view_event'),
    url(r'^bar/(?P<slugname>.+?)/$', 'bar.bar.view'),
    # Actions for cron
    url(r'^admin/cron/regenerate_bar_ranking/', 'cron.actions.regenerate_bar_ranking'),
    url(r'^admin/cron/regenerate_user_ranking/', 'cron.actions.regenerate_user_ranking'),

    url(r'^admin/ad/click/(?P<id>\d+?)/$', 'adverts.click.click'),
    url(r'^admin/adpanel/delete/(?P<id>\d+?)/$', 'admin.adpanel.delete'),
    url(r'^admin/adpanel/$', 'admin.adpanel.view_banners'),

    url(r'^(?P<slugname>.+)', 'bar.bar.refer'),
)

handler404 = 'trybar.main.static.http404'
handler500 = 'trybar.main.static.http500'

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