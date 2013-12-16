from django import forms
from django.forms import ModelForm
from olwidget.forms import  MapModelForm
from olwidget.fields import EditableLayerField
from olwidget.widgets import EditableMap
from datetime import datetime, date, timedelta
from ceqanet.models import projects,documents,geowords,reviewingagencies,leadagencies,keywords,doctypes,docattachments,Locations
from localflavor.us.forms import USPhoneNumberField,USStateField,USZipCodeField
from enumerations import DOCUMENT_TYPES,PROJECT_EXISTS,EXEMPT_STATUS_CHOICES,PLANNERREGION_CHOICES,COLATION_CHOICES,PRJ_SORT_FIELDS,DOC_SORT_FIELDS,RDODATE_CHOICES,RDOPLACE_CHOICES,RDOLAG_CHOICES,RDORAG_CHOICES,RDODOCTYPE_CHOICES,DETERMINATION_CHOICES,NODAGENCY_CHOICES,RDOLAT_CHOICES,RDODEVTYPE_CHOICES,RDOISSUE_CHOICES
from django.contrib.admin.widgets import FilteredSelectMultiple


class MapForm(forms.Form):
    '''Reusable Map enhancement to forms'''
    geom = forms.CharField(widget=EditableMap(options={'layers': ['osm.mapnik'],
                                                    'isCollection':True, 
                                                    'geometry':['point','linestring','polygon'],
                                                    'default_lat': 37.424431833728114,
                                                    'default_lon': -121.90515908415186,'default_zoom':6},template=None))
    
class basicqueryform(forms.Form):
    prj_schno = forms.CharField(label="Clearinghouse Number:",required=True,max_length=12)
    colation = forms.ChoiceField(label="Search Database By:",required=True,choices=COLATION_CHOICES,initial='document',widget=forms.RadioSelect())

class advancedqueryform(forms.Form):
    rdodate = forms.ChoiceField(label="Date Range:",required=True,choices=RDODATE_CHOICES,initial='range',widget=forms.RadioSelect(attrs={'id':'rdodate'}))
    date_from = forms.DateField(label="From:",required=False, initial=lambda: (date.today() - timedelta(days=180)).strftime("%Y-%m-%d"),input_formats=['%Y-%m-%d'])
    date_to = forms.DateField(label="To:",required=False, initial=date.today().strftime("%Y-%m-%d"),input_formats=['%Y-%m-%d'])
    rdoplace = forms.ChoiceField(label="Project Location:",required=True,choices=RDOPLACE_CHOICES,initial='all',widget=forms.RadioSelect(attrs={'id':'rdoplace'}))
    cityid = forms.ModelChoiceField(label="City:",required=False,queryset=geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).order_by('geow_shortname'),empty_label=None)
    countyid = forms.ModelChoiceField(label="County:",required=False,queryset=geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).order_by('geow_shortname'),empty_label=None)
    rdolag = forms.ChoiceField(label="Lead Agency:",required=True,choices=RDOLAG_CHOICES,initial='all',widget=forms.RadioSelect(attrs={'id':'rdolag'}))
    lagid = forms.ModelChoiceField(label="Lead Agency:",required=False,queryset=leadagencies.objects.filter(inlookup=True).order_by('lag_name'),empty_label=None)
    rdorag = forms.ChoiceField(label="Reviewing Agency:",required=True,choices=RDORAG_CHOICES,initial='all',widget=forms.RadioSelect(attrs={'id':'rdorag'}))
    ragid = forms.ModelChoiceField(label="Reviewing Agency:",required=False,queryset=reviewingagencies.objects.filter(inlookup=True).order_by('rag_name'),empty_label=None)
    rdodoctype = forms.ChoiceField(label="Document Type:",required=True,choices=RDODOCTYPE_CHOICES,initial='all',widget=forms.RadioSelect(attrs={'id':'rdodoctype'}))
    doctypeid = forms.ModelChoiceField(label="Document Type:",required=False,queryset=doctypes.objects.filter(inlookup=True).order_by('keyw_longname'),empty_label=None)
    rdolat = forms.ChoiceField(label="Local Action Type:",required=True,choices=RDOLAT_CHOICES,initial='all',widget=forms.RadioSelect(attrs={'id':'rdolat'}))
    latid = forms.ModelChoiceField(label="Local Action Type:",required=False,queryset=keywords.objects.filter(keyw_keyl_fk__keyl_pk=1001).order_by('keyw_longname'),empty_label=None)
    rdodevtype = forms.ChoiceField(label="Development Type:",required=True,choices=RDODEVTYPE_CHOICES,initial='all',widget=forms.RadioSelect(attrs={'id':'rdodevtype'}))
    devtypeid = forms.ModelChoiceField(label="Development Type:",required=False,queryset=keywords.objects.filter(keyw_keyl_fk__keyl_pk=1010).order_by('keyw_longname'),empty_label=None)
    rdoissue = forms.ChoiceField(label="Project Issue:",required=True,choices=RDOISSUE_CHOICES,initial='all',widget=forms.RadioSelect(attrs={'id':'rdoissue'}))
    issueid = forms.ModelChoiceField(label="Project Issue:",required=False,queryset=keywords.objects.filter(keyw_keyl_fk__keyl_pk=1002).order_by('keyw_longname'),empty_label=None)
    colation = forms.ChoiceField(label="Search Database By:",required=True,choices=COLATION_CHOICES,initial='document',widget=forms.RadioSelect(attrs={'id':'colation'}))

class prjlistform(forms.Form):
    sortfld = forms.ChoiceField(label="Sort Results By:",required=True,choices=PRJ_SORT_FIELDS,initial='-prj_schno')

class doclistform(forms.Form):
    sortfld = forms.ChoiceField(label="Sort Results By:",required=True,choices=DOC_SORT_FIELDS,initial='-doc_prj_fk__prj_schno')

class QueryForm(forms.Form):
    prj_schno = forms.CharField(label="Clearinghouse Number:",max_length=12)

    date_from = forms.DateField(label="From", initial=lambda: (date.today() - timedelta(days=14)).strftime("%Y-%m-%d"),input_formats=['%Y-%m-%d'])
    date_to = forms.DateField(label="To", initial=date.today().strftime("%Y-%m-%d"),input_formats=['%Y-%m-%d'])

class submitform(forms.Form):
    doctype = forms.ChoiceField(required=True,choices=DOCUMENT_TYPES,initial='NOE')
    prjtoggle = forms.ChoiceField(required=True,choices=PROJECT_EXISTS,initial='no',widget=forms.RadioSelect())

class nocform(forms.Form):
    prj_title = forms.CharField(label="Project Title:",required=True,max_length=160,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
    prj_description = forms.CharField(label="Project Description:",required=True,widget=forms.Textarea(attrs={'cols':'75','rows':'5'}))
    doc_conname = forms.CharField(label="Contact Person:",required=True,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    doc_conemail = forms.EmailField(label="E-mail:",required=True,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    doc_conphone = USPhoneNumberField(label="Phone:",required=True)
    doc_conaddress1 = forms.CharField(label="Street Address1:",required=True,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    doc_conaddress2 = forms.CharField(label="Street Address2:",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    doc_concity = forms.CharField(label="City:",required=True,max_length=32,widget=forms.TextInput(attrs={'size':'32'}))
    doc_constate = USStateField(label="State:",required=True)
    doc_conzip = USZipCodeField(label="Zip:",required=True)
    doc_location = forms.CharField(label="Document Location:",widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
    doc_latitude = forms.CharField(label="Document Latitude:",max_length=30,widget=forms.TextInput(attrs={'size':'30'}))
    doc_longitude = forms.CharField(label="Document Longitude:",max_length=30,widget=forms.TextInput(attrs={'size':'30'}))
    doc_city = forms.ModelChoiceField(label="City:",queryset=geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).order_by('geow_shortname'),empty_label="[Select City]")
    doc_county = forms.ModelChoiceField(label="County:",queryset=geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).order_by('geow_shortname'),empty_label="[Select County]")
    doc_parcelno = forms.CharField(label='Parcel No.:',required=False,max_length=96,widget=forms.TextInput(attrs={'size':'96'}))
    doc_xstreets = forms.CharField(label='Cross Streets:',required=False,max_length=96,widget=forms.TextInput(attrs={'size':'96'}))
    doc_township = forms.CharField(label='Township:',required=False,max_length=6,widget=forms.TextInput(attrs={'size':'6'}))
    doc_range = forms.CharField(label='Range:',required=False,max_length=6,widget=forms.TextInput(attrs={'size':'6'}))
    doc_section = forms.CharField(label='Section:',required=False,max_length=6,widget=forms.TextInput(attrs={'size':'6'}))
    doc_base = forms.CharField(label='Base:',required=False,max_length=8,widget=forms.TextInput(attrs={'size':'8'}))
    doc_highways = forms.CharField(label="State Hwy #:",required=False,max_length=32,widget=forms.TextInput(attrs={'size':'32'}))
    doc_airports = forms.CharField(label="Airports:",required=False,max_length=32,widget=forms.TextInput(attrs={'size':'32'}))
    doc_railways = forms.CharField(label="Railways:",required=False,max_length=32,widget=forms.TextInput(attrs={'size':'32'}))
    doc_waterways = forms.CharField(label="Waterways:",required=False,max_length=96,widget=forms.TextInput(attrs={'size':'96'}))
    doc_landuse = forms.CharField(required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
    doc_schools = forms.CharField(label="Schools:",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    doctypeid = forms.ModelChoiceField(required=True,queryset=doctypes.objects.filter(inlookup=True).filter(storfed__gt=0).order_by('ordinal'),empty_label=None,widget=forms.RadioSelect())
    actions = forms.ModelMultipleChoiceField(required=False,queryset=keywords.objects.filter(keyw_keyl_fk__keyl_pk=1001).order_by('keyw_longname'),widget=forms.CheckboxSelectMultiple())
    dkey_comment_actions = forms.CharField(required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    dev6001_val1 = forms.CharField(label="Units",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6001_val2 = forms.CharField(label="Acres",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6002_val1 = forms.CharField(label="SqFt",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6002_val2 = forms.CharField(label="Acres",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6002_val3 = forms.CharField(label="Employees",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6003_val1 = forms.CharField(label="SqFt",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6003_val2 = forms.CharField(label="Acres",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6003_val3 = forms.CharField(label="Employees",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6004_val1 = forms.CharField(label="SqFt",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6004_val2 = forms.CharField(label="Acres",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6004_val3 = forms.CharField(label="Employees",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev7001_val1 = forms.CharField(label="Type",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev8001_val1 = forms.CharField(label="Type",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev10001_val1 = forms.CharField(label="Mineral",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    devtrans_id = forms.ModelChoiceField(required=False,queryset=keywords.objects.filter(keyw_pk__gt=4000).filter(keyw_pk__lt=5000),empty_label=None)
    devtrans_comment = forms.CharField(label="Comment",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'32'}))
    devpower_id = forms.ModelChoiceField(required=False,queryset=keywords.objects.filter(keyw_pk__gt=3000).filter(keyw_pk__lt=4000),empty_label=None)
    devpower_comment = forms.CharField(label="Comment",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'32'}))
    devpower_val1 = forms.CharField(label="Watts",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    devwaste_id = forms.ModelChoiceField(required=False,queryset=keywords.objects.filter(keyw_pk__gt=5000).filter(keyw_pk__lt=6000),empty_label=None)
    devwaste_comment = forms.CharField(label="Comment",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'32'}))
    dev9001_val1 = forms.CharField(label="Type",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev9001_val2 = forms.CharField(label="MGD",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dkey_comment_dev = forms.CharField(label="Other",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'8'}))
    issues = forms.ModelMultipleChoiceField(required=False,queryset=keywords.objects.filter(keyw_keyl_fk__keyl_pk=1002).order_by('keyw_longname'),widget=forms.CheckboxSelectMultiple())
    dkey_comment_issues = forms.CharField(required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    ragencies = forms.ModelMultipleChoiceField(label="Reviewing Agencies:",required=False,queryset=reviewingagencies.objects.filter(inlookup=True).order_by('rag_title'),widget=forms.SelectMultiple(attrs={'size':'10'}))
    #ragencies = forms.ModelMultipleChoiceField(label="Reviewing Agencies:",required=False,queryset=reviewingagencies.objects.filter(inlookup=True).order_by('rag_title'),widget=FilteredSelectMultiple("Subjects",True,attrs={'rows':'10'}))

class editnocform(forms.Form):
    prj_title = forms.CharField(label="Project Title:",required=False,max_length=160,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
    prj_description = forms.CharField(label="Project Description:",required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'5'}))
    doc_conagency = forms.CharField(label="Contact Agency:",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    doc_conname = forms.CharField(label="Contact Person:",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    doc_conemail = forms.EmailField(label="E-mail:",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    doc_conphone = USPhoneNumberField(label="Phone:",required=False)
    doc_conaddress1 = forms.CharField(label="Street Address1:",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    doc_conaddress2 = forms.CharField(label="Street Address2:",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    doc_concity = forms.CharField(label="City:",required=False,max_length=32,widget=forms.TextInput(attrs={'size':'32'}))
    doc_constate = USStateField(label="State:",required=False)
    doc_conzip = USZipCodeField(label="Zip:",required=False)
    doc_location = forms.CharField(label="Document Location:",required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
    doc_latitude = forms.CharField(label="Document Latitude:",required=False,max_length=30,widget=forms.TextInput(attrs={'size':'30'}))
    doc_longitude = forms.CharField(label="Document Longitude:",required=False,max_length=30,widget=forms.TextInput(attrs={'size':'30'}))
    doc_city = forms.ModelChoiceField(label="City:",required=False,queryset=geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).order_by('geow_shortname'),empty_label="[Select City]")
    doc_county = forms.ModelChoiceField(label="County:",required=False,queryset=geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).order_by('geow_shortname'),empty_label="[Select County]")
    doc_parcelno = forms.CharField(label='Parcel No.:',required=False,max_length=96,widget=forms.TextInput(attrs={'size':'96'}))
    doc_xstreets = forms.CharField(label='Cross Streets:',required=False,max_length=96,widget=forms.TextInput(attrs={'size':'96'}))
    doc_township = forms.CharField(label='Township:',required=False,max_length=6,widget=forms.TextInput(attrs={'size':'6'}))
    doc_range = forms.CharField(label='Range:',required=False,max_length=6,widget=forms.TextInput(attrs={'size':'6'}))
    doc_section = forms.CharField(label='Section:',required=False,max_length=6,widget=forms.TextInput(attrs={'size':'6'}))
    doc_base = forms.CharField(label='Base:',required=False,max_length=8,widget=forms.TextInput(attrs={'size':'8'}))
    doc_highways = forms.CharField(label="State Hwy #:",required=False,max_length=32,widget=forms.TextInput(attrs={'size':'32'}))
    doc_airports = forms.CharField(label="Airports:",required=False,max_length=32,widget=forms.TextInput(attrs={'size':'32'}))
    doc_railways = forms.CharField(label="Railways:",required=False,max_length=32,widget=forms.TextInput(attrs={'size':'32'}))
    doc_waterways = forms.CharField(label="Waterways:",required=False,max_length=96,widget=forms.TextInput(attrs={'size':'96'}))
    doc_landuse = forms.CharField(required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
    doc_schools = forms.CharField(label="Schools:",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    doctypeid = forms.ModelChoiceField(required=True,queryset=doctypes.objects.filter(inlookup=True).filter(storfed__gt=0).order_by('ordinal'),empty_label=None,widget=forms.RadioSelect())
    actions = forms.ModelMultipleChoiceField(required=False,queryset=keywords.objects.filter(keyw_keyl_fk__keyl_pk=1001).order_by('keyw_longname'),widget=forms.CheckboxSelectMultiple())
    dkey_comment_actions = forms.CharField(required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    dev6001_val1 = forms.CharField(label="Units",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6001_val2 = forms.CharField(label="Acres",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6002_val1 = forms.CharField(label="SqFt",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6002_val2 = forms.CharField(label="Acres",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6002_val3 = forms.CharField(label="Employees",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6003_val1 = forms.CharField(label="SqFt",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6003_val2 = forms.CharField(label="Acres",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6003_val3 = forms.CharField(label="Employees",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6004_val1 = forms.CharField(label="SqFt",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6004_val2 = forms.CharField(label="Acres",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6004_val3 = forms.CharField(label="Employees",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev7001_val1 = forms.CharField(label="Type",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev8001_val1 = forms.CharField(label="Type",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev10001_val1 = forms.CharField(label="Mineral",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    devtrans_id = forms.ModelChoiceField(required=False,queryset=keywords.objects.filter(keyw_pk__gt=4000).filter(keyw_pk__lt=5000),empty_label=None)
    devtrans_comment = forms.CharField(label="Comment",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'32'}))
    devpower_id = forms.ModelChoiceField(required=False,queryset=keywords.objects.filter(keyw_pk__gt=3000).filter(keyw_pk__lt=4000),empty_label=None)
    devpower_comment = forms.CharField(label="Comment",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'32'}))
    devpower_val1 = forms.CharField(label="Watts",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    devwaste_id = forms.ModelChoiceField(required=False,queryset=keywords.objects.filter(keyw_pk__gt=5000).filter(keyw_pk__lt=6000),empty_label=None)
    devwaste_comment = forms.CharField(label="Comment",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'32'}))
    dev9001_val1 = forms.CharField(label="Type",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev9001_val2 = forms.CharField(label="MGD",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    devtypes = forms.ModelMultipleChoiceField(required=False,queryset=keywords.objects.filter(keyw_keyl_fk__keyl_pk=1010).order_by('keyw_longname'),widget=forms.CheckboxSelectMultiple())
    dkey_comment_dev = forms.CharField(label="Other",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    issues = forms.ModelMultipleChoiceField(required=False,queryset=keywords.objects.filter(keyw_keyl_fk__keyl_pk=1002).order_by('keyw_longname'),widget=forms.CheckboxSelectMultiple())
    dkey_comment_issues = forms.CharField(required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    ragencies = forms.ModelMultipleChoiceField(label="Reviewing Agencies:",required=False,queryset=reviewingagencies.objects.filter(inlookup=True).order_by('rag_title'),widget=forms.SelectMultiple(attrs={'size':'10'}))

class nodform(forms.Form):
    prj_title = forms.CharField(label="Project Title:",required=True,max_length=160,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
    prj_description = forms.CharField(label="Project Description:",required=True,widget=forms.Textarea(attrs={'cols':'75','rows':'5'}))
    doc_conname = forms.CharField(label="Contact Person:",required=True,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    doc_conemail = forms.EmailField(label="E-mail:",required=True,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    doc_conphone = USPhoneNumberField(label="Phone:",required=True)
    doc_conaddress1 = forms.CharField(label="Street Address1:",required=True,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    doc_conaddress2 = forms.CharField(label="Street Address2:",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    doc_concity = forms.CharField(label="City:",required=True,max_length=32,widget=forms.TextInput(attrs={'size':'32'}))
    doc_constate = USStateField(label="State:",required=True)
    doc_conzip = USZipCodeField(label="Zip:",required=True)
    doc_location = forms.CharField(label="Document Location:",widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
    doc_latitude = forms.CharField(label="Document Latitude:",max_length=30,widget=forms.TextInput(attrs={'size':'30'}))
    doc_longitude = forms.CharField(label="Document Longitude:",max_length=30,widget=forms.TextInput(attrs={'size':'30'}))
    doc_city = forms.ModelChoiceField(label="City:",queryset=geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).order_by('geow_shortname'),empty_label="[Select City]")
    doc_county = forms.ModelChoiceField(label="County:",queryset=geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).order_by('geow_shortname'),empty_label="[Select County]")
    leadorresp = forms.ChoiceField(required=False,choices=NODAGENCY_CHOICES,widget=forms.RadioSelect(attrs={'id':'det1'}))
    doc_nodagency = forms.ModelChoiceField(required=False,queryset=leadagencies.objects.filter(inlookup=True).order_by('lag_name'),empty_label="[Select Agency]")
    doc_nod = forms.DateField(required=False,input_formats=['%Y-%m-%d'])
    det1 = forms.ChoiceField(required=False,choices=DETERMINATION_CHOICES,widget=forms.RadioSelect(attrs={'id':'det1'}))
    det2 = forms.ChoiceField(required=False,choices=DETERMINATION_CHOICES,widget=forms.RadioSelect(attrs={'id':'det2'}))
    det3 = forms.ChoiceField(required=False,choices=DETERMINATION_CHOICES,widget=forms.RadioSelect(attrs={'id':'det3'}))
    det4 = forms.ChoiceField(required=False,choices=DETERMINATION_CHOICES,widget=forms.RadioSelect(attrs={'id':'det4'}))
    det5 = forms.ChoiceField(required=False,choices=DETERMINATION_CHOICES,widget=forms.RadioSelect(attrs={'id':'det5'}))
    doc_eiravailableat = forms.CharField(required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'5'}))

class editnodform(forms.Form):
    prj_title = forms.CharField(label="Project Title:",required=False,max_length=160,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
    prj_description = forms.CharField(label="Project Description:",required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'5'}))
    doc_conagency = forms.CharField(label="Contact Agency:",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    doc_conname = forms.CharField(label="Contact Person:",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    doc_conemail = forms.EmailField(label="E-mail:",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    doc_conphone = USPhoneNumberField(label="Phone:",required=False)
    doc_conaddress1 = forms.CharField(label="Street Address1:",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    doc_conaddress2 = forms.CharField(label="Street Address2:",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    doc_concity = forms.CharField(label="City:",required=False,max_length=32,widget=forms.TextInput(attrs={'size':'32'}))
    doc_constate = USStateField(label="State:",required=False)
    doc_conzip = USZipCodeField(label="Zip:",required=False)
    doc_location = forms.CharField(label="Document Location:",required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
    doc_latitude = forms.CharField(label="Document Latitude:",required=False,max_length=30,widget=forms.TextInput(attrs={'size':'30'}))
    doc_longitude = forms.CharField(label="Document Longitude:",required=False,max_length=30,widget=forms.TextInput(attrs={'size':'30'}))
    doc_city = forms.ModelChoiceField(label="City:",required=False,queryset=geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).order_by('geow_shortname'),empty_label="[Select City]")
    doc_county = forms.ModelChoiceField(label="County:",required=False,queryset=geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).order_by('geow_shortname'),empty_label="[Select County]")
    leadorresp = forms.ChoiceField(required=False,choices=NODAGENCY_CHOICES,widget=forms.RadioSelect(attrs={'id':'det1'}))
    doc_nodagency = forms.CharField(required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    doc_nod = forms.DateField(required=False,input_formats=['%Y-%m-%d'])
    det1 = forms.ChoiceField(required=False,choices=DETERMINATION_CHOICES,widget=forms.RadioSelect(attrs={'id':'det1'}))
    det2 = forms.ChoiceField(required=False,choices=DETERMINATION_CHOICES,widget=forms.RadioSelect(attrs={'id':'det2'}))
    det3 = forms.ChoiceField(required=False,choices=DETERMINATION_CHOICES,widget=forms.RadioSelect(attrs={'id':'det3'}))
    det4 = forms.ChoiceField(required=False,choices=DETERMINATION_CHOICES,widget=forms.RadioSelect(attrs={'id':'det4'}))
    det5 = forms.ChoiceField(required=False,choices=DETERMINATION_CHOICES,widget=forms.RadioSelect(attrs={'id':'det5'}))
    doc_eiravailableat = forms.CharField(required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'5'}))

#class noeform(forms.Form):
class noeform(MapForm):
    prj_title = forms.CharField(label="Project Title:",required=True,max_length=160,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
    prj_description = forms.CharField(label="Project Description:",required=True,widget=forms.Textarea(attrs={'cols':'75','rows':'5'}))
    doc_conname = forms.CharField(label="Contact Person:",required=True,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    doc_conemail = forms.EmailField(label="E-mail:",required=True,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    doc_conphone = USPhoneNumberField(label="Phone:",required=True)
    doc_conaddress1 = forms.CharField(label="Street Address1:",required=True,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    doc_conaddress2 = forms.CharField(label="Street Address2:",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    doc_concity = forms.CharField(label="City:",required=True,max_length=32,widget=forms.TextInput(attrs={'size':'32'}))
    doc_constate = USStateField(label="State:",required=True)
    doc_conzip = USZipCodeField(label="Zip:",required=True)
    doc_location = forms.CharField(label="Document Location:",widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
    doc_latitude = forms.CharField(label="Document Latitude:",max_length=30,widget=forms.TextInput(attrs={'size':'30'}))
    doc_longitude = forms.CharField(label="Document Longitude:",max_length=30,widget=forms.TextInput(attrs={'size':'30'}))
    doc_city = forms.ModelChoiceField(label="City:",queryset=geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).order_by('geow_shortname'),empty_label="[Select City]")
    doc_county = forms.ModelChoiceField(label="County:",queryset=geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).order_by('geow_shortname'),empty_label="[Select County]")
    strleadagency2 = forms.CharField(label="Person or Agency Carrying Out Project:",required=False,max_length=45,widget=forms.TextInput(attrs={'size':'45'}))
    rdoexemptstatus = forms.ChoiceField(required=True,choices=EXEMPT_STATUS_CHOICES,initial=4,widget=forms.RadioSelect())
    strsectionnumber = forms.CharField(label="Section Number:",required=False,max_length=50,widget=forms.TextInput(attrs={'size':'50'}))
    strcodenumber = forms.CharField(label="Code Number:",required=False,max_length=50,widget=forms.TextInput(attrs={'size':'50'}))
    doc_exreasons = forms.CharField(label="Reasons why project is exempt:",required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'4'}))

    def clean(self):
        cleaned_data = super(noeform, self).clean()

        msg_strsectionnumber = u"Section Number is required for Categorical Exemption."
        msg_strcodenumber = u"Code Number is required for Statutory Exemption."

        if cleaned_data.get('rdoexemptstatus') == '4':
            strsectionnumber = cleaned_data.get('strsectionnumber')
            if strsectionnumber == '':
                self._errors['strsectionnumber'] = self.error_class([msg_strsectionnumber])
                del cleaned_data['rdoexemptstatus']
                del cleaned_data['strsectionnumber']
        if cleaned_data.get('rdoexemptstatus') == '5':
            strcodenumber = cleaned_data.get('strcodenumber')
            if strcodenumber == '':
                self._errors['strcodenumber'] = self.error_class([msg_strcodenumber])
                del cleaned_data['rdoexemptstatus']
                del cleaned_data['strcodenumber']

        return cleaned_data

class editnoeform(forms.Form):
    prj_title = forms.CharField(label="Project Title:",required=False,max_length=160,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
    prj_description = forms.CharField(label="Project Description:",required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'5'}))
    doc_conagency = forms.CharField(label="Contact Agency:",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    doc_conname = forms.CharField(label="Contact Person:",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    doc_conemail = forms.EmailField(label="E-mail:",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    doc_conphone = USPhoneNumberField(label="Phone:",required=False)
    doc_conaddress1 = forms.CharField(label="Street Address1:",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    doc_conaddress2 = forms.CharField(label="Street Address2:",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    doc_concity = forms.CharField(label="City:",required=False,max_length=32,widget=forms.TextInput(attrs={'size':'32'}))
    doc_constate = USStateField(label="State:",required=False)
    doc_conzip = USZipCodeField(label="Zip:",required=False)
    doc_location = forms.CharField(label="Document Location:",required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
    doc_latitude = forms.CharField(label="Document Latitude:",required=False,max_length=30,widget=forms.TextInput(attrs={'size':'30'}))
    doc_longitude = forms.CharField(label="Document Longitude:",required=False,max_length=30,widget=forms.TextInput(attrs={'size':'30'}))
    doc_city = forms.ModelChoiceField(label="City:",required=False,queryset=geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).order_by('geow_shortname'),empty_label="[Select City]")
    doc_county = forms.ModelChoiceField(label="County:",required=False,queryset=geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).order_by('geow_shortname'),empty_label="[Select County]")
    strleadagency2 = forms.CharField(label="Person or Agency Carrying Out Project:",required=False,max_length=45,widget=forms.TextInput(attrs={'size':'45'}))
    rdoexemptstatus = forms.ChoiceField(required=False,choices=EXEMPT_STATUS_CHOICES,widget=forms.RadioSelect())
    strsectionnumber = forms.CharField(label="Section Number:",required=False,max_length=50,widget=forms.TextInput(attrs={'size':'50'}))
    strcodenumber = forms.CharField(label="Code Number:",required=False,max_length=50,widget=forms.TextInput(attrs={'size':'50'}))
    doc_exreasons = forms.CharField(label="Reasons why project is exempt:",required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'4'}))

    def clean(self):
        cleaned_data = super(editnoeform, self).clean()

        msg_strsectionnumber = u"Section Number is required for Categorical Exemption."
        msg_strcodenumber = u"Code Number is required for Statutory Exemption."

        if cleaned_data.get('rdoexemptstatus') == '4':
            strsectionnumber = cleaned_data.get('strsectionnumber')
            if strsectionnumber == '':
                self._errors['strsectionnumber'] = self.error_class([msg_strsectionnumber])
                del cleaned_data['rdoexemptstatus']
                del cleaned_data['strsectionnumber']
        if cleaned_data.get('rdoexemptstatus') == '5':
            strcodenumber = cleaned_data.get('strcodenumber')
            if strcodenumber == '':
                self._errors['strcodenumber'] = self.error_class([msg_strcodenumber])
                del cleaned_data['rdoexemptstatus']
                del cleaned_data['strcodenumber']

        return cleaned_data

class nopform(forms.Form):
    prj_title = forms.CharField(label="Project Title:",required=True,max_length=160,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
    prj_description = forms.CharField(label="Project Description:",required=True,widget=forms.Textarea(attrs={'cols':'75','rows':'5'}))
    doc_conname = forms.CharField(label="Contact Person:",required=True,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    doc_conemail = forms.EmailField(label="E-mail:",required=True,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    doc_conphone = USPhoneNumberField(label="Phone:",required=True)
    doc_conaddress1 = forms.CharField(label="Street Address1:",required=True,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    doc_conaddress2 = forms.CharField(label="Street Address2:",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    doc_concity = forms.CharField(label="City:",required=True,max_length=32,widget=forms.TextInput(attrs={'size':'32'}))
    doc_constate = USStateField(label="State:",required=True)
    doc_conzip = USZipCodeField(label="Zip:",required=True)
    doc_location = forms.CharField(label="Document Location:",widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
    doc_latitude = forms.CharField(label="Document Latitude:",max_length=30,widget=forms.TextInput(attrs={'size':'30'}))
    doc_longitude = forms.CharField(label="Document Longitude:",max_length=30,widget=forms.TextInput(attrs={'size':'30'}))
    doc_city = forms.ModelChoiceField(label="City:",queryset=geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).order_by('geow_shortname'),empty_label="[Select City]")
    doc_county = forms.ModelChoiceField(label="County:",queryset=geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).order_by('geow_shortname'),empty_label="[Select County]")
    doc_parcelno = forms.CharField(label='Parcel No.:',required=False,max_length=96,widget=forms.TextInput(attrs={'size':'96'}))
    doc_xstreets = forms.CharField(label='Cross Streets:',required=False,max_length=96,widget=forms.TextInput(attrs={'size':'96'}))
    doc_township = forms.CharField(label='Township:',required=False,max_length=6,widget=forms.TextInput(attrs={'size':'6'}))
    doc_range = forms.CharField(label='Range:',required=False,max_length=6,widget=forms.TextInput(attrs={'size':'6'}))
    doc_section = forms.CharField(label='Section:',required=False,max_length=6,widget=forms.TextInput(attrs={'size':'6'}))
    doc_base = forms.CharField(label='Base:',required=False,max_length=8,widget=forms.TextInput(attrs={'size':'8'}))
    doc_highways = forms.CharField(label="State Hwy #:",required=False,max_length=32,widget=forms.TextInput(attrs={'size':'32'}))
    doc_airports = forms.CharField(label="Airports:",required=False,max_length=32,widget=forms.TextInput(attrs={'size':'32'}))
    doc_railways = forms.CharField(label="Railways:",required=False,max_length=32,widget=forms.TextInput(attrs={'size':'32'}))
    doc_waterways = forms.CharField(label="Waterways:",required=False,max_length=96,widget=forms.TextInput(attrs={'size':'96'}))
    doc_landuse = forms.CharField(required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
    doc_schools = forms.CharField(label="Schools:",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    actions = forms.ModelMultipleChoiceField(required=False,queryset=keywords.objects.filter(keyw_keyl_fk__keyl_pk=1001).order_by('keyw_longname'),widget=forms.CheckboxSelectMultiple())
    dkey_comment_actions = forms.CharField(required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    dev6001_val1 = forms.CharField(label="Units",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6001_val2 = forms.CharField(label="Acres",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6002_val1 = forms.CharField(label="SqFt",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6002_val2 = forms.CharField(label="Acres",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6002_val3 = forms.CharField(label="Employees",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6003_val1 = forms.CharField(label="SqFt",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6003_val2 = forms.CharField(label="Acres",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6003_val3 = forms.CharField(label="Employees",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6004_val1 = forms.CharField(label="SqFt",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6004_val2 = forms.CharField(label="Acres",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6004_val3 = forms.CharField(label="Employees",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev7001_val1 = forms.CharField(label="Type",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev8001_val1 = forms.CharField(label="Type",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev10001_val1 = forms.CharField(label="Mineral",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    devtrans_id = forms.ModelChoiceField(required=False,queryset=keywords.objects.filter(keyw_pk__gt=4000).filter(keyw_pk__lt=5000),empty_label=None)
    devtrans_comment = forms.CharField(label="Comment",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'32'}))
    devpower_id = forms.ModelChoiceField(required=False,queryset=keywords.objects.filter(keyw_pk__gt=3000).filter(keyw_pk__lt=4000),empty_label=None)
    devpower_comment = forms.CharField(label="Comment",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'32'}))
    devpower_val1 = forms.CharField(label="Watts",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    devwaste_id = forms.ModelChoiceField(required=False,queryset=keywords.objects.filter(keyw_pk__gt=5000).filter(keyw_pk__lt=6000),empty_label=None)
    devwaste_comment = forms.CharField(label="Comment",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'32'}))
    dev9001_val1 = forms.CharField(label="Type",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev9001_val2 = forms.CharField(label="MGD",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dkey_comment_dev = forms.CharField(label="Other",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'8'}))
    issues = forms.ModelMultipleChoiceField(required=False,queryset=keywords.objects.filter(keyw_keyl_fk__keyl_pk=1002).order_by('keyw_longname'),widget=forms.CheckboxSelectMultiple())
    dkey_comment_issues = forms.CharField(required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    ragencies = forms.ModelMultipleChoiceField(label="Reviewing Agencies:",required=False,queryset=reviewingagencies.objects.filter(inlookup=True).order_by('rag_title'),widget=forms.SelectMultiple(attrs={'size':'10'}))

class editnopform(forms.Form):
    prj_title = forms.CharField(label="Project Title:",required=False,max_length=160,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
    prj_description = forms.CharField(label="Project Description:",required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'5'}))
    doc_conagency = forms.CharField(label="Contact Agency:",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    doc_conname = forms.CharField(label="Contact Person:",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    doc_conemail = forms.EmailField(label="E-mail:",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    doc_conphone = USPhoneNumberField(label="Phone:",required=False)
    doc_conaddress1 = forms.CharField(label="Street Address1:",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    doc_conaddress2 = forms.CharField(label="Street Address2:",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    doc_concity = forms.CharField(label="City:",required=False,max_length=32,widget=forms.TextInput(attrs={'size':'32'}))
    doc_constate = USStateField(label="State:",required=False)
    doc_conzip = USZipCodeField(label="Zip:",required=False)
    doc_location = forms.CharField(label="Document Location:",required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
    doc_latitude = forms.CharField(label="Document Latitude:",required=False,max_length=30,widget=forms.TextInput(attrs={'size':'30'}))
    doc_longitude = forms.CharField(label="Document Longitude:",required=False,max_length=30,widget=forms.TextInput(attrs={'size':'30'}))
    doc_city = forms.ModelChoiceField(label="City:",required=False,queryset=geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).order_by('geow_shortname'),empty_label="[Select City]")
    doc_county = forms.ModelChoiceField(label="County:",required=False,queryset=geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).order_by('geow_shortname'),empty_label="[Select County]")
    doc_parcelno = forms.CharField(label='Parcel No.:',required=False,max_length=96,widget=forms.TextInput(attrs={'size':'96'}))
    doc_xstreets = forms.CharField(label='Cross Streets:',required=False,max_length=96,widget=forms.TextInput(attrs={'size':'96'}))
    doc_township = forms.CharField(label='Township:',required=False,max_length=6,widget=forms.TextInput(attrs={'size':'6'}))
    doc_range = forms.CharField(label='Range:',required=False,max_length=6,widget=forms.TextInput(attrs={'size':'6'}))
    doc_section = forms.CharField(label='Section:',required=False,max_length=6,widget=forms.TextInput(attrs={'size':'6'}))
    doc_base = forms.CharField(label='Base:',required=False,max_length=8,widget=forms.TextInput(attrs={'size':'8'}))
    doc_highways = forms.CharField(label="State Hwy #:",required=False,max_length=32,widget=forms.TextInput(attrs={'size':'32'}))
    doc_airports = forms.CharField(label="Airports:",required=False,max_length=32,widget=forms.TextInput(attrs={'size':'32'}))
    doc_railways = forms.CharField(label="Railways:",required=False,max_length=32,widget=forms.TextInput(attrs={'size':'32'}))
    doc_waterways = forms.CharField(label="Waterways:",required=False,max_length=96,widget=forms.TextInput(attrs={'size':'96'}))
    doc_landuse = forms.CharField(required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
    doc_schools = forms.CharField(label="Schools:",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    actions = forms.ModelMultipleChoiceField(required=False,queryset=keywords.objects.filter(keyw_keyl_fk__keyl_pk=1001).order_by('keyw_longname'),widget=forms.CheckboxSelectMultiple())
    dkey_comment_actions = forms.CharField(required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    dev6001_val1 = forms.CharField(label="Units",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6001_val2 = forms.CharField(label="Acres",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6002_val1 = forms.CharField(label="SqFt",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6002_val2 = forms.CharField(label="Acres",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6002_val3 = forms.CharField(label="Employees",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6003_val1 = forms.CharField(label="SqFt",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6003_val2 = forms.CharField(label="Acres",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6003_val3 = forms.CharField(label="Employees",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6004_val1 = forms.CharField(label="SqFt",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6004_val2 = forms.CharField(label="Acres",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6004_val3 = forms.CharField(label="Employees",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev7001_val1 = forms.CharField(label="Type",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev8001_val1 = forms.CharField(label="Type",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev10001_val1 = forms.CharField(label="Mineral",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    devtrans_id = forms.ModelChoiceField(required=False,queryset=keywords.objects.filter(keyw_pk__gt=4000).filter(keyw_pk__lt=5000),empty_label=None)
    devtrans_comment = forms.CharField(label="Comment",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'32'}))
    devpower_id = forms.ModelChoiceField(required=False,queryset=keywords.objects.filter(keyw_pk__gt=3000).filter(keyw_pk__lt=4000),empty_label=None)
    devpower_comment = forms.CharField(label="Comment",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'32'}))
    devpower_val1 = forms.CharField(label="Watts",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    devwaste_id = forms.ModelChoiceField(required=False,queryset=keywords.objects.filter(keyw_pk__gt=5000).filter(keyw_pk__lt=6000),empty_label=None)
    devwaste_comment = forms.CharField(label="Comment",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'32'}))
    dev9001_val1 = forms.CharField(label="Type",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev9001_val2 = forms.CharField(label="MGD",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    devtypes = forms.ModelMultipleChoiceField(required=False,queryset=keywords.objects.filter(keyw_keyl_fk__keyl_pk=1010).order_by('keyw_longname'),widget=forms.CheckboxSelectMultiple())
    dkey_comment_dev = forms.CharField(label="Other",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    issues = forms.ModelMultipleChoiceField(required=False,queryset=keywords.objects.filter(keyw_keyl_fk__keyl_pk=1002).order_by('keyw_longname'),widget=forms.CheckboxSelectMultiple())
    dkey_comment_issues = forms.CharField(required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    ragencies = forms.ModelMultipleChoiceField(label="Reviewing Agencies:",required=False,queryset=reviewingagencies.objects.filter(inlookup=True).order_by('rag_title'),widget=forms.SelectMultiple(attrs={'size':'10'}))

class attachmentsform(forms.Form):
    datt_file = forms.FileField(label='Select file to attach:',required=False,help_text='max. 42 megabytes')

class pendingdetailnocform(editnocform):
    doc_plannerregion = forms.ChoiceField(label="Assign Region:",required=True,choices=PLANNERREGION_CHOICES)

class pendingdetailnodform(editnodform):
    doc_plannerregion = forms.ChoiceField(label="Assign Region:",required=True,choices=PLANNERREGION_CHOICES)

class pendingdetailnoeform(editnoeform):
    doc_plannerregion = forms.ChoiceField(label="Assign Region:",required=True,choices=PLANNERREGION_CHOICES)

class pendingdetailnopform(editnopform):
    doc_plannerregion = forms.ChoiceField(label="Assign Region:",required=True,choices=PLANNERREGION_CHOICES)

class reviewdetailnocform(editnocform):
    doc_dept = forms.DateField(label="Start of Review:",required=False,input_formats=['%Y-%m-%d'])
    doc_clear = forms.DateField(label="End of Review:",required=False,input_formats=['%Y-%m-%d'])

class reviewdetailnodform(editnodform):
    doc_dept = forms.DateField(label="Start of Review:",required=False,input_formats=['%Y-%m-%d'])
    doc_clear = forms.DateField(label="End of Review:",required=False,input_formats=['%Y-%m-%d'])

class reviewdetailnoeform(editnoeform):
    doc_dept = forms.DateField(label="Start of Review:",required=False,input_formats=['%Y-%m-%d'])
    doc_clear = forms.DateField(label="End of Review:",required=False,input_formats=['%Y-%m-%d'])

class reviewdetailnopform(editnopform):
    doc_dept = forms.DateField(label="Start of Review:",required=False,input_formats=['%Y-%m-%d'])
    doc_clear = forms.DateField(label="End of Review:",required=False,input_formats=['%Y-%m-%d'])

class commentdetailform(forms.Form):
    drag_ragcomment = forms.CharField(label="Text Comment:",required=False,widget=forms.Textarea(attrs={'cols':'100','rows':'40'}))
    drag_file = forms.FileField(label='Select a PDF File:',help_text='max. 42 megabytes')

class usersettingsform(forms.Form):
    formID = "usersettingsform"

    region = forms.IntegerField(required=False)
    set_lag_fk = forms.ModelChoiceField(label="Lead Agency:",required=False,queryset=leadagencies.objects.filter(inlookup=True).order_by('lag_name'))
    set_rag_fk = forms.ModelChoiceField(label="Reviewing Agency:",required=False,queryset=reviewingagencies.objects.filter(inlookup=True).order_by('rag_name'))
    conphone = USPhoneNumberField(label="Phone Number:",required=False)

class chqueryform(forms.Form):
    prj_schno = forms.CharField(label="Clearinghouse Number:",max_length=12)

class findprojectform(forms.Form):
    pass
    
class geocode(forms.Form):
    address = forms.CharField(label="",max_length=254)
    
class locationEditForm(MapModelForm):
    document = forms.CharField()
    geom = EditableLayerField()

    class Meta:
        model = Locations
        maps = (
            (('geom',),
                {'layers': ['osm.mapnik'],
                'isCollection':True,
                'geometry':['point','linestring','polygon'],
                } ),
        )
 
    

