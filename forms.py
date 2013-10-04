from django import forms
from django.forms import ModelForm
from datetime import datetime, date, timedelta
from ceqanet.models import projects,documents,geowords,reviewingagencies,leadagencies
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

class NOEeditForm(ModelForm):
	formID = "NOEeditForm"

	class Meta:
		model = documents
		fields = ('doc_schno','doc_doctype','doc_conname','doc_conemail','doc_conaddress1','doc_conaddress2','doc_concity','doc_constate','doc_conzip','doc_county','doc_city','doc_region','doc_xstreets','doc_parcelno','doc_township','doc_range','doc_section','doc_base','doc_location','doc_exreasons')


class SubmitForm(forms.Form):
	pass

class nocform(ModelForm):
	prj_title = forms.CharField(label="Project Title:",max_length=160,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
	prj_schno = forms.CharField(label="Clearinghouse Number:",max_length=12)

	class Meta:
		model = projects
		fields = ('prj_title','prj_schno')

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

class nopform(forms.Form):
	pass

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