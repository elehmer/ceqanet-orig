from django.conf.urls import patterns, url
from ceqanet.views import index,query,projectlist,projdoclist,NOEdescription,NODdescription,docdescription,submit,findproject,addproject,inputform,docadd_noc,docadd_nod,docadd_noe,docadd_nop,adddocument

urlpatterns = patterns('ceqanet.views',
	url(r'^$','index',name='index'),
	#url(r'^caindex/$','caindex',name='caindex'),
	url(r'^query/$',query.as_view(),name='query'),
	url(r'^projectlist/$',projectlist.as_view(),name='projectlist'),
	url(r'^projdoclist/$',projdoclist.as_view(),name='projdoclist'),
	url(r'^NOEdescription/$',NOEdescription.as_view(),name='NOEdescription'),
	url(r'^NODdescription/$',NODdescription.as_view(),name='NODdescription'),
	url(r'^docdescription/$',docdescription.as_view(),name='docdescription'),
	url(r'^submit/$',submit.as_view(),name='submit'),
	url(r'^findproject/$',findproject.as_view(),name='findproject'),
	url(r'^addproject/$',addproject.as_view(),name='addproject'),
	url(r'^inputform/$',inputform.as_view(),name='inputform'),
	url(r'^docadd_noc/$',docadd_noc.as_view(),name='docadd_noc'),
	url(r'^docadd_nod/$',docadd_nod.as_view(),name='docadd_nod'),
	url(r'^docadd_noe/$',docadd_noe.as_view(),name='docadd_noe'),
	url(r'^docadd_nop/$',docadd_nop.as_view(),name='docadd_nop'),
	url(r'^adddocument/$',adddocument.as_view(),name='adddocument'),
)