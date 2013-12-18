from django.conf.urls import patterns, url
from django.conf.urls.static import static
from django.conf import settings
from ceqanet.views import index,query,basicquery,advancedquery,prjlist,doclist,projectlist,projdoclist,submit,chquery,findproject,accept,usersettings,attachments,account
from ceqanet.views import docdesp_noc,docdesp_noe,docdesp_nod,docdesp_nop
from ceqanet.views import docadd_noc,docadd_nod,docadd_noe,docadd_nop
from ceqanet.views import docedit_noc,docedit_noe,docedit_nod,docedit_nop
from ceqanet.views import pending,pendingdetail_noc,pendingdetail_nod,pendingdetail_noe,pendingdetail_nop
from ceqanet.views import review,reviewdetail_noc,reviewdetail_nod,reviewdetail_noe,reviewdetail_nop
from ceqanet.views import comment,commentdetail_noc,commentdetail_nod,commentdetail_noe,commentdetail_nop
#map related views
from ceqanet.views import locations_geojson, map, locationEdit
#document api
from ceqanet.views import doc_json,doc_location

urlpatterns = patterns('ceqanet.views',
    url(r'^$','index',name='index'),
    url(r'^search/original/$',query.as_view(),name='query'),
    url(r'^search/$',basicquery.as_view(),name='basicquery'),
    url(r'^search/advanced/$',advancedquery.as_view(),name='advancedquery'),
    url(r'^project/list/$',prjlist.as_view(),name='prjlist'),
    url(r'^document/list/$',doclist.as_view(),name='doclist'),
    url(r'^projectlist/$',projectlist.as_view(),name='projectlist'),
    url(r'^projdoclist/$',projdoclist.as_view(),name='projdoclist'),
    url(r'^submit/$',submit.as_view(),name='submit'),
    url(r'^accept/$','accept',name='accept'),
    url(r'^chquery/$',chquery.as_view(),name='chquery'),
    url(r'^project/find$',findproject.as_view(),name='findproject'),
    url(r'^document/attachments/$',attachments.as_view(),name='attachments'),
    url(r'^document/noc/description/(?P<pk>\d+)/$',docdesp_noc.as_view(),name='docdesp_noc'),
    url(r'^document/nod/description/(?P<pk>\d+)/$',docdesp_nod.as_view(),name='docdesp_nod'),
    url(r'^document/noe/description/(?P<pk>\d+)/$',docdesp_noe.as_view(),name='docdesp_noe'),
    url(r'^document/nop/description/(?P<pk>\d+)/$',docdesp_nop.as_view(),name='docdesp_nop'),
    url(r'^document/noc/edit/$',docedit_noc.as_view(),name='docedit_noc'),
    url(r'^document/nod/edit/$',docedit_nod.as_view(),name='docedit_nod'),
    url(r'^document/noe/edit/$',docedit_noe.as_view(),name='docedit_noe'),
    url(r'^document/nop/edit/$',docedit_nop.as_view(),name='docedit_nop'),
    url(r'^document/noc/add/$',docadd_noc.as_view(),name='docadd_noc'),
    url(r'^document/nod/add/$',docadd_nod.as_view(),name='docadd_nod'),
    url(r'^document/noe/add/$',docadd_noe.as_view(),name='docadd_noe'),
    url(r'^document/nop/add/$',docadd_nop.as_view(),name='docadd_nop'),
    url(r'^pending/$',pending.as_view(),name='pending'),
    url(r'^review/$',review.as_view(),name='review'),
    #url(r'^comment/$',comment.as_view(),name='comment'),
    #url(r'^commentdetail/$',commentdetail.as_view(),name='commentdetail'),
    #url(r'^usersettings/$',usersettings.as_view(),name='usersettings'),
    url(r'^pending/noc/detail/$',pendingdetail_noc.as_view(),name='pendingdetail_noc'),
    url(r'^pending/nod/detail/$',pendingdetail_nod.as_view(),name='pendingdetail_nod'),
    url(r'^pending/noe/detail/$',pendingdetail_noe.as_view(),name='pendingdetail_noe'),
    url(r'^pending/nop/detail/$',pendingdetail_nop.as_view(),name='pendingdetail_nop'),
    url(r'^review/$',review.as_view(),name='review'),
    url(r'^review/noc/detail/$',reviewdetail_noc.as_view(),name='reviewdetail_noc'),
    url(r'^review/nod/detail/$',reviewdetail_nod.as_view(),name='reviewdetail_nod'),
    url(r'^review/noe/detail/$',reviewdetail_noe.as_view(),name='reviewdetail_noe'),
    url(r'^review/nop/detail/$',reviewdetail_nop.as_view(),name='reviewdetail_nop'),
    url(r'^comment/$',comment.as_view(),name='comment'),
    url(r'^comment/noc/detail/$',commentdetail_noc.as_view(),name='commentdetail_noc'),
    url(r'^comment/nod/detail/$',commentdetail_nod.as_view(),name='commentdetail_nod'),
    url(r'^comment/noe/detail/$',commentdetail_noe.as_view(),name='commentdetail_noe'),
    url(r'^comment/nop/detail/$',commentdetail_nop.as_view(),name='commentdetail_nop'),
    url(r'^user/account/$','account',name='account'),
    url(r'^user/settings/$',usersettings.as_view(),name='usersettings'),
    url(r'^map/all/geojson/$','locations_geojson',name="locationsall"),
    url(r'^map/all/geojson/(?P<limit>\d+)/$','locations_geojson',name="locationslimited"),
    url(r'^api/doc/short/(?P<doc_id>\d+)/$','doc_json',name="doc_json"),
    url(r'^api/doc/location/(?P<doc_id>\d+)/$','doc_location',name="doc_location"), 
    url(r'^map/$','map',name="map"),
    url(r'^document/location/edit/(?P<slug>\d+)/$',locationEdit.as_view(),name='map_edit'),
) 
#+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


urlpatterns += patterns('',
    url(r'^login/$','django.contrib.auth.views.login',{'template_name':'ceqanet/login.html'},name = 'login'),
    url(r'^logout/$','django.contrib.auth.views.logout', {'next_page': '/'}, name = 'logout'),
)
