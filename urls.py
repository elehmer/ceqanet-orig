from django.conf.urls import patterns, url
from ceqanet.views import index,query,projectlist,projdoclist,docdescription,submit,findproject,docadd_noc,docadd_nod,docadd_noe,docadd_nop,adddocument,docedit_noc,docedit_noe,docedit_nod,docedit_nop,pending,pendingdetail,accept,review,reviewdetail,usersettings,comment,commentdetail,docdesp_noc,docdesp_noe,docdesp_nod,docdesp_nop
#map related views
from ceqanet.views import locations_geojson, map

urlpatterns = patterns('ceqanet.views',
    url(r'^$','index',name='index'),
    #url(r'^caindex/$','caindex',name='caindex'),
    url(r'^query/$',query.as_view(),name='query'),
    url(r'^projectlist/$',projectlist.as_view(),name='projectlist'),
    url(r'^projdoclist/$',projdoclist.as_view(),name='projdoclist'),
    url(r'^docdescription/(?P<pk>\d+)/$',docdescription.as_view(),name='docdescription'),
    url(r'^submit/$',submit.as_view(),name='submit'),
    url(r'^findproject/$',findproject.as_view(),name='findproject'),
    url(r'^docdesp_noc/(?P<pk>\d+)/$',docdesp_noc.as_view(),name='docdesp_noc'),
    url(r'^docedit_noc/$',docedit_noc.as_view(),name='docedit_noc'),
    url(r'^docdesp_noe/(?P<pk>\d+)/$',docdesp_noe.as_view(),name='docdesp_noe'),
    url(r'^docedit_noe/$',docedit_noe.as_view(),name='docedit_noe'),
    url(r'^docdesp_nod/(?P<pk>\d+)/$',docdesp_nod.as_view(),name='docdesp_nod'),
    url(r'^docedit_nod/$',docedit_nod.as_view(),name='docedit_nod'),
    url(r'^docdesp_nop/(?P<pk>\d+)/$',docdesp_nop.as_view(),name='docdesp_nop'),
    url(r'^docedit_nop/$',docedit_nop.as_view(),name='docedit_nop'),
    url(r'^docadd_noc/$',docadd_noc.as_view(),name='docadd_noc'),
    url(r'^docadd_nod/$',docadd_nod.as_view(),name='docadd_nod'),
    url(r'^docadd_noe/$',docadd_noe.as_view(),name='docadd_noe'),
    url(r'^docadd_nop/$',docadd_nop.as_view(),name='docadd_nop'),
    url(r'^adddocument/$',adddocument.as_view(),name='adddocument'),
    url(r'^accept/$','accept',name='accept'),
    url(r'^pending/$',pending.as_view(),name='pending'),
    url(r'^pendingdetail/$',pendingdetail.as_view(),name='pendingdetail'),
    url(r'^review/$',review.as_view(),name='review'),
    url(r'^reviewdetail/$',reviewdetail.as_view(),name='reviewdetail'),
    url(r'^comment/$',comment.as_view(),name='comment'),
    url(r'^commentdetail/$',commentdetail.as_view(),name='commentdetail'),
    url(r'^usersettings/$',usersettings.as_view(),name='usersettings'),
    url(r'^map/all/geojson/$','locations_geojson',name="locations"),
    url(r'^map/all/geojson/(?P<limit>\d+)/$','locations_geojson',name="locations"),
    url(r'^map/$','map',name="map"),


)

urlpatterns += patterns('',
    url(r'^login/$','django.contrib.auth.views.login',{'template_name':'ceqanet/login.html'},name = 'login'),
    url(r'^logout/$','django.contrib.auth.views.logout', {'next_page': '/'}, name = 'logout'),
)
