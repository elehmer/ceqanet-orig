from django.template import RequestContext, Context, loader
from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import FormView,UpdateView
from django.core.urlresolvers import reverse_lazy, reverse
from django.core.mail import send_mail
from ceqanet.forms import QueryForm,SubmitForm,AddPrjForm,AddDocForm,InputForm,nocform,nodform,noeform,nopform,NOEeditForm,DocReviewForm,usersettingsform,reviewdetailform
from ceqanet.models import projects,documents,geowords,leadagencies,reviewingagencies,doctypes,dockeywords,docreviews,latlongs,counties,UserProfile,clearinghouse,keywords
from datetime import datetime

# Create your views here.
def index(request):
	t = loader.get_template("ceqanet/index.html")
	c = RequestContext(request,{})
	return HttpResponse(t.render(c))

class query(FormView):
    template_name="ceqanet/query.html"
    form_class = QueryForm
    success_url = '/projectlist/'

    def get_context_data(self, **kwargs):
        context = super(query, self).get_context_data(**kwargs)
        context['citylist'] = geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).order_by('geow_shortname')
        context['countylist'] = geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).order_by('geow_shortname')
        context['laglist'] = leadagencies.objects.filter(inlookup=True).order_by('lag_name')
        context['raglist'] = reviewingagencies.objects.filter(inlookup=True).order_by('rag_name')
        context['doctypes'] = doctypes.objects.filter(inlookup=True).order_by('keyw_longname')
        return context

class submit(FormView):
    template_name="ceqanet/submit.html"
    form_class = SubmitForm

    def get_success_url(self):
        lag_pk = self.request.POST.get('lag_pk')
        doctype = self.request.POST.get('doctype')
        prjtoggle = self.request.POST.get('prjtoggle')

        if prjtoggle == "yes":
            success_url = "%s?prj_schno=&lag_pk=%s&doctype=%s" % (reverse_lazy('findproject'),lag_pk,doctype)
        elif prjtoggle == "no":
            success_url = "%s?prj_pk=-9999&lag_pk=%s&doctype=%s" % (reverse_lazy('adddocument'),lag_pk,doctype)
        return success_url

    def get_context_data(self, **kwargs):
        context = super(submit, self).get_context_data(**kwargs)
        context['laglist'] = leadagencies.objects.filter(inlookup=True).order_by('lag_name')
        return context

class findproject(ListView):
    template_name="ceqanet/findproject.html"
    context_object_name = "schnos"
    paginate_by = 25

    def get_queryset(self):
        queryset = ""
        if "prj_schno" in self.request.GET:
            if self.request.GET.get('prj_schno') != '':
                queryset = ClearinghouseQuery(self.request)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(findproject, self).get_context_data(**kwargs)

        qsminuspage = self.request.GET.copy()
        
        if "page" in qsminuspage:
            qsminuspage.pop('page')
        if "whichpk" in qsminuspage:
            qsminuspage.pop('whichpk')

        context['prj_schno'] = self.request.GET.get('prj_schno')
        context['lag_pk'] = self.request.GET.get('lag_pk')
        context['doctype'] = self.request.GET.get('doctype')
        context['restofqs'] = qsminuspage.urlencode()

        return context

def ClearinghouseQuery(request):
    prj_schno = request.GET.get('prj_schno')

    queryset = projects.objects.filter(prj_visible=True).filter(prj_schno__startswith=prj_schno).order_by('-prj_schno')
    return queryset


class addproject(FormView):
    template_name="ceqanet/addproject.html"
    form_class = AddPrjForm

class adddocument(FormView):
    template_name="ceqanet/adddocument.html"
    form_class = AddDocForm

    def get_success_url(self):
        success_url = "%s" % (reverse_lazy('accept'))
        return success_url

    def get_context_data(self, **kwargs):
        context = super(adddocument, self).get_context_data(**kwargs)

        context['prj_pk'] = self.request.GET.get("prj_pk")
        context['lag_pk'] = self.request.GET.get("lag_pk")
        context['doctype'] = self.request.GET.get("doctype")
        if self.request.GET.get('doctype') in ['NOC','NOP']:
            context['actions'] = keywords.objects.filter(keyw_keyl_fk__keyl_pk=1001).order_by('keyw_longname')
            #context['devtypes'] = keywords.objects.filter(keyw_keyl_fk__keyl_pk=1010).order_by('keyw_longname')
            #context['issues'] = keywords.objects.filter(keyw_keyl_fk__keyl_pk=1002).order_by('keyw_longname')
        if self.request.GET.get("prj_pk") != '-9999':
            context['prjinfo'] = projects.objects.get(prj_pk__exact=self.request.GET.get("prj_pk"))
        context['laglist'] = leadagencies.objects.get(lag_pk__exact=self.request.GET.get('lag_pk'))

        return context
    
    def get_initial(self):
        initial = super(adddocument, self).get_initial()

        la_query = leadagencies.objects.get(lag_pk__exact=self.request.GET.get('lag_pk'))
        initial['doc_conaddress1'] = la_query.lag_address1.strip
        initial['doc_conaddress2'] = la_query.lag_address2.strip
        initial['doc_concity'] = la_query.lag_city.strip
        initial['doc_constate'] = la_query.lag_state.strip
        initial['doc_conzip'] = la_query.lag_zip.strip
        return initial

    def form_valid(self,form):
        data = form.cleaned_data
        today = datetime.now()
        doc_received = today
        lag = leadagencies.objects.get(pk=self.request.POST.get('lag_pk'))
        doc = documents.objects.get(pk=0)
        cnty = counties.objects.get(pk=data['doc_county'].pk)
        doct = doctypes.objects.get(keyw_shortname__startswith=self.request.POST.get('doctype'))
        if data['doc_conaddress2'] == '':
            doc_conaddress2 = None
        else:
            doc_conaddress2 = data['doc_conaddress2']
        doc_conphone = data['strphone1']+data['strphone2']+data['strphone3']
        if self.request.POST.get('doctype') in ['NOC','NOP']:
            if data['doc_parcelno'] == '':
                doc_parcelno = None
            else:
                doc_parcelno = data['doc_parcelno']
            if data['doc_xstreets'] == '':
                doc_xstreets = None
            else:
                doc_xstreets = data['doc_xstreets']
            if data['doc_township'] == '':
                doc_township = None
            else:
                doc_township = data['doc_township']
            if data['doc_range'] == '':
                doc_range = None
            else:
                doc_range = data['doc_range']
            if data['doc_section'] == '':
                doc_section = None
            else:
                doc_section = data['doc_section']
            if data['doc_base'] == '':
                doc_base = None
            else:
                doc_base = data['doc_base']
            if data['doc_highways'] == '':
                doc_highways = None
            else:
                doc_highways = data['doc_highways']
            if data['doc_airports'] == '':
                doc_airports = None
            else:
                doc_airports = data['doc_airports']
            if data['doc_railways'] == '':
                doc_railways = None
            else:
                doc_railways = data['doc_railways']
            if data['doc_waterways'] == '':
                doc_waterways = None
            else:
                doc_waterways = data['doc_waterways']
            if data['doc_landuse'] == '':
                doc_landuse = None
            else:
                doc_landuse = data['doc_landuse']
            if data['doc_schools'] == '':
                doc_schools = None
            else:
                doc_schools = data['doc_schools']

        if self.request.POST.get('doctype') == 'NOE':
            doc_exministerial = False
            doc_exdeclared = False
            doc_exemergency = False
            doc_excategorical = False
            doc_exstatutory = False
            doc_exnumber = ""
            status = ""
            rdoexemptstatus = self.request.POST.get('rdoexemptstatus')
            if rdoexemptstatus == '1':
                doc_exministerial = True
                status = "Ministerial"
            elif rdoexemptstatus == '2':
                doc_exdeclared = True
                status = "Declared Emergency"
            elif rdoexemptstatus == '3':
                doc_exemergency = True
                status = "Emergency Project"
            elif rdoexemptstatus == '4':
                doc_excategorical = True
                doc_exnumber = self.request.POST.get('strsectionnumber')
                status = "Categorical Exemption, Section " + doc_exnumber
            elif rdoexemptstatus == '5':
                doc_exstatutory = True
                doc_exnumber = self.request.POST.get('strcodenumber')
                status = "Statutory Exemptions, State Code " + doc_exnumber

        if self.request.POST.get('prj_pk') == '-9999':
            prj = projects(prj_lag_fk=lag,prj_doc_fk=doc,prj_title=data['prj_title'],prj_description=data['prj_description'],prj_leadagency=lag.lag_name,prj_datefirst=today,prj_datelast=today)
            prj.save()
        else:
            prj = projects.objects.get(pk=self.request.POST.get('prj_pk'))

        if self.request.POST.get('doctype') in ['NOC','NOP']:
            adddoc = documents(doc_prj_fk=prj,doc_cnty_fk=cnty,doc_doct_fk=doct,doc_doctype=self.request.POST.get('doctype'),doc_docname=doct.keyw_longname,doc_conname=data['doc_conname'],doc_conemail=data['doc_conemail'],doc_conphone=doc_conphone,doc_conaddress1=data['doc_conaddress1'],doc_conaddress2=data['doc_conaddress2'],doc_concity=data['doc_concity'],doc_constate=data['doc_constate'],doc_conzip=data['doc_conzip'],doc_location=data['doc_location'],doc_city=data['doc_city'].geow_shortname,doc_county=data['doc_county'].geow_shortname,doc_pending=1,doc_received=doc_received,doc_parcelno=doc_parcelno,doc_xstreets=doc_xstreets,doc_township=doc_township,doc_range=doc_range,doc_section=doc_section,doc_base=doc_base)
            adddoc.save()
            actions = keywords.objects.filter(keyw_keyl_fk__keyl_pk=1001)
            for a in actions:
                if self.request.POST.get('lat'+str(a.keyw_pk)) == "1":
                    adockeyw = dockeywords(dkey_doc_fk=adddoc,dkey_keyw_fk=a,dkey_rank=0)
                    adockeyw.save()
            devtypes = keywords.objects.filter(keyw_keyl_fk__keyl_pk=1010)
            for d in devtypes:
                if self.request.POST.get('dev'+str(d.keyw_pk)) == "1":
                    ddockeyw = dockeywords(dkey_doc_fk=adddoc,dkey_keyw_fk=d,dkey_value1=self.request.POST.get('dev'+str(d.keyw_pk)+'_val1'),dkey_value2=self.request.POST.get('dev'+str(d.keyw_pk)+'_val2'),dkey_value3=self.request.POST.get('dev'+str(d.keyw_pk)+'_val3'),dkey_rank=0)
                    ddockeyw.save()
            issues = keywords.objects.filter(keyw_keyl_fk__keyl_pk=1002)
            for i in issues:
                if self.request.POST.get('issue'+str(i.keyw_pk)) == "1":
                    idockeyw = dockeywords(dkey_doc_fk=adddoc,dkey_keyw_fk=i,dkey_rank=0)
                    idockeyw.save()
            for ra in data['ragencies']:
                docrev = docreviews(drag_doc_fk=adddoc,drag_rag_fk=ra,drag_rank=0,drag_copies=1)
                docrev.save()

        if self.request.POST.get('doctype') == 'NOE':
            adddoc = documents(doc_prj_fk=prj,doc_cnty_fk=cnty,doc_doct_fk=doct,doc_doctype=self.request.POST.get('doctype'),doc_docname=doct.keyw_longname,doc_conname=data['doc_conname'],doc_conemail=data['doc_conemail'],doc_conphone=doc_conphone,doc_conaddress1=data['doc_conaddress1'],doc_conaddress2=data['doc_conaddress2'],doc_concity=data['doc_concity'],doc_constate=data['doc_constate'],doc_conzip=data['doc_conzip'],doc_location=data['doc_location'],doc_city=data['doc_city'].geow_shortname,doc_county=data['doc_county'].geow_shortname,doc_pending=1,doc_received=doc_received,doc_exministerial=doc_exministerial,doc_exdeclared=doc_exdeclared,doc_exemergency=doc_exemergency,doc_excategorical=doc_excategorical,doc_exstatutory=doc_exstatutory,doc_exnumber=doc_exnumber)
            adddoc.save()
        prj.prj_doc_fk=adddoc
        prj.save()

        strFrom = "ceqanet@opr.ca.gov"
        ToList = [data['doc_conemail']]
        strSubject = "Confirmation of Submittal - " + doct.keyw_longname
        strBody = "This confirms receipt of your electronic " + doct.keyw_longname + " form submission on " + doc_received.strftime('%m/%d/%Y') + ".  \n \n"
        strBody = strBody + "The State Clearinghouse will review your submittal and provide a State Clearinghouse Number and filing date within one business day. \n \n"
        strBody = strBody + "If you have questions about the form submittal process, please reply to this email.  Thank you for using CEQAnet. \n"
        strBody = strBody + "\n \n" + "--- Information Submitted ---" + "\n"
        strBody = strBody + "Document Type: " + self.request.POST.get('doctype') + "\n"        
        if self.request.POST.get('prj_pk') == '-9999':
            strBody = strBody + "Project Title: " + data['prj_title'] + "\n"
        else:
            strBody = strBody + "Project Title: " + prj.prj_title + "\n"            
        strBody = strBody + "Project Location: " + data['doc_location'] + "\n"
        strBody = strBody + "    City: " + data['doc_city'].geow_shortname + "\n"
        strBody = strBody + "    County: " + data['doc_county'].geow_shortname + "\n"
        strBody = strBody + "    Latitude: " + data['doc_latitude'] + "\n"
        strBody = strBody + "    Longitude: " + data['doc_longitude'] + "\n"
        if self.request.POST.get('prj_pk') == '-9999':
            strBody = strBody + "Project Description: " + data['prj_description'] + "\n"
        else:
            strBody = strBody + "Project Description: " + prj.prj_description + "\n"
        #strBody = strBody + "Person or Agency Carrying out Project: " & prj_otheragency + "\n"
        strBody = strBody + "Agency Approving Project: " + lag.lag_name + "\n"
        strBody = strBody + "Primary Contact:  " + "\n"
        strBody = strBody + "    Name: " + data['doc_conname'] + "\n"
        strBody = strBody + "    Phone: " + doc_conphone + "\n"
        strBody = strBody + "    E-mail: " + data['doc_conemail'] + "\n"
        if self.request.POST.get('doctype') == 'NOE':
            strBody = strBody + "Exempt Status: " + status + "\n"
            strBody = strBody + "Reason for Exemption: " + data['txtreason'] + "\n"
        strBody = strBody + "DATE: " + doc_received.strftime('%m/%d/%Y') + "\n"

        #send_mail(strSubject,strBody,strFrom,ToList,fail_silently=False)

        return super(adddocument,self).form_valid(form)

def ProjectInfoQuery(request):
    prj_pk = request.GET.get('prj_pk')

    queryset = projects.objects.get(prj_pk=prj_pk)
    return queryset

class docadd_noc(FormView):
    model = projects
    template_name="ceqanet/docadd_noc.html"
    form_class = nocform

    def get_success_url(self):
        success_url = "%s" % (reverse_lazy('submit'))
        return success_url

    def get_context_data(self, **kwargs):
        context = super(docadd_noc, self).get_context_data(**kwargs)
        context['lag_pk'] = self.request.GET.get('lag_pk')
        return context

    def form_valid(self,form):
        data = form.cleaned_data
        lag = leadagencies.objects.get(pk=self.request.POST.get('lag_pk'))
        doc = documents.objects.get(pk=0)
        addproject = projects(prj_title=data['prj_title'],prj_lag_fk=lag,prj_doc_fk=doc)
        addproject.save()
        return super(docadd_noc,self).form_valid(form)

class docadd_nod(FormView):
    template_name="ceqanet/docadd_nod.html"
    form_class = nodform

class docadd_noe(FormView):
    template_name="ceqanet/docadd_noe.html"
    form_class = noeform

    def get_initial(self):
        initial = super(docadd_noe, self).get_initial()

        la_query = leadagencies.objects.get(lag_pk__exact=self.request.GET.get('lag_pk'))
        initial['doc_lagaddress1'] = la_query.lag_address1
        initial['doc_lagaddress2'] = la_query.lag_address2
        initial['doc_lagcity'] = la_query.lag_city
        initial['doc_lagstate'] = la_query.lag_state
        initial['doc_lagzip'] = la_query.lag_zip
        return initial

    def get_success_url(self):
        success_url = "%s" % (reverse_lazy('submit'))
        return success_url

    def get_context_data(self, **kwargs):
        context = super(docadd_noe, self).get_context_data(**kwargs)
        context['lag_pk'] = self.request.GET.get('lag_pk')
        context['laglist'] = leadagencies.objects.get(lag_pk__exact=self.request.GET.get('lag_pk'))
        context['citylist'] = geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).order_by('geow_shortname')
        context['countylist'] = geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).order_by('geow_shortname')
        return context

    #def clean_prj_schno(self):
    #    prj_schno = self.cleaned_data['prj_schno']
    #    prjtoggle = self.cleaned_data['prjtoggle']

    #    if prjtoggle == "yes":
    #        if prj_schno == '':
    #            raise forms.ValidationError("Clearing House Number Required")
            #else
                #projects.objects.filter(prj_schno__startswith=prj_schno)
    #    else:
    #        prj_schno = "-99999"

    #    return prj_schno


    #def clean(self):
    #    cleaned_data = super(docadd_noe,self).clean()
    #    prjtoggle = cleaned_data.get("prjtoggle")

    #    if prjtoggle == "yes":
    #        pass
    #    else

    def form_valid(self,form):
        data = form.cleaned_data
        lag = leadagencies.objects.get(pk=self.request.POST.get('lag_pk'))
        doc = documents.objects.get(pk=0)
        addproject = projects(prj_title=data['prj_title'],prj_lag_fk=lag,prj_doc_fk=doc)
        addproject.save()
        return super(docadd_noc,self).form_valid(form)

class docadd_nop(FormView):
    template_name="ceqanet/docadd_nop.html"
    form_class = nopform

class inputform(FormView):
    template_name="ceqanet/inputform.html"
    form_class = InputForm
    success_url = "/docaccept/"

    def get_initial(self):
        initial = super(inputform, self).get_initial()

        la_query = leadagencies.objects.get(lag_pk__exact=self.request.GET.get('lag_pk'))
        initial['doc_lagaddress1'] = la_query.lag_address1
        initial['doc_lagaddress2'] = la_query.lag_address2
        initial['doc_lagcity'] = la_query.lag_city
        initial['doc_lagstate'] = la_query.lag_state
        initial['doc_lagzip'] = la_query.lag_zip
        return initial

    def get_context_data(self, **kwargs):
        context = super(inputform, self).get_context_data(**kwargs)
        context['doctype'] = self.request.GET.get('doctype')
        context['laglist'] = leadagencies.objects.get(lag_pk__exact=self.request.GET.get('lag_pk'))
        context['citylist'] = geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).order_by('geow_shortname')
        context['countylist'] = geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).order_by('geow_shortname')
        return context

    def form_valid(self,form):
        data = self.cleaned_data
        docs = counties(geow_shortname=data['doc_lagaddress1'],geow_longname=data['doc_lagaddress1'])
        docs.save()
        return super(inputform,self).form_valid(form)


class projectlist(ListView):
    template_name="ceqanet/projectlist.html"
    context_object_name = "docs"
    paginate_by = 25

    def get_queryset(self):
        queryset = ProjectListQuery(self.request)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(projectlist, self).get_context_data(**kwargs)

        qsminuspage = self.request.GET.copy()
        
        if "page" in qsminuspage:
            qsminuspage.pop('page')

        context['restofqs'] = qsminuspage.urlencode()

        mode = self.request.GET.get('mode')

        if mode == "A":
          prj_schno = self.request.GET.get('prj_schno')
        elif mode == "B":
          rdodate = self.request.GET.get('rdodate')
          date_from = self.request.GET.get('date_from')
          date_to = self.request.GET.get('date_to')
          rdoplace = self.request.GET.get('rdoplace')
          cityid = self.request.GET.get('cityid')
          cid = self.request.GET.get('cid')
          rdokword = self.request.GET.get('rdokword')
          rdorag = self.request.GET.get('rdorag')
          rag_pk = self.request.GET.get('rag_pk')
          rdolag = self.request.GET.get('rdolag')
          lag_pk = self.request.GET.get('lag_pk')
          doctype = self.request.GET.get('doctype')

        return context

def ProjectListQuery(request):
    mode = request.GET.get('mode')

    prj_schno = request.GET.get('prj_schno')
    rdodate = request.GET.get('rdodate')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    rdoplace = request.GET.get('rdoplace')
    cityid = request.GET.get('cityid')
    cid = request.GET.get('cid')
    rdokword = request.GET.get('rdokword')
    rdorag = request.GET.get('rdorag')
    rag_pk = request.GET.get('rag_pk')
    rdolag = request.GET.get('rdolag')
    lag_pk = request.GET.get('lag_pk')
    doctype = request.GET.get('doctype')

    queryset = ""

    if mode == "A":
        queryset = documents.objects.filter(doc_visible=True).filter(doc_prj_fk__prj_schno__startswith=prj_schno).order_by('-doc_received','-doc_prj_fk__prj_schno')
    elif mode == "B":
        queryset = documents.objects.filter(doc_visible=True).order_by('-doc_received','-doc_prj_fk__prj_schno')
        if rdodate == "2":
            queryset = queryset.filter(doc_received__range=(date_from,date_to))
        if rdoplace == "2":
            queryset = queryset.filter(docgeowords__dgeo_geow_fk__geow_pk=cityid)
        elif rdoplace == "3":
            queryset = queryset.filter(docgeowords__dgeo_geow_fk__geow_pk=cid)
        if rdorag == "2":
            queryset = queryset.filter(docreviews__drag_rag_fk__rag_pk=rag_pk)
        if rdolag == "2":
            queryset = queryset.filter(projects__prj_lag_fk__lag_pk=lag_pk)
        if doctype != "1":
            queryset = queryset.filter(doc_doct_fk__keyw_pk=doctype)
    return queryset

class projdoclist(ListView):
    template_name="ceqanet/projdoclist.html"
    context_object_name = "prjdocs"

    def get_queryset(self):
        queryset = ProjDocListQuery(self.request)
        return queryset

def ProjDocListQuery(request):
    prj_pk = request.GET.get('prj_pk')

    queryset = documents.objects.filter(doc_visible=True).filter(doc_prj_fk__exact=prj_pk).order_by('-doc_received')
    return queryset

class docdescription(DetailView):
    model = documents
    template_name="ceqanet/docdescription.html"
    context_object_name = "doc"

    def get_context_data(self, **kwargs):
        context = super(docdescription, self).get_context_data(**kwargs)
        doc_pk = self.kwargs['pk']
        context['doc_pk'] = doc_pk
        doctype = self.request.GET.get("doctype")
        context['doctype'] = doctype
        if doctype == "NOE":
            context['latlongs'] = latlongs.objects.filter(doc_pk=doc_pk)
        elif doctype == "NOD":
            context['latlongs'] = latlongs.objects.filter(doc_pk=doc_pk)
        else:
            context['latlongs'] = latlongs.objects.filter(doc_pk=doc_pk)
            context['dev'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc_pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1010)
            context['actions'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc_pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1001)
            context['issues'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc_pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1002)
            context['lag'] = docreviews.objects.filter(drag_doc_fk__doc_pk=doc_pk)
        return context

class NOEedit(UpdateView):
    model = documents
    form_class = NOEeditForm
    template_name="ceqanet/NOEedit.html"

    def get_success_url(self):
        success_url = "%s?doc_pk=%s" % (reverse_lazy('NOEdescription'),self.request.POST.get('doc_pk'))
        return success_url

    def get_context_data(self, **kwargs):
        context = super(NOEedit, self).get_context_data(**kwargs)
        context['doc_pk'] = self.kwargs['pk']
        context['latlongs'] = latlongs.objects.filter(doc_pk=self.kwargs['pk'])

        return context


class docreview(ListView):
    template_name="ceqanet/docreview.html"
    context_object_name = "pendings"
    paginate_by = 25

    def get_queryset(self):
        queryset = PendingListQuery(self.request)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(docreview, self).get_context_data(**kwargs)

        doc_pk = self.request.GET.get('doc_pk')
        qsminuspage = self.request.GET.copy()
        
        if "page" in qsminuspage:
            qsminuspage.pop('page')

        context['restofqs'] = qsminuspage.urlencode()
        context['latlongs'] = latlongs.objects.filter(doc_pk=doc_pk)
        context['dev'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc_pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1010)
        context['actions'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc_pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1001)
        context['issues'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc_pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1002)
        context['lag'] = docreviews.objects.filter(drag_doc_fk__doc_pk=doc_pk)

        return context

def PendingListQuery(request):
    queryset = documents.objects.filter(doc_pending=True).order_by('-doc_received')
    return queryset

class reviewdetail(FormView):
    form_class = reviewdetailform
    template_name="ceqanet/reviewdetail.html"
    context_object_name = "detail"

#    def get_queryset(self):
#        queryset = ReviewDetailQuery(self.request)
#        return queryset
 
    def get_context_data(self, **kwargs):
        context = super(reviewdetail, self).get_context_data(**kwargs)

        doc_pk = self.request.GET.get('doc_pk')
        context['doc_pk'] = doc_pk
        context['detail'] = documents.objects.get(doc_pk__exact=self.request.GET.get('doc_pk'))
        context['latlongs'] = latlongs.objects.filter(doc_pk=doc_pk)
        context['dev'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc_pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1010)
        context['actions'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc_pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1001)
        context['issues'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc_pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1002)
        context['lag'] = docreviews.objects.filter(drag_doc_fk__doc_pk=doc_pk)

        return context

    def get_success_url(self):
        success_url = "%s" % reverse_lazy('docreview')
        return success_url

    def form_valid(self,form):
        data = form.cleaned_data

        ch = clearinghouse.objects.get(pk=1)
        currentidnum = str(ch.currentid)
        if len(currentidnum) == 1:
            currentidnum = "00"+currentidnum
        elif len(currentidnum) == 2:
            currentidnum = "0"+currentidnum
        schno = ch.schnoprefix + self.request.POST.get('region') + currentidnum
        ch.currentid = ch.currentid+1
        ch.save()

        doc = documents.objects.get(pk=self.request.POST.get('doc_pk'))
        doc.doc_dept = data['doc_dept']
        doc.doc_clear = data['doc_clear']
        doc.doc_pending = False
        doc.doc_review = True
        doc.doc_schno = schno

        prj = projects.objects.get(pk=doc.doc_prj_fk.prj_pk)

        if prj.prj_pending:
            prj.prj_pending = False
            prj.prj_schno = schno
        doc.save()
        prj.save()

        return super(reviewdetail,self).form_valid(form)

#def ReviewDetailQuery(request):
#    doc_pk = request.GET.get("doc_pk")
#    queryset = documents.objects.get(pk=doc_pk)
#    return queryset

def accept(request):
    t = loader.get_template("ceqanet/accept.html")
    c = RequestContext(request,{})
    return HttpResponse(t.render(c))

class usersettings(UpdateView):
    model = UserProfile
    form_class = usersettingsform
    template_name="ceqanet/usersettings.html"

    def get_success_url(self):
        success_url = "%s" % (reverse_lazy('index'))
        return success_url