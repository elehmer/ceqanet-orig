from django.conf.urls import patterns, url
from ceqanet.views import index,query,projectlist,projdoclist,docdescription,submit,findproject,addproject,inputform,docadd_noc,docadd_nod,docadd_noe,docadd_nop,adddocument,NOEedit,pending,pendingdetail,accept,review,reviewdetail,usersettings,comment,commentdetail

urlpatterns = patterns('ceqanet.views',
	url(r'^$','index',name='index'),
	#url(r'^caindex/$','caindex',name='caindex'),
	url(r'^query/$',query.as_view(),name='query'),
	url(r'^projectlist/$',projectlist.as_view(),name='projectlist'),
	url(r'^projdoclist/$',projdoclist.as_view(),name='projdoclist'),
	url(r'^docdescription/(?P<pk>\d+)/$',docdescription.as_view(),name='docdescription'),
	url(r'^docdescription/(?P<pk>\d+)/edit$',NOEedit.as_view(),name='NOEedit'),
	url(r'^submit/$',submit.as_view(),name='submit'),
	url(r'^findproject/$',findproject.as_view(),name='findproject'),
	url(r'^addproject/$',addproject.as_view(),name='addproject'),
	url(r'^inputform/$',inputform.as_view(),name='inputform'),
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
)

urlpatterns += patterns('',
    url(r'^login/$','django.contrib.auth.views.login',{'template_name':'ceqanet/login.html'},name = 'login'),
    url(r'^logout/$','django.contrib.auth.views.logout', {'next_page': '/'}, name = 'logout'),
)
