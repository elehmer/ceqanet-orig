from django import forms
from django.forms import ModelForm
from datetime import datetime, date, timedelta
from ceqanet.models import projects

class QueryForm(forms.Form):
	prj_schno = forms.CharField(label="Clearinghouse Number:",max_length=12)

	date_from = forms.DateField(label="From", initial=lambda: (date.today() - timedelta(days=14)).strftime("%Y-%m-%d"),input_formats=['%Y-%m-%d'])
	date_to = forms.DateField(label="To", initial=date.today().strftime("%Y-%m-%d"),input_formats=['%Y-%m-%d'])

class AddPrjForm(forms.Form):
	prj_title = forms.CharField(label="Project Title:",max_length=160,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
	prj_description = forms.CharField(label="Project Description:",widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))

class AddDocForm(forms.Form):
	prj_title = forms.CharField(label="Project Title:",max_length=160,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
	prj_description = forms.CharField(label="Project Description:",widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
	doc_lagaddress1 = forms.CharField(label="Street Address1:",max_length=50,widget=forms.TextInput(attrs={'size':'50'}))
	doc_lagaddress2 = forms.CharField(label="Street Address2:",max_length=50,widget=forms.TextInput(attrs={'size':'50'}))
	doc_lagcity = forms.CharField(label="City:",max_length=30,widget=forms.TextInput(attrs={'size':'30'}))
	doc_lagstate = forms.CharField(label="State:",max_length=2,widget=forms.TextInput(attrs={'size':'2'}))
	doc_lagzip = forms.CharField(label="Zip:",max_length=10,widget=forms.TextInput(attrs={'size':'10'}))
	doc_location = forms.CharField(label="Document Location:",widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
	doc_latitude = forms.CharField(label="Document Latitude:",max_length=20,widget=forms.TextInput(attrs={'size':'20'}))
	doc_longitude = forms.CharField(label="Document Longitude:",max_length=20,widget=forms.TextInput(attrs={'size':'20'}))
	strsectionnumber = forms.CharField(label="Section Number:",max_length=50,widget=forms.TextInput(attrs={'size':'50'}))
	strcodenumber = forms.CharField(label="Code Number:",max_length=50,widget=forms.TextInput(attrs={'size':'50'}))
	txtreason = forms.CharField(label="Reasons why project is exempt:",widget=forms.Textarea(attrs={'cols':'75','rows':'4'}))
	strlagcontact = forms.CharField(label="Lead Agency Contact Person:",max_length=50,widget=forms.TextInput(attrs={'size':'50'}))
	stremail = forms.EmailField(label="E-mail:",max_length=50)
	strphone1 = forms.CharField(max_length=3,widget=forms.TextInput(attrs={'size':'3'}))
	strphone2 = forms.CharField(max_length=3,widget=forms.TextInput(attrs={'size':'3'}))
	strphone3 = forms.CharField(max_length=3,widget=forms.TextInput(attrs={'size':'3'}))

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