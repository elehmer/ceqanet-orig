from django import forms
from django.forms import ModelForm
from datetime import datetime, date, timedelta
from ceqanet.models import projects,documents,geowords,reviewingagencies,leadagencies,keywords,doctypes
from localflavor.us.forms import USPhoneNumberField,USStateField,USZipCodeField

class QueryForm(forms.Form):
	prj_schno = forms.CharField(label="Clearinghouse Number:",max_length=12)

	date_from = forms.DateField(label="From", initial=lambda: (date.today() - timedelta(days=14)).strftime("%Y-%m-%d"),input_formats=['%Y-%m-%d'])
	date_to = forms.DateField(label="To", initial=date.today().strftime("%Y-%m-%d"),input_formats=['%Y-%m-%d'])

class AddDocForm(forms.Form):
	prj_title = forms.CharField(label="Project Title:",required=False,max_length=160,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
	prj_description = forms.CharField(label="Project Description:",required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
	doc_conname = forms.CharField(label="Contact Person:",max_length=50,widget=forms.TextInput(attrs={'size':'50'}))
	doc_conemail = forms.EmailField(label="E-mail:",max_length=64)
	doc_conaddress1 = forms.CharField(label="Street Address1:",max_length=50,widget=forms.TextInput(attrs={'size':'50'}))
	doc_conaddress2 = forms.CharField(label="Street Address2:",required=False,max_length=50,widget=forms.TextInput(attrs={'size':'50'}))
	doc_concity = forms.CharField(label="City:",max_length=30,widget=forms.TextInput(attrs={'size':'30'}))
	doc_constate = forms.CharField(label="State:",max_length=2,widget=forms.TextInput(attrs={'size':'2'}))
	doc_conzip = forms.CharField(label="Zip:",max_length=10,widget=forms.TextInput(attrs={'size':'10'}))
	doc_location = forms.CharField(label="Document Location:",widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
	doc_county = forms.ModelChoiceField(label="County:",queryset=geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).order_by('geow_shortname'),empty_label="[Select County]")
	doc_city = forms.ModelChoiceField(label="City:",queryset=geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).order_by('geow_shortname'),empty_label="[Select City]")
	doc_latitude = forms.CharField(label="Document Latitude:",max_length=20,widget=forms.TextInput(attrs={'size':'20'}))
	doc_longitude = forms.CharField(label="Document Longitude:",max_length=20,widget=forms.TextInput(attrs={'size':'20'}))
	strsectionnumber = forms.CharField(label="Section Number:",required=False,max_length=50,widget=forms.TextInput(attrs={'size':'50'}))
	strcodenumber = forms.CharField(label="Code Number:",required=False,max_length=50,widget=forms.TextInput(attrs={'size':'50'}))
	txtreason = forms.CharField(label="Reasons why project is exempt:",required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'4'}))
	strleadagency2 = forms.CharField(label="Person or Agency Carrying Out Project:",required=False,max_length=45,widget=forms.TextInput(attrs={'size':'45'}))
	strphone1 = forms.CharField(max_length=3,widget=forms.TextInput(attrs={'size':'3'}))
	strphone2 = forms.CharField(max_length=3,widget=forms.TextInput(attrs={'size':'3'}))
	strphone3 = forms.CharField(max_length=4,widget=forms.TextInput(attrs={'size':'4'}))
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
	doc_actionnotes = forms.CharField(required=False,max_length=32,widget=forms.TextInput(attrs={'size':'32'}))
	doc_issuesnotes = forms.CharField(required=False,max_length=32,widget=forms.TextInput(attrs={'size':'32'}))
	ragencies = forms.ModelMultipleChoiceField(label="Reviewing Agencies:",required=False,queryset=reviewingagencies.objects.filter(inlookup=True).order_by('rag_title'),widget=forms.SelectMultiple(attrs={'size':'10'}))

	# def clean(self):
	# 	cleaned_data = super(AddDocForm, self).clean()
	# 	prj_title = cleaned_data.get("prj_title")
	# 	prj_description = cleaned_data.get("prj_description")

	# 	msg_title = u"Project Title is required."
	# 	msg_description = u"Project Description is required."

	# 	if prj_title == '':
	# 		self._errors["prj_title"] = self.error_class([msg_title])
	# 		del cleaned_data["prj_title"]
	# 	if prj_description == '':
	# 		self._errors["prj_description"] = self.error_class([msg_description])
	# 		del cleaned_data["prj_description"]
	# 	return cleaned_data

class submitform(forms.Form):
	NOC = 'NOC'
	NOD = 'NOD'
	NOE = 'NOE'
	NOP = 'NOP'

	DOCUMENT_TYPES = (
		(NOC,'NOC'),
		(NOD,'NOD'),
		(NOE,'NOE'),
		(NOP,'NOP')
	)

	YES = 'yes'
	NO = 'no'

	PROJECT_EXISTS = (
		(YES,'Yes'),
		(NO,'No')
	)

	doctype = forms.ChoiceField(required=True,choices=DOCUMENT_TYPES,initial=NOE)
	prjtoggle = forms.ChoiceField(required=True,choices=PROJECT_EXISTS,initial=NO,widget=forms.RadioSelect())

class nocform(forms.Form):
	prj_title = forms.CharField(label="Project Title:",required=True,max_length=160,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
	prj_description = forms.CharField(label="Project Description:",required=True,widget=forms.Textarea(attrs={'cols':'75','rows':'5'}))
	doc_conname = forms.CharField(label="Contact Person:",required=True,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
	doc_conemail = forms.EmailField(label="E-mail:",required=True,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
	doc_conphone = USPhoneNumberField(label="Phone:",required=True)
	doc_conaddress1 = forms.CharField(label="Street Address1:",required=True,max_length=50,widget=forms.TextInput(attrs={'size':'50'}))
	doc_conaddress2 = forms.CharField(label="Street Address2:",required=False,max_length=50,widget=forms.TextInput(attrs={'size':'50'}))
	doc_concity = forms.CharField(label="City:",required=True,max_length=30,widget=forms.TextInput(attrs={'size':'30'}))
	doc_constate = USStateField(label="State:",required=True)
	doc_conzip = USZipCodeField(label="Zip:",required=True)
	doc_location = forms.CharField(label="Document Location:",widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
	doc_latitude = forms.CharField(label="Document Latitude:",max_length=20,widget=forms.TextInput(attrs={'size':'20'}))
	doc_longitude = forms.CharField(label="Document Longitude:",max_length=20,widget=forms.TextInput(attrs={'size':'20'}))
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
	devpower_id = forms.ModelChoiceField(required=False,queryset=keywords.objects.filter(keyw_pk__gt=3000).filter(keyw_pk__lt=4000),empty_label=None)
	devpower_val1 = forms.CharField(label="Watts",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
	devwaste_id = forms.ModelChoiceField(required=False,queryset=keywords.objects.filter(keyw_pk__gt=5000).filter(keyw_pk__lt=6000),empty_label=None)
	dev9001_val1 = forms.CharField(label="Type",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
	dev9001_val2 = forms.CharField(label="MGD",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
	dkey_comment_dev = forms.CharField(label="Other",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'8'}))
	dkey_comment_issues = forms.CharField(required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
	ragencies = forms.ModelMultipleChoiceField(label="Reviewing Agencies:",required=False,queryset=reviewingagencies.objects.filter(inlookup=True).order_by('rag_title'),widget=forms.SelectMultiple(attrs={'size':'10'}))

class editnocform(forms.Form):
	prj_title = forms.CharField(label="Project Title:",required=False,max_length=160,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
	prj_description = forms.CharField(label="Project Description:",required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'5'}))
	doc_conagency = forms.CharField(label="Contact Agency:",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
	doc_conname = forms.CharField(label="Contact Person:",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
	doc_conemail = forms.EmailField(label="E-mail:",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
	doc_conphone = USPhoneNumberField(label="Phone:",required=False)
	doc_conaddress1 = forms.CharField(label="Street Address1:",required=False,max_length=50,widget=forms.TextInput(attrs={'size':'50'}))
	doc_conaddress2 = forms.CharField(label="Street Address2:",required=False,max_length=50,widget=forms.TextInput(attrs={'size':'50'}))
	doc_concity = forms.CharField(label="City:",required=False,max_length=30,widget=forms.TextInput(attrs={'size':'30'}))
	doc_constate = USStateField(label="State:",required=False)
	doc_conzip = USZipCodeField(label="Zip:",required=False)
	doc_location = forms.CharField(label="Document Location:",required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
	doc_latitude = forms.CharField(label="Document Latitude:",required=False,max_length=20,widget=forms.TextInput(attrs={'size':'20'}))
	doc_longitude = forms.CharField(label="Document Longitude:",required=False,max_length=20,widget=forms.TextInput(attrs={'size':'20'}))
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
	doc_conaddress1 = forms.CharField(label="Street Address1:",required=True,max_length=50,widget=forms.TextInput(attrs={'size':'50'}))
	doc_conaddress2 = forms.CharField(label="Street Address2:",required=False,max_length=50,widget=forms.TextInput(attrs={'size':'50'}))
	doc_concity = forms.CharField(label="City:",required=True,max_length=30,widget=forms.TextInput(attrs={'size':'30'}))
	doc_constate = USStateField(label="State:",required=True)
	doc_conzip = USZipCodeField(label="Zip:",required=True)
	doc_location = forms.CharField(label="Document Location:",widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
	doc_latitude = forms.CharField(label="Document Latitude:",max_length=20,widget=forms.TextInput(attrs={'size':'20'}))
	doc_longitude = forms.CharField(label="Document Longitude:",max_length=20,widget=forms.TextInput(attrs={'size':'20'}))
	doc_city = forms.ModelChoiceField(label="City:",queryset=geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).order_by('geow_shortname'),empty_label="[Select City]")
	doc_county = forms.ModelChoiceField(label="County:",queryset=geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).order_by('geow_shortname'),empty_label="[Select County]")
	doc_nodbylead = forms.BooleanField(required=False)
	doc_nodbyresp = forms.BooleanField(required=False)
	doc_nodagency = forms.CharField(required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
	doc_nod = forms.DateField(required=False,input_formats=['%Y-%m-%d'])
	doc_detsigeffect = forms.BooleanField(required=False)
	doc_detnotsigeffect = forms.BooleanField(required=False)
	doc_deteir = forms.BooleanField(required=False)
	doc_detnegdec = forms.BooleanField(required=False)
	doc_detmitigation = forms.BooleanField(required=False)
	doc_detnotmitigation = forms.BooleanField(required=False)
	doc_detconsider = forms.BooleanField(required=False)
	doc_detnotconsider = forms.BooleanField(required=False)
	doc_detfindings = forms.BooleanField(required=False)
	doc_detnotfindings = forms.BooleanField(required=False)
	doc_eiravailableat = forms.CharField(required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'5'}))

class editnodform(forms.Form):
	prj_title = forms.CharField(label="Project Title:",required=False,max_length=160,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
	prj_description = forms.CharField(label="Project Description:",required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'5'}))
	doc_conagency = forms.CharField(label="Contact Agency:",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
	doc_conname = forms.CharField(label="Contact Person:",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
	doc_conemail = forms.EmailField(label="E-mail:",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
	doc_conphone = USPhoneNumberField(label="Phone:",required=False)
	doc_conaddress1 = forms.CharField(label="Street Address1:",required=False,max_length=50,widget=forms.TextInput(attrs={'size':'50'}))
	doc_conaddress2 = forms.CharField(label="Street Address2:",required=False,max_length=50,widget=forms.TextInput(attrs={'size':'50'}))
	doc_concity = forms.CharField(label="City:",required=False,max_length=30,widget=forms.TextInput(attrs={'size':'30'}))
	doc_constate = USStateField(label="State:",required=False)
	doc_conzip = USZipCodeField(label="Zip:",required=False)
	doc_location = forms.CharField(label="Document Location:",required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
	doc_latitude = forms.CharField(label="Document Latitude:",required=False,max_length=20,widget=forms.TextInput(attrs={'size':'20'}))
	doc_longitude = forms.CharField(label="Document Longitude:",required=False,max_length=20,widget=forms.TextInput(attrs={'size':'20'}))
	doc_city = forms.ModelChoiceField(label="City:",required=False,queryset=geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).order_by('geow_shortname'),empty_label="[Select City]")
	doc_county = forms.ModelChoiceField(label="County:",required=False,queryset=geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).order_by('geow_shortname'),empty_label="[Select County]")
	doc_nodbylead = forms.BooleanField(required=False)
	doc_nodbyresp = forms.BooleanField(required=False)
	doc_nodagency = forms.CharField(required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
	doc_nod = forms.DateField(required=False,input_formats=['%Y-%m-%d'])
	doc_detsigeffect = forms.BooleanField(required=False)
	doc_detnotsigeffect = forms.BooleanField(required=False)
	doc_deteir = forms.BooleanField(required=False)
	doc_detnegdec = forms.BooleanField(required=False)
	doc_detmitigation = forms.BooleanField(required=False)
	doc_detnotmitigation = forms.BooleanField(required=False)
	doc_detconsider = forms.BooleanField(required=False)
	doc_detnotconsider = forms.BooleanField(required=False)
	doc_detfindings = forms.BooleanField(required=False)
	doc_detnotfindings = forms.BooleanField(required=False)
	doc_eiravailableat = forms.CharField(required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'5'}))

class noeform(forms.Form):
	EXMINISTERIAL = 1
	EXDECLARED = 2
	EXEMERGENCY = 3
	EXCATEGORICAL = 4
	EXSTATUTORY = 5

	EXEMPT_STATUS_CHOICES = (
		(EXMINISTERIAL,'Ministerial (Sec.21080(b)(1); 15268);'),
		(EXDECLARED,'Declared Emergency (Sec. 21080(b)(3);15269(a));'),
		(EXEMERGENCY,'Emergency Project (Sec. 21080(b)(4); 15269(b)(c));'),
		(EXCATEGORICAL,'Categorical Exemption. State type and section number:'),
		(EXSTATUTORY,'Statutory Exemptions. State code number:')
	)

	prj_title = forms.CharField(label="Project Title:",required=True,max_length=160,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
	prj_description = forms.CharField(label="Project Description:",required=True,widget=forms.Textarea(attrs={'cols':'75','rows':'5'}))
	doc_conname = forms.CharField(label="Contact Person:",required=True,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
	doc_conemail = forms.EmailField(label="E-mail:",required=True,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
	doc_conphone = USPhoneNumberField(label="Phone:",required=True)
	doc_conaddress1 = forms.CharField(label="Street Address1:",required=True,max_length=50,widget=forms.TextInput(attrs={'size':'50'}))
	doc_conaddress2 = forms.CharField(label="Street Address2:",required=False,max_length=50,widget=forms.TextInput(attrs={'size':'50'}))
	doc_concity = forms.CharField(label="City:",required=True,max_length=30,widget=forms.TextInput(attrs={'size':'30'}))
	doc_constate = USStateField(label="State:",required=True)
	doc_conzip = USZipCodeField(label="Zip:",required=True)
	doc_location = forms.CharField(label="Document Location:",widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
	doc_latitude = forms.CharField(label="Document Latitude:",max_length=20,widget=forms.TextInput(attrs={'size':'20'}))
	doc_longitude = forms.CharField(label="Document Longitude:",max_length=20,widget=forms.TextInput(attrs={'size':'20'}))
	doc_city = forms.ModelChoiceField(label="City:",queryset=geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).order_by('geow_shortname'),empty_label="[Select City]")
	doc_county = forms.ModelChoiceField(label="County:",queryset=geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).order_by('geow_shortname'),empty_label="[Select County]")
	strleadagency2 = forms.CharField(label="Person or Agency Carrying Out Project:",required=False,max_length=45,widget=forms.TextInput(attrs={'size':'45'}))
	rdoexemptstatus = forms.ChoiceField(required=True,choices=EXEMPT_STATUS_CHOICES,initial=EXCATEGORICAL,widget=forms.RadioSelect())
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
	EXMINISTERIAL = 1
	EXDECLARED = 2
	EXEMERGENCY = 3
	EXCATEGORICAL = 4
	EXSTATUTORY = 5

	EXEMPT_STATUS_CHOICES = (
		(EXMINISTERIAL,'Ministerial (Sec.21080(b)(1); 15268);'),
		(EXDECLARED,'Declared Emergency (Sec. 21080(b)(3);15269(a));'),
		(EXEMERGENCY,'Emergency Project (Sec. 21080(b)(4); 15269(b)(c));'),
		(EXCATEGORICAL,'Categorical Exemption. State type and section number:'),
		(EXSTATUTORY,'Statutory Exemptions. State code number:')
	)

	prj_title = forms.CharField(label="Project Title:",required=False,max_length=160,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
	prj_description = forms.CharField(label="Project Description:",required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'5'}))
	doc_conagency = forms.CharField(label="Contact Agency:",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
	doc_conname = forms.CharField(label="Contact Person:",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
	doc_conemail = forms.EmailField(label="E-mail:",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
	doc_conphone = USPhoneNumberField(label="Phone:",required=False)
	doc_conaddress1 = forms.CharField(label="Street Address1:",required=False,max_length=50,widget=forms.TextInput(attrs={'size':'50'}))
	doc_conaddress2 = forms.CharField(label="Street Address2:",required=False,max_length=50,widget=forms.TextInput(attrs={'size':'50'}))
	doc_concity = forms.CharField(label="City:",required=False,max_length=30,widget=forms.TextInput(attrs={'size':'30'}))
	doc_constate = USStateField(label="State:",required=False)
	doc_conzip = USZipCodeField(label="Zip:",required=False)
	doc_location = forms.CharField(label="Document Location:",required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
	doc_latitude = forms.CharField(label="Document Latitude:",required=False,max_length=20,widget=forms.TextInput(attrs={'size':'20'}))
	doc_longitude = forms.CharField(label="Document Longitude:",required=False,max_length=20,widget=forms.TextInput(attrs={'size':'20'}))
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
	doc_conaddress1 = forms.CharField(label="Street Address1:",required=True,max_length=50,widget=forms.TextInput(attrs={'size':'50'}))
	doc_conaddress2 = forms.CharField(label="Street Address2:",required=False,max_length=50,widget=forms.TextInput(attrs={'size':'50'}))
	doc_concity = forms.CharField(label="City:",required=True,max_length=30,widget=forms.TextInput(attrs={'size':'30'}))
	doc_constate = USStateField(label="State:",required=True)
	doc_conzip = USZipCodeField(label="Zip:",required=True)
	doc_location = forms.CharField(label="Document Location:",widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
	doc_latitude = forms.CharField(label="Document Latitude:",max_length=20,widget=forms.TextInput(attrs={'size':'20'}))
	doc_longitude = forms.CharField(label="Document Longitude:",max_length=20,widget=forms.TextInput(attrs={'size':'20'}))
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
	devpower_id = forms.ModelChoiceField(required=False,queryset=keywords.objects.filter(keyw_pk__gt=3000).filter(keyw_pk__lt=4000),empty_label=None)
	devpower_val1 = forms.CharField(label="Watts",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
	devwaste_id = forms.ModelChoiceField(required=False,queryset=keywords.objects.filter(keyw_pk__gt=5000).filter(keyw_pk__lt=6000),empty_label=None)
	dev9001_val1 = forms.CharField(label="Type",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
	dev9001_val2 = forms.CharField(label="MGD",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
	dev11001_val1 = forms.CharField(label="Other",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
	doc_actionnotes = forms.CharField(required=False,max_length=32,widget=forms.TextInput(attrs={'size':'32'}))
	doc_issuesnotes = forms.CharField(required=False,max_length=32,widget=forms.TextInput(attrs={'size':'32'}))
	ragencies = forms.ModelMultipleChoiceField(label="Reviewing Agencies:",required=False,queryset=reviewingagencies.objects.filter(inlookup=True).order_by('rag_title'),widget=forms.SelectMultiple(attrs={'size':'10'}))

class editnopform(forms.Form):
	prj_title = forms.CharField(label="Project Title:",required=False,max_length=160,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
	prj_description = forms.CharField(label="Project Description:",required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'5'}))
	doc_conagency = forms.CharField(label="Contact Agency:",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
	doc_conname = forms.CharField(label="Contact Person:",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
	doc_conemail = forms.EmailField(label="E-mail:",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
	doc_conphone = USPhoneNumberField(label="Phone:",required=False)
	doc_conaddress1 = forms.CharField(label="Street Address1:",required=False,max_length=50,widget=forms.TextInput(attrs={'size':'50'}))
	doc_conaddress2 = forms.CharField(label="Street Address2:",required=False,max_length=50,widget=forms.TextInput(attrs={'size':'50'}))
	doc_concity = forms.CharField(label="City:",required=False,max_length=30,widget=forms.TextInput(attrs={'size':'30'}))
	doc_constate = USStateField(label="State:",required=False)
	doc_conzip = USZipCodeField(label="Zip:",required=False)
	doc_location = forms.CharField(label="Document Location:",required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
	doc_latitude = forms.CharField(label="Document Latitude:",required=False,max_length=20,widget=forms.TextInput(attrs={'size':'20'}))
	doc_longitude = forms.CharField(label="Document Longitude:",required=False,max_length=20,widget=forms.TextInput(attrs={'size':'20'}))
	doc_city = forms.ModelChoiceField(label="City:",required=False,queryset=geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).order_by('geow_shortname'),empty_label="[Select City]")
	doc_county = forms.ModelChoiceField(label="County:",required=False,queryset=geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).order_by('geow_shortname'),empty_label="[Select County]")

class DocReviewForm(forms.Form):
	pass

class pendingdetailform(forms.Form):
	pass

class reviewdetailform(forms.Form):
	doc_dept = forms.DateField(label="Start of Review:",required=False,input_formats=['%Y-%m-%d'])
	doc_clear = forms.DateField(label="End of Review:",required=False,input_formats=['%Y-%m-%d'])

class commentdetailform(forms.Form):
	drag_ragcomment = forms.CharField(label="Comment:",required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'4'}))

class usersettingsform(forms.Form):
	formID = "usersettingsform"

	region = forms.IntegerField(required=False)
	set_lag_fk = forms.ModelChoiceField(label="Lead Agency:",required=False,queryset=leadagencies.objects.filter(inlookup=True).order_by('lag_name'))
	set_rag_fk = forms.ModelChoiceField(label="Reviewing Agency:",required=False,queryset=reviewingagencies.objects.filter(inlookup=True).order_by('rag_name'))
	conphone = USPhoneNumberField(label="Phone Number:",required=False)