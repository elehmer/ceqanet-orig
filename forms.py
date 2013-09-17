from django import forms
from django.forms import ModelForm
from datetime import datetime, date, timedelta
from ceqanet.models import projects,documents,geowords

class QueryForm(forms.Form):
	prj_schno = forms.CharField(label="Clearinghouse Number:",max_length=12)

	date_from = forms.DateField(label="From", initial=lambda: (date.today() - timedelta(days=14)).strftime("%Y-%m-%d"),input_formats=['%Y-%m-%d'])
	date_to = forms.DateField(label="To", initial=date.today().strftime("%Y-%m-%d"),input_formats=['%Y-%m-%d'])

class AddPrjForm(forms.Form):
	prj_title = forms.CharField(label="Project Title:",max_length=160,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
	prj_description = forms.CharField(label="Project Description:",widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))

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
	txtreason = forms.CharField(label="Reasons why project is exempt:",widget=forms.Textarea(attrs={'cols':'75','rows':'4'}))
	strleadagency2 = forms.CharField(label="Person or Agency Carrying Out Project:",max_length=45,widget=forms.TextInput(attrs={'size':'45'}))
	strphone1 = forms.CharField(max_length=3,widget=forms.TextInput(attrs={'size':'3'}))
	strphone2 = forms.CharField(max_length=3,widget=forms.TextInput(attrs={'size':'3'}))
	strphone3 = forms.CharField(max_length=4,widget=forms.TextInput(attrs={'size':'4'}))

	def clean(self):
		cleaned_data = super(AddDocForm, self).clean()
		prj_title = cleaned_data.get("prj_title")
		prj_description = cleaned_data.get("prj_description")

		msg_title = u"Project Title is required."
		msg_description = u"Project Description is required."

		if prj_title == '':
			self._errors["prj_title"] = self.error_class([msg_title])
			del cleaned_data["prj_title"]
		if prj_description == '':
			self._errors["prj_description"] = self.error_class([msg_description])
			del cleaned_data["prj_description"]
		return cleaned_data

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
	pass

class noeform(forms.Form):
	doc_lagaddress1 = forms.CharField(label="Street Address1:",max_length=50,widget=forms.TextInput(attrs={'size':'50'}))
	doc_lagaddress2 = forms.CharField(label="Street Address2:",max_length=50,widget=forms.TextInput(attrs={'size':'50'}))
	doc_lagcity = forms.CharField(label="City:",max_length=30,widget=forms.TextInput(attrs={'size':'30'}))
	doc_lagstate = forms.CharField(label="State:",max_length=2,widget=forms.TextInput(attrs={'size':'2'}))
	doc_lagzip = forms.CharField(label="Zip:",max_length=10,widget=forms.TextInput(attrs={'size':'10'}))
	doc_location = forms.CharField(label="Project Location:",widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
	doc_latitude = forms.CharField(label="Project Latitude:",max_length=20,widget=forms.TextInput(attrs={'size':'20'}))
	doc_longitude = forms.CharField(label="Project Longitude:",max_length=20,widget=forms.TextInput(attrs={'size':'20'}))
	prj_description = forms.CharField(label="Project Description:",widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
	strsectionnumber = forms.CharField(label="Section Number:",max_length=50,widget=forms.TextInput(attrs={'size':'50'}))
	strcodenumber = forms.CharField(label="Code Number:",max_length=50,widget=forms.TextInput(attrs={'size':'50'}))
	txtreason = forms.CharField(label="Reasons why project is exempt:",widget=forms.Textarea(attrs={'cols':'75','rows':'4'}))
	strlagcontact = forms.CharField(label="Lead Agency Contact Person:",max_length=50,widget=forms.TextInput(attrs={'size':'50'}))
	stremail = forms.EmailField(label="E-mail:",max_length=50)
	strphone1 = forms.CharField(max_length=3,widget=forms.TextInput(attrs={'size':'3'}))
	strphone2 = forms.CharField(max_length=3,widget=forms.TextInput(attrs={'size':'3'}))
	strphone3 = forms.CharField(max_length=3,widget=forms.TextInput(attrs={'size':'3'}))

class nopform(forms.Form):
	pass

class InputForm(forms.Form):
	pass

class DocReviewForm(forms.Form):
	pass