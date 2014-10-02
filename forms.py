from django import forms
from django.forms import ModelForm
from olwidget.forms import  MapModelForm
from olwidget.fields import EditableLayerField
from olwidget.widgets import EditableMap
from datetime import datetime, date, timedelta
from django.contrib.auth.models import Group
from ceqanet.models import projects,documents,geowords,reviewingagencies,leadagencies,keywords,doctypes,docattachments,Locations,holidays
from localflavor.us.forms import USPhoneNumberField,USStateField,USZipCodeField
from enumerations import DOCUMENT_TYPES,PROJECT_EXISTS,EXEMPT_STATUS_CHOICES,PLANNERREGION_CHOICES,COLATION_CHOICES,PRJ_SORT_FIELDS,DOC_SORT_FIELDS,RDODATE_CHOICES,RDOPLACE_CHOICES,RDOLAG_CHOICES,RDORAG_CHOICES,RDODOCTYPE_CHOICES,DETERMINATION_CHOICES,NODAGENCY_CHOICES,RDOLAT_CHOICES,RDODEVTYPE_CHOICES,RDOISSUE_CHOICES,RDOTITLE_CHOICES,RDODESCRIPTION_CHOICES,UPGRADE_CHOICES,COMMENT_CHOICES,NODFEESPAID_CHOICES
from django.contrib.admin.widgets import FilteredSelectMultiple

class MapForm(forms.Form):
    '''Reusable Map enhancement to forms, inherited by document forms needing location entry'''
    geom = forms.CharField(label="Geography:",widget=EditableMap(options={'layers': ['osm.mapnik'],
                                                    'isCollection':True, 
                                                    'geometry':['point','polygon'],
                                                    'default_lat': 37.424431833728114,
                                                    'default_lon': -121.90515908415186,'default_zoom':6},template=None))
    
class basicsearchform(forms.Form):
    prj_schno = forms.CharField(label="Clearinghouse Number:",required=True,max_length=12)
    colation = forms.ChoiceField(label="Search Database By:",required=True,choices=COLATION_CHOICES,initial='document',widget=forms.RadioSelect())

class advancedsearchform(forms.Form):
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
    rdotitle = forms.ChoiceField(label="Project Title Contains:",required=True,choices=RDOTITLE_CHOICES,initial='all',widget=forms.RadioSelect(attrs={'id':'rdotitle'}))
    titlestr = forms.CharField(label="Project Title Contains:",required=False,max_length=100,widget=forms.TextInput(attrs={'size':'64'}))
    rdodescription = forms.ChoiceField(label="Project Description Contains:",required=True,choices=RDODESCRIPTION_CHOICES,initial='all',widget=forms.RadioSelect(attrs={'id':'rdodescription'}))
    descriptionstr = forms.CharField(label="Project Description Contains:",required=False,max_length=100,widget=forms.TextInput(attrs={'size':'64'}))
    colation = forms.ChoiceField(label="Search Database By:",required=True,choices=COLATION_CHOICES,initial='document',widget=forms.RadioSelect(attrs={'id':'colation'}))

class prjlistform(forms.Form):
    sortfld = forms.ChoiceField(label="Sort Results By:",required=True,choices=PRJ_SORT_FIELDS,initial='-prj_schno')

class doclistform(forms.Form):
    sortfld = forms.ChoiceField(label="Sort Results By:",required=True,choices=DOC_SORT_FIELDS,initial='-doc_prj_fk__prj_schno')

class submitform(forms.Form):
    doctype = forms.ChoiceField(required=True,choices=DOCUMENT_TYPES,initial='NOC')
    prjtoggle = forms.ChoiceField(required=True,choices=PROJECT_EXISTS,initial='no',widget=forms.RadioSelect(attrs={'id':'prjtoggle','class':'prjtoggle'}))

class basedocumentform(MapForm):
    prj_title = forms.CharField(label="Project Title:",required=True,max_length=160,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
    prj_description = forms.CharField(label="Project Description:",required=True,widget=forms.Textarea(attrs={'cols':'75','rows':'5'}))
    doc_title = forms.CharField(label="Alternate Title:",required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
    doc_description = forms.CharField(label="Alternate Description:",required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'5'}))
    doc_conname = forms.CharField(label="Contact Person:",required=True,max_length=64,widget=forms.TextInput(attrs={'size':'50'}))
    doc_conemail = forms.EmailField(label="E-mail:",required=True,max_length=64,widget=forms.TextInput(attrs={'size':'50'}))
    doc_conphone = USPhoneNumberField(label="Phone:",required=True)
    doc_conaddress1 = forms.CharField(label="Street Address1:",required=True,max_length=64,widget=forms.TextInput(attrs={'size':'50'}))
    doc_conaddress2 = forms.CharField(label="Street Address2:",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'50'}))
    doc_concity = forms.CharField(label="City:",required=True,max_length=32,widget=forms.TextInput(attrs={'size':'32'}))
    doc_constate = USStateField(label="State:",required=True)
    doc_conzip = USZipCodeField(label="Zip:",required=True)
    doc_location = forms.CharField(label="Document Location:",required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
    doc_latitude = forms.FloatField(label="Latitude:",required=True,widget=forms.TextInput(attrs={'size':'30'}))
    doc_longitude = forms.FloatField(label="Longitude:",required=True,widget=forms.TextInput(attrs={'size':'30'}))
    counties = forms.ModelMultipleChoiceField(label="Counties:",required=False,queryset=geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).order_by('geow_shortname'),widget=forms.SelectMultiple(attrs={'size':'8'}))
    cities = forms.ModelMultipleChoiceField(label="Cities:",required=False,queryset=geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).order_by('geow_shortname'),widget=forms.SelectMultiple(attrs={'size':'8'}))
    statewide = forms.ChoiceField(required=True,choices=PROJECT_EXISTS,initial='no',widget=forms.RadioSelect(attrs={'id':'statewide','class':'statewide'}))

    def clean(self):
        cleaned_data = super(basedocumentform, self).clean()

        msg_countyerror = u"County is Required."

        if cleaned_data.get('statewide') == 'no':
            if cleaned_data.get('counties') == None:
                self._errors['counties'] = self.error_class([msg_countyerror])
                del cleaned_data['counties']

        msg_cityerror = u"City Not Within County Specified: "

        if cleaned_data.get('cities') != None:
            if cleaned_data.get('counties') != None:
                for cty in cleaned_data.get('cities'):
                    if cty.geow_parent_fk not in cleaned_data.get('counties'):
                        self._errors['cities'] = self.error_class([msg_cityerror + cty.geow_shortname])
                        del cleaned_data['cities']
        return cleaned_data

class nodform(basedocumentform):
    leadorresp = forms.ChoiceField(required=True,choices=NODAGENCY_CHOICES,widget=forms.RadioSelect(attrs={'id':'lorr','class':'lorr'}))
    doc_nodagency = forms.ModelChoiceField(required=True,queryset=leadagencies.objects.filter(inlookup=True).order_by('lag_name'),empty_label="[Select Agency]",widget=forms.Select(attrs={'id':'nodagency','class':'nodagency'}))
    #leadorresp = forms.CharField(required=True,max_length=10,widget=forms.HiddenInput())
    #doc_nodagency = forms.CharField(required=True,max_length=20,widget=forms.HiddenInput())
    doc_nod = forms.DateField(required=True,input_formats=['%Y-%m-%d'])
    det1 = forms.ChoiceField(required=True,choices=DETERMINATION_CHOICES,widget=forms.RadioSelect(attrs={'id':'det1'}))
    det2 = forms.ChoiceField(required=True,choices=DETERMINATION_CHOICES,widget=forms.RadioSelect(attrs={'id':'det2'}))
    det3 = forms.ChoiceField(required=True,choices=DETERMINATION_CHOICES,widget=forms.RadioSelect(attrs={'id':'det3'}))
    det4 = forms.ChoiceField(required=True,choices=DETERMINATION_CHOICES,widget=forms.RadioSelect(attrs={'id':'det4'}))
    det5 = forms.ChoiceField(required=True,choices=DETERMINATION_CHOICES,widget=forms.RadioSelect(attrs={'id':'det5'}))
    doc_eiravailableat = forms.CharField(required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'5'}))
    doc_nodfeespaid = forms.ChoiceField(required=True,choices=NODFEESPAID_CHOICES,widget=forms.RadioSelect(attrs={'id':'fees','class':'fees'}))
    prj_applicant = forms.CharField(label="Project Applicant:",required=True,max_length=64,widget=forms.TextInput(attrs={'size':'50'}))

class editnodform(nodform):
    def __init__(self, *args, **kwargs):
        super(editnodform, self).__init__(*args, **kwargs)
        self.fields['geom'].required = False
        self.fields['doc_conemail'].required = False
        self.fields['doc_nodfeespaid'].required = False
        self.fields['prj_applicant'].required = False
    doc_latitude = forms.CharField(label="Document Latitude:",required=False,widget=forms.TextInput(attrs={'size':'30'}))
    doc_longitude = forms.CharField(label="Document Longitude:",required=False,widget=forms.TextInput(attrs={'size':'30'}))
    doc_conphone = forms.CharField(required=True,max_length=32,widget=forms.TextInput(attrs={'size':'32'}))
    doc_nodagency = forms.CharField(required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    doc_clerknotes = forms.CharField(label="Additional Notes:",required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'4'}))

class noeform(basedocumentform):
    doc_approve_noe = forms.CharField(label="Agency Approving Project:",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    doc_carryout_noe = forms.CharField(label="Person or Agency Carrying Out Project:",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
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

class editnoeform(noeform):
    def __init__(self, *args, **kwargs):
        super(editnoeform, self).__init__(*args, **kwargs)
        self.fields['geom'].required = False
        self.fields['doc_conemail'].required = False
    doc_latitude = forms.CharField(label="Document Latitude:",required=False,widget=forms.TextInput(attrs={'size':'30'}))
    doc_longitude = forms.CharField(label="Document Longitude:",required=False,widget=forms.TextInput(attrs={'size':'30'}))
    doc_clerknotes = forms.CharField(label="Additional Notes:",required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'4'}))

class nopform(basedocumentform):
    doc_parcelno = forms.CharField(label='Parcel No.:',required=False,max_length=96,widget=forms.TextInput(attrs={'size':'96'}))
    doc_xstreets = forms.CharField(label='Cross Streets:',required=False,max_length=96,widget=forms.TextInput(attrs={'size':'96'}))
    doc_township = forms.CharField(label='Township:',required=False,max_length=6,widget=forms.TextInput(attrs={'size':'6'}))
    doc_range = forms.CharField(label='Range:',required=False,max_length=6,widget=forms.TextInput(attrs={'size':'6'}))
    doc_section = forms.CharField(label='Section:',required=False,max_length=6,widget=forms.TextInput(attrs={'size':'6'}))
    doc_base = forms.CharField(label='Base:',required=False,max_length=8,widget=forms.TextInput(attrs={'size':'8'}))
    doc_highways = forms.CharField(label="State Hwy #:",required=False,max_length=32,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
    doc_airports = forms.CharField(label="Airports:",required=False,max_length=32,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
    doc_railways = forms.CharField(label="Railways:",required=False,max_length=32,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
    doc_waterways = forms.CharField(label="Waterways:",required=False,max_length=96,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
    doc_landuse = forms.CharField(required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
    doc_schools = forms.CharField(label="Schools:",required=False,max_length=64,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
    actions = forms.ModelMultipleChoiceField(required=False,queryset=keywords.objects.filter(keyw_keyl_fk__keyl_pk=1001).order_by('keyw_longname'),widget=forms.CheckboxSelectMultiple(attrs={'class':'localactiontypes'}))
    dkey_comment_actions = forms.CharField(required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    dev6001 = forms.BooleanField(label="Residential:",required=False)
    dev6001_val1 = forms.CharField(label="Units",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6001_val2 = forms.CharField(label="Acres",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6002 = forms.BooleanField(label="Office:",required=False)
    dev6002_val1 = forms.CharField(label="SqFt",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6002_val2 = forms.CharField(label="Acres",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6002_val3 = forms.CharField(label="Employees",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6003 = forms.BooleanField(label="Commercial:",required=False)
    dev6003_val1 = forms.CharField(label="SqFt",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6003_val2 = forms.CharField(label="Acres",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6003_val3 = forms.CharField(label="Employees",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6004 = forms.BooleanField(label="Industrial:",required=False)
    dev6004_val1 = forms.CharField(label="SqFt",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6004_val2 = forms.CharField(label="Acres",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev6004_val3 = forms.CharField(label="Employees",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev7001 = forms.BooleanField(label="Educational:",required=False)
    dev7001_val1 = forms.CharField(label="Type",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev8001 = forms.BooleanField(label="Recreational:",required=False)
    dev8001_val1 = forms.CharField(label="Type",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    devtrans = forms.BooleanField(label="Transportation:",required=False)
    devtrans_id = forms.ModelChoiceField(required=False,queryset=keywords.objects.filter(keyw_pk__gt=4000).filter(keyw_pk__lt=5000),empty_label=None)
    devtrans_comment = forms.CharField(label="Comment",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'32'}))
    devpower = forms.BooleanField(label="Power:",required=False)
    devpower_id = forms.ModelChoiceField(required=False,queryset=keywords.objects.filter(keyw_pk__gt=3000).filter(keyw_pk__lt=4000),empty_label=None)
    devpower_comment = forms.CharField(label="Comment",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'32'}))
    devpower_val1 = forms.CharField(label="Watts",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    devwaste = forms.BooleanField(label="Waste:",required=False)
    devwaste_id = forms.ModelChoiceField(required=False,queryset=keywords.objects.filter(keyw_pk__gt=5000).filter(keyw_pk__lt=6000),empty_label=None)
    devwaste_comment = forms.CharField(label="Comment",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'32'}))
    dev9001 = forms.BooleanField(label="Water Facilities:",required=False)
    dev9001_val1 = forms.CharField(label="Type",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev9001_val2 = forms.CharField(label="MGD",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev10001 = forms.BooleanField(label="Mining:",required=False)
    dev10001_val1 = forms.CharField(label="Mineral",required=False,max_length=16,widget=forms.TextInput(attrs={'size':'8'}))
    dev11001 = forms.BooleanField(label="Other:",required=False)
    dkey_comment_dev = forms.CharField(label="Other",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'8'}))
    issues = forms.ModelMultipleChoiceField(required=False,queryset=keywords.objects.filter(keyw_keyl_fk__keyl_pk=1002).order_by('keyw_longname'),widget=forms.CheckboxSelectMultiple(attrs={'class':'iss'}))
    dkey_comment_issues = forms.CharField(required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    doc_dept = forms.DateField(label="Start of Review:",required=False,input_formats=['%Y-%m-%d'],widget=forms.TextInput(attrs={'class':'date-pick'}))
    doc_clear = forms.DateField(label="End of Review:",required=False,input_formats=['%Y-%m-%d'],widget=forms.TextInput(attrs={'class':'date-pick'}))
    #ragencies = forms.ModelMultipleChoiceField(label="Reviewing Agencies:",required=False,queryset=reviewingagencies.objects.filter(inlookup=True).order_by('rag_title'),widget=FilteredSelectMultiple("Reviewing Agencies",True,attrs={'rows':'10'}))
    ragencies = forms.ModelMultipleChoiceField(label="Reviewing Agencies:",required=False,queryset=reviewingagencies.objects.filter(inlookup=True).order_by('rag_title'),widget=forms.CheckboxSelectMultiple(attrs={'class':'agencies'}))

    def clean(self):
        cleaned_data = super(nopform, self).clean()

        msg_actions = u"Other Type Required."
        msg_dev = u"Other Type Required."
        msg_issues = u"Other Issue Required."

        for a in cleaned_data.get('actions'):
            if a.keyw_pk == 1018:
                if cleaned_data.get('dkey_comment_actions') == '':
                    self._errors['dkey_comment_actions'] = self.error_class([msg_actions])
                    del cleaned_data['dkey_comment_actions']

        if cleaned_data.get('dev11001'):
            if cleaned_data.get('dkey_comment_dev') == '':
                self._errors['dkey_comment_dev'] = self.error_class([msg_dev])
                del cleaned_data['dkey_comment_dev']

        for i in cleaned_data.get('issues'):
            if i.keyw_pk == 2034:
                if cleaned_data.get('dkey_comment_issues') == '':
                    self._errors['dkey_comment_issues'] = self.error_class([msg_issues])
                    del cleaned_data['dkey_comment_issues']

        return cleaned_data

class editnopform(nopform):
    def __init__(self, *args, **kwargs):
        super(editnopform, self).__init__(*args, **kwargs)
        self.fields['geom'].required = False
        self.fields['doc_conemail'].required = False
    doc_latitude = forms.CharField(label="Document Latitude:",required=False,widget=forms.TextInput(attrs={'size':'30'}))
    doc_longitude = forms.CharField(label="Document Longitude:",required=False,widget=forms.TextInput(attrs={'size':'30'}))
    doc_clerknotes = forms.CharField(label="Additional Notes:",required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'4'}))

class nocform(nopform):
    doctypeid = forms.ModelChoiceField(required=True,queryset=doctypes.objects.filter(inlookup=True).filter(storfed__gt=0).order_by('ordinal'),empty_label=None,widget=forms.RadioSelect())

class editnocform(editnopform):
    doctypeid = forms.ModelChoiceField(required=True,queryset=doctypes.objects.filter(inlookup=True).filter(storfed__gt=0).order_by('ordinal'),empty_label=None,widget=forms.RadioSelect())

class attachmentsform(forms.Form):
    datt_file = forms.FileField(label='Select file to attach:',required=False,help_text='max. 42 megabytes')

class addleadagencyform(forms.Form):
    lag_name = forms.CharField(label="Name:",required=True,max_length=90,widget=forms.TextInput(attrs={'size':'90'}))
    lag_title = forms.CharField(label="Title:",required=True,max_length=90,widget=forms.TextInput(attrs={'size':'90'}))
    lag_address1 = forms.CharField(label="Street Address1:",required=True,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    lag_address2 = forms.CharField(label="Street Address2:",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    lag_county = forms.ModelChoiceField(label="County:",required=True,queryset=geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).order_by('geow_shortname'),empty_label="[Select County]")
    lag_city = forms.ModelChoiceField(label="City:",required=True,queryset=geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).order_by('geow_shortname'),empty_label="[Select City]")
    lag_state = USStateField(label="State:",required=True)
    lag_zip = USZipCodeField(label="Zip:",required=True)
    lag_phone = USPhoneNumberField(label="Phone:",required=True)
    lag_fax = USPhoneNumberField(label="FAX:",required=False)

class addreviewingagencyform(forms.Form):
    rag_name = forms.CharField(label="Name:",required=True,max_length=90,widget=forms.TextInput(attrs={'size':'90'}))
    rag_title = forms.CharField(label="Title:",required=True,max_length=90,widget=forms.TextInput(attrs={'size':'90'}))
    rag_address1 = forms.CharField(label="Street Address1:",required=True,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    rag_address2 = forms.CharField(label="Street Address2:",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    rag_county = forms.ModelChoiceField(label="County:",required=True,queryset=geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).order_by('geow_shortname'),empty_label="[Select County]")
    rag_city = forms.ModelChoiceField(label="City:",required=True,queryset=geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).order_by('geow_shortname'),empty_label="[Select City]")
    rag_state = USStateField(label="State:",required=True)
    rag_zip = USZipCodeField(label="Zip:",required=True)
    rag_phone = USPhoneNumberField(label="Phone:",required=True)

class addholidayform(forms.Form):
    hday_name = forms.CharField(label="Holiday Name:",required=True,max_length=40,widget=forms.TextInput(attrs={'size':'40'}))
    hday_date = forms.DateField(label="Holiday Date:",required=True,input_formats=['%Y-%m-%d'],widget=forms.TextInput(attrs={'class':'date-pick'}))
    hday_note = forms.CharField(label="Holiday Note:",required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))

    def clean(self):
        cleaned_data = super(addholidayform, self).clean()

        msg_date_weekend = u"Date is on weekend."
        msg_date_holiday = u"Date is on holiday."

        if cleaned_data.get('hday_date').weekday() in [5,6]:
            self._errors['hday_date'] = self.error_class([msg_date_weekend])
            del cleaned_data['hday_date']

        return cleaned_data

class manageusersform(forms.Form):
    userfilter = forms.CharField(label="Filter User Names:",required=False,max_length=40,widget=forms.TextInput(attrs={'size':'40'}))
    #sortfld = forms.ChoiceField(label="Sort Results By:",required=True,choices=DOC_SORT_FIELDS,initial='-doc_prj_fk__prj_schno')

class manageuserform(forms.Form):
    usr_grp = forms.ModelChoiceField(label="Assign Group:",required=False,queryset=Group.objects.filter(pk__gt=1).filter(pk__lt=5),empty_label="None",widget=forms.RadioSelect(attrs={'id':'usr_grp','class':'usr_grp'}))
    set_lag_fk = forms.ModelChoiceField(label="Lead Agency:",required=False,queryset=leadagencies.objects.filter(inlookup=True).order_by('lag_name'))
    set_rag_fk = forms.ModelChoiceField(label="Reviewing Agency:",required=False,queryset=reviewingagencies.objects.filter(inlookup=True).order_by('rag_name'))

class pendingdetailnocform(nocform):
    def __init__(self, *args, **kwargs):
        super(pendingdetailnocform, self).__init__(*args, **kwargs)
        self.fields['doc_dept'].required = True
        self.fields['doc_clear'].required = True
    doc_plannerregion = forms.ChoiceField(label="Assign Region:",required=True,choices=PLANNERREGION_CHOICES)
    doc_clerknotes = forms.CharField(label="Additional Notes:",required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'4'}))
    rejectreason = forms.CharField(label="Rejection Reason:",required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
    doc_bia = forms.BooleanField(label="BIA - Bureau of Land Trust (YYYY-XXX)",required=False)

    def clean(self):
        cleaned_data = super(pendingdetailnocform, self).clean()

        msg_date_weekend = u"Date is on weekend."
        msg_date_holiday = u"Date is on holiday."

        if cleaned_data.get('doc_dept') != None:
            if cleaned_data.get('doc_dept').weekday() in [5,6]:
                self._errors['doc_dept'] = self.error_class([msg_date_weekend])
                del cleaned_data['doc_dept']

        if cleaned_data.get('doc_clear') != None:
            if cleaned_data.get('doc_clear').weekday() in [5,6]:
                self._errors['doc_clear'] = self.error_class([msg_date_weekend])
                del cleaned_data['doc_clear']

        allhdays = holidays.objects.all()

        for hday in allhdays:
            if cleaned_data.get('doc_dept') != None:
                if cleaned_data.get('doc_dept') == hday.hday_date:
                    self._errors['doc_dept'] = self.error_class([msg_date_holiday])
                    del cleaned_data['doc_dept']        
            if cleaned_data.get('doc_clear') != None:
                if cleaned_data.get('doc_clear') == hday.hday_date:
                    self._errors['doc_clear'] = self.error_class([msg_date_holiday])
                    del cleaned_data['doc_clear']        

        return cleaned_data

class pendingdetailnodform(nodform):
    doc_clerknotes = forms.CharField(label="Additional Notes:",required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'4'}))
    rejectreason = forms.CharField(label="Rejection Reason:",required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))

class pendingdetailnoeform(noeform):
    doc_clerknotes = forms.CharField(label="Additional Notes:",required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'4'}))
    rejectreason = forms.CharField(label="Rejection Reason:",required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))

class pendingdetailnopform(nopform):
    def __init__(self, *args, **kwargs):
        super(pendingdetailnopform, self).__init__(*args, **kwargs)
        self.fields['doc_dept'].required = True
        self.fields['doc_clear'].required = True
    doc_plannerregion = forms.ChoiceField(label="Assign Region:",required=True,choices=PLANNERREGION_CHOICES)
    doc_clerknotes = forms.CharField(label="Additional Notes:",required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'4'}))
    rejectreason = forms.CharField(label="Rejection Reason:",required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))
    doc_bia = forms.BooleanField(label="BIA - Bureau of Land Trust (YYYY-XXX)",required=False)

    def clean(self):
        cleaned_data = super(pendingdetailnopform, self).clean()

        msg_date_weekend = u"Date is on weekend."
        msg_date_holiday = u"Date is on holiday."

        if cleaned_data.get('doc_dept') != None:
            if cleaned_data.get('doc_dept').weekday() in [5,6]:
                self._errors['doc_dept'] = self.error_class([msg_date_weekend])
                del cleaned_data['doc_dept']

        if cleaned_data.get('doc_clear') != None:
            if cleaned_data.get('doc_clear').weekday() in [5,6]:
                self._errors['doc_clear'] = self.error_class([msg_date_weekend])
                del cleaned_data['doc_clear']

        allhdays = holidays.objects.all()

        for hday in allhdays:
            if cleaned_data.get('doc_dept') != None:
                if cleaned_data.get('doc_dept') == hday.hday_date:
                    self._errors['doc_dept'] = self.error_class([msg_date_holiday])
                    del cleaned_data['doc_dept']        
            if cleaned_data.get('doc_clear') != None:
                if cleaned_data.get('doc_clear') == hday.hday_date:
                    self._errors['doc_clear'] = self.error_class([msg_date_holiday])
                    del cleaned_data['doc_clear']        

        return cleaned_data

class reviewdetailnocform(nocform):
    doc_clerknotes = forms.CharField(label="Additional Notes:",required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'4'}))
    rejectreason = forms.CharField(label="Rejection Reason:",required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))

class reviewdetailnopform(nopform):
    doc_clerknotes = forms.CharField(label="Additional Notes:",required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'4'}))
    rejectreason = forms.CharField(label="Rejection Reason:",required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))

class commentaddform(forms.Form):
    commenttype = forms.ChoiceField(required=True,choices=COMMENT_CHOICES,initial='text',widget=forms.RadioSelect(attrs={'id':'commenttype','class':'commenttype'}))
    dcom_textcomment = forms.CharField(label="Text Comment:",required=False,widget=forms.Textarea(attrs={'cols':'100','rows':'20'}))
    dcom_filecomment = forms.FileField(label='Select a PDF File:',required=False,help_text='max. 42 megabytes')

class manageaccountform(forms.Form):
    confirstname = forms.CharField(label="First Name:",required=False,max_length=32,widget=forms.TextInput(attrs={'size':'32'}))
    conlastname = forms.CharField(label="Last Name:",required=False,max_length=32,widget=forms.TextInput(attrs={'size':'32'}))
    conemail = forms.EmailField(label="E-mail:",required=False,max_length=64,widget=forms.TextInput(attrs={'size':'64'}))
    conphone = USPhoneNumberField(label="Phone Number:",required=False)

class requestupgrdform(forms.Form):
    rqst_type = forms.ChoiceField(label="Request Type:",required=True,choices=UPGRADE_CHOICES,initial='lead',widget=forms.RadioSelect(attrs={'id':'rqst_type'}))
    rqst_lag_fk = forms.ModelChoiceField(label="Lead Agency:",required=False,queryset=leadagencies.objects.filter(inlookup=True).order_by('lag_name'))
    rqst_rag_fk = forms.ModelChoiceField(label="Reviewing Agency:",required=False,queryset=reviewingagencies.objects.filter(inlookup=True).order_by('rag_name'))
    rqst_reason = forms.CharField(label="Reason for Request:",required=True,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))

class manageupgradeform(forms.Form):
    allowupgrade = forms.ChoiceField(label="Allow Upgrade?:",required=True,choices=PROJECT_EXISTS,initial='no',widget=forms.RadioSelect(attrs={'id':'allowupgrade'}))
    rejectreason = forms.CharField(label="Rejection Reason:",required=False,widget=forms.Textarea(attrs={'cols':'75','rows':'2'}))

class usersettingsform(forms.Form):
    set_lag_fk = forms.ModelChoiceField(label="Lead Agency:",required=False,queryset=leadagencies.objects.filter(inlookup=True).order_by('lag_name'))
    set_rag_fk = forms.ModelChoiceField(label="Reviewing Agency:",required=False,queryset=reviewingagencies.objects.filter(inlookup=True).order_by('rag_name'))

class chqueryform(forms.Form):
    prj_schno = forms.CharField(label="Clearinghouse Number:",max_length=12)
    leadorresp = forms.ChoiceField(required=False,choices=NODAGENCY_CHOICES,initial='lead',widget=forms.RadioSelect(attrs={'id':'lorr','class':'lorr'}))
    nodagency = forms.ModelChoiceField(required=False,queryset=leadagencies.objects.filter(inlookup=True).order_by('lag_name'),empty_label="[Select Agency]",widget=forms.Select(attrs={'id':'nodagency','class':'nodagency'}))
    doctype = forms.CharField(required=True,max_length=10,widget=forms.HiddenInput())

    # def clean(self):
    #     cleaned_data = super(chqueryform, self).clean()

    #     msg_leadorresp = u"You must choose Lead Agency or Responsible Agency radio buttons."
    #     msg_nodagency = u"You must choose a Lead Agency from the list."

    #     if cleaned_data.get('doctype') == '108':
    #         if cleaned_data.get('leadorresp') == None:
    #             self._errors['leadorresp'] = self.error_class([msg_leadorresp])
    #             del cleaned_data['leadorresp']

    #         if cleaned_data.get('nodagency') == None:
    #             self._errors['nodagency'] = self.error_class([msg_nodagency])
    #             del cleaned_data['nodagency']

    #     return cleaned_data

class findprojectform(forms.Form):
    pass
    
class geocode(forms.Form):
    address = forms.CharField(label="",max_length=254, widget=forms.TextInput(attrs={'onkeydown':"if (event.keyCode == 13) doBasicSearchClick()"}))
    
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
 
    

