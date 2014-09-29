from django.conf.urls import include,patterns, url
from django.conf.urls.static import static
from django.conf import settings
from ceqanet.views import index,basicsearch,advancedsearch,prjlist,doclist,projectlist,projdoclist,submit,draftsbylag,pendingsbylag,chquery,findproject,accept,usersettings,attachments,manageaccount,requestupgrd,manageupgrades,manageupgrade,manageusers,manageuser,reviewsbylag
from ceqanet.views import docdesp_noc,docdesp_noe,docdesp_nod,docdesp_nop
from ceqanet.views import docadd_noc,docadd_nod,docadd_noe,docadd_nop
from ceqanet.views import docedit_noc,docedit_noe,docedit_nod,docedit_nop
from ceqanet.views import draftedit_noc,draftedit_nod,draftedit_noe,draftedit_nop
from ceqanet.views import pending,pendingdetail_noc,pendingdetail_nod,pendingdetail_noe,pendingdetail_nop,latest,addleadagency,addreviewingagency,addholiday
from ceqanet.views import review,reviewdetail_noc,reviewdetail_nop
from ceqanet.views import comment,commentdetail,commentadd,showcomment,commentaccept
#map related views
from ceqanet.views import locations_geojson, map, locationEdit
#document api
from ceqanet.views import doc_json,doc_location
#from registration.backends.default.views import register
#from ceqanet.forms import UserRegistrationForm
#import regbackend

urlpatterns = patterns('ceqanet.views',
    url(r'^$','index',name='index'),
    url(r'^search/$',basicsearch.as_view(),name='basicsearch'),
    url(r'^search/advanced/$',advancedsearch.as_view(),name='advancedsearch'),
    url(r'^project/list/$',prjlist.as_view(),name='prjlist'),
    url(r'^document/list/$',doclist.as_view(),name='doclist'),
    url(r'^projectlist/$',projectlist.as_view(),name='projectlist'),
    url(r'^projdoclist/$',projdoclist.as_view(),name='projdoclist'),
    url(r'^submit/$',submit.as_view(),name='submit'),
    url(r'^draftsbylag/$',draftsbylag.as_view(),name='draftsbylag'),
    url(r'^pendingsbylag/$',pendingsbylag.as_view(),name='pendingsbylag'),
    url(r'^reviewsbylag/$',reviewsbylag.as_view(),name='reviewsbylag'),
    url(r'^accept/$','accept',name='accept'),
    url(r'^chquery/$',chquery.as_view(),name='chquery'),
    url(r'^project/find$',findproject.as_view(),name='findproject'),
    url(r'^attachments/$',attachments.as_view(),name='attachments'),
    url(r'^draft/noc/edit/$',draftedit_noc.as_view(),name='draftedit_noc'),
    url(r'^draft/nod/edit/$',draftedit_nod.as_view(),name='draftedit_nod'),
    url(r'^draft/noe/edit/$',draftedit_noe.as_view(),name='draftedit_noe'),
    url(r'^draft/nop/edit/$',draftedit_nop.as_view(),name='draftedit_nop'),
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
    url(r'^document/showcomment/(?P<pk>\d+)/$',showcomment.as_view(),name='showcomment'),    
    url(r'^pending/$',pending.as_view(),name='pending'),
    url(r'^latest/$',latest.as_view(),name='latest'),
    url(r'^addleadagency/$',addleadagency.as_view(),name='addleadagency'),
    url(r'^addreviewingagency/$',addreviewingagency.as_view(),name='addreviewingagency'),
    url(r'^addholiday/$',addholiday.as_view(),name='addholiday'),
    url(r'^review/$',review.as_view(),name='review'),
    url(r'^pending/noc/detail/$',pendingdetail_noc.as_view(),name='pendingdetail_noc'),
    url(r'^pending/nod/detail/$',pendingdetail_nod.as_view(),name='pendingdetail_nod'),
    url(r'^pending/noe/detail/$',pendingdetail_noe.as_view(),name='pendingdetail_noe'),
    url(r'^pending/nop/detail/$',pendingdetail_nop.as_view(),name='pendingdetail_nop'),
    url(r'^review/$',review.as_view(),name='review'),
    url(r'^review/noc/detail/$',reviewdetail_noc.as_view(),name='reviewdetail_noc'),
    url(r'^review/nop/detail/$',reviewdetail_nop.as_view(),name='reviewdetail_nop'),
    url(r'^comment/$',comment.as_view(),name='comment'),
    url(r'^comment/detail/$',commentdetail.as_view(),name='commentdetail'),
    url(r'^comment/add/$',commentadd.as_view(),name='commentadd'),
    url(r'^comment/accept/$','commentaccept',name='commentaccept'),
    url(r'^user/account/$',manageaccount.as_view(),name='manageaccount'),
    url(r'^user/requestupgrade/$',requestupgrd.as_view(),name='requestupgrd'),
    url(r'^user/manageupgrades/$',manageupgrades.as_view(),name='manageupgrades'),
    url(r'^user/manageupgrade/$',manageupgrade.as_view(),name='manageupgrade'),
    url(r'^user/manageusers/$',manageusers.as_view(),name='manageusers'),
    url(r'^user/manageuser/$',manageuser.as_view(),name='manageuser'),
    url(r'^user/settings/$',usersettings.as_view(),name='usersettings'),
    url(r'^county/(?P<county>[-\w]+)/citiesforcounty_json/$', 'citiesforcounty_json'),
    url(r'^map/all/geojson/$','locations_geojson',name="locationsall"),
    url(r'^map/all/geojson/(?P<limit>\d+)/$','locations_geojson',name="locationslimited"),
    url(r'^api/doc/short/(?P<doc_id>\d+)/$','doc_json',name="doc_json"),
    url(r'^api/doc/location/(?P<doc_id>\d+)/$','doc_location',name="doc_location"), 
    url(r'^map/$','map',name="map"),
    url(r'^document/location/edit/(?P<slug>\d+)/$',locationEdit.as_view(),name='map_edit'),
) 
#+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


urlpatterns += patterns('',
    #url(r'^accounts/register/$', register, {'backend': 'registration.backends.default.DefaultBackend','form_class': UserRegistrationForm}, name='registration_register'),    
    url(r'^accounts/login/$','django.contrib.auth.views.login',{'template_name':'ceqanet/login.html'},name = 'login'),
    #url(r'^accounts/login/$','django.contrib.auth.views.login',name = 'login'),
    url(r'^accounts/logout/$','django.contrib.auth.views.logout', {'next_page': '/'}, name = 'logout'),
)

#urlpatterns = patterns('',
#    ...
#    (r'^accounts/', include('allauth.urls')),
#    ...
#)
