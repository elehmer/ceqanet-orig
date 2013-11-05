from django.conf.urls import patterns, url
from django.conf.urls.static import static
from django.conf import settings
from ceqanet.views import index,query,basicquery,prjlist,projectlist,projdoclist,submit,findproject,accept,usersettings
from ceqanet.views import docdesp_noc,docdesp_noe,docdesp_nod,docdesp_nop
from ceqanet.views import docadd_noc,docadd_nod,docadd_noe,docadd_nop
from ceqanet.views import docedit_noc,docedit_noe,docedit_nod,docedit_nop
from ceqanet.views import pending,pendingdetail_noc,pendingdetail_nod,pendingdetail_noe,pendingdetail_nop
from ceqanet.views import review,reviewdetail_noc,reviewdetail_nod,reviewdetail_noe,reviewdetail_nop
from ceqanet.views import comment,commentdetail_noc,commentdetail_nod,commentdetail_noe,commentdetail_nop


urlpatterns = patterns('ceqanet.views',
    url(r'^$','index',name='index'),
    url(r'^query/$',query.as_view(),name='query'),
    url(r'^basicquery/$',basicquery.as_view(),name='basicquery'),
    url(r'^prjlist/$',prjlist.as_view(),name='prjlist'),
    url(r'^projectlist/$',projectlist.as_view(),name='projectlist'),
    url(r'^projdoclist/$',projdoclist.as_view(),name='projdoclist'),
    url(r'^submit/$',submit.as_view(),name='submit'),
    url(r'^accept/$','accept',name='accept'),
    url(r'^findproject/$',findproject.as_view(),name='findproject'),
    url(r'^docdesp_noc/(?P<pk>\d+)/$',docdesp_noc.as_view(),name='docdesp_noc'),
    url(r'^docdesp_nod/(?P<pk>\d+)/$',docdesp_nod.as_view(),name='docdesp_nod'),
    url(r'^docdesp_noe/(?P<pk>\d+)/$',docdesp_noe.as_view(),name='docdesp_noe'),
    url(r'^docdesp_nop/(?P<pk>\d+)/$',docdesp_nop.as_view(),name='docdesp_nop'),
    url(r'^docedit_noc/$',docedit_noc.as_view(),name='docedit_noc'),
    url(r'^docedit_nod/$',docedit_nod.as_view(),name='docedit_nod'),
    url(r'^docedit_noe/$',docedit_noe.as_view(),name='docedit_noe'),
    url(r'^docedit_nop/$',docedit_nop.as_view(),name='docedit_nop'),
    url(r'^docadd_noc/$',docadd_noc.as_view(),name='docadd_noc'),
    url(r'^docadd_nod/$',docadd_nod.as_view(),name='docadd_nod'),
    url(r'^docadd_noe/$',docadd_noe.as_view(),name='docadd_noe'),
    url(r'^docadd_nop/$',docadd_nop.as_view(),name='docadd_nop'),
    url(r'^pending/$',pending.as_view(),name='pending'),
    url(r'^pendingdetail_noc/$',pendingdetail_noc.as_view(),name='pendingdetail_noc'),
    url(r'^pendingdetail_nod/$',pendingdetail_nod.as_view(),name='pendingdetail_nod'),
    url(r'^pendingdetail_noe/$',pendingdetail_noe.as_view(),name='pendingdetail_noe'),
    url(r'^pendingdetail_nop/$',pendingdetail_nop.as_view(),name='pendingdetail_nop'),
    url(r'^review/$',review.as_view(),name='review'),
    url(r'^reviewdetail_noc/$',reviewdetail_noc.as_view(),name='reviewdetail_noc'),
    url(r'^reviewdetail_nod/$',reviewdetail_nod.as_view(),name='reviewdetail_nod'),
    url(r'^reviewdetail_noe/$',reviewdetail_noe.as_view(),name='reviewdetail_noe'),
    url(r'^reviewdetail_nop/$',reviewdetail_nop.as_view(),name='reviewdetail_nop'),
    url(r'^comment/$',comment.as_view(),name='comment'),
    url(r'^commentdetail_noc/$',commentdetail_noc.as_view(),name='commentdetail_noc'),
    url(r'^commentdetail_nod/$',commentdetail_nod.as_view(),name='commentdetail_nod'),
    url(r'^commentdetail_noe/$',commentdetail_noe.as_view(),name='commentdetail_noe'),
    url(r'^commentdetail_nop/$',commentdetail_nop.as_view(),name='commentdetail_nop'),
    url(r'^usersettings/$',usersettings.as_view(),name='usersettings'),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += patterns('',
    url(r'^login/$','django.contrib.auth.views.login',{'template_name':'ceqanet/login.html'},name = 'login'),
    url(r'^logout/$','django.contrib.auth.views.logout', {'next_page': '/'}, name = 'logout'),
)
