from django.template import RequestContext, Context, loader
from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.generic.list import ListView
from django.views.generic.edit import FormView,UpdateView
from django.core.urlresolvers import reverse_lazy, reverse
from django.core.mail import send_mail
from ceqanet.forms import QueryForm,SubmitForm,AddPrjForm,AddDocForm,InputForm,nocform,nodform,noeform,nopform,NOEeditForm,DocReviewForm
from ceqanet.models import projects,documents,geowords,leadagencies,reviewingagencies,doctypes,dockeywords,docreviews,latlongs,counties
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
        if self.request.GET.get("prj_pk") != '-9999':
            context['prjinfo'] = projects.objects.get(prj_pk__exact=self.request.GET.get("prj_pk"))
        context['laglist'] = leadagencies.objects.get(lag_pk__exact=self.request.GET.get('lag_pk'))
        context['citylist'] = geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).order_by('geow_shortname')
        context['countylist'] = geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).order_by('geow_shortname')

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
        cnty = counties.objects.get(geow_shortname__exact=self.request.POST.get('doc_county'))
        doct = doctypes.objects.get(keyw_shortname__startswith=self.request.POST.get('doctype'))
        doc_conphone = data['strphone1']+data['strphone2']+data['strphone3']
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
            addprj = projects(prj_lag_fk=lag,prj_doc_fk=doc,prj_title=data['prj_title'],prj_description=data['prj_description'],prj_leadagency=lag.lag_name,prj_datefirst=today,prj_datelast=today)
            addprj.save()
            if self.request.POST.get('doctype') == 'NOE':
                adddoc = documents(doc_prj_fk=addprj,doc_cnty_fk=cnty,doc_doct_fk=doct,doc_doctype=self.request.POST.get('doctype'),doc_docname=doct.keyw_longname,doc_conname=data['doc_conname'],doc_conemail=data['doc_conemail'],doc_conphone=doc_conphone,doc_conaddress1=data['doc_conaddress1'],doc_conaddress2=data['doc_conaddress2'],doc_concity=data['doc_concity'],doc_constate=data['doc_constate'],doc_conzip=data['doc_conzip'],doc_location=data['doc_location'],doc_city=self.request.POST.get('doc_city'),doc_county=self.request.POST.get('doc_county'),doc_pending=1,doc_exministerial=doc_exministerial,doc_exdeclared=doc_exdeclared,doc_exemergency=doc_exemergency,doc_excategorical=doc_excategorical,doc_exstatutory=doc_exstatutory,doc_exnumber=doc_exnumber)
            adddoc.save()
            addprj.prj_doc_fk=adddoc
            addprj.save()
        else:
            prj = projects.objects.get(pk=self.request.POST.get('prj_pk'))
            if self.request.POST.get('doctype') == 'NOE':
                adddoc = documents(doc_prj_fk=prj,doc_cnty_fk=cnty,doc_doct_fk=doct,doc_doctype=self.request.POST.get('doctype'),doc_docname=doct.keyw_longname,doc_conname=data['doc_conname'],doc_conemail=data['doc_conemail'],doc_conphone=doc_conphone,doc_conaddress1=data['doc_conaddress1'],doc_conaddress2=data['doc_conaddress2'],doc_concity=data['doc_concity'],doc_constate=data['doc_constate'],doc_conzip=data['doc_conzip'],doc_location=data['doc_location'],doc_city=self.request.POST.get('doc_city'),doc_county=self.request.POST.get('doc_county'),doc_pending=1,doc_exministerial=doc_exministerial,doc_exdeclared=doc_exdeclared,doc_exemergency=doc_exemergency,doc_excategorical=doc_excategorical,doc_exstatutory=doc_exstatutory,doc_exnumber=doc_exnumber)
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
        strBody = strBody + "Project Title: " + data['prj_title'] + "\n"
        strBody = strBody + "Project Location: " + data['doc_location'] + "\n"
        strBody = strBody + "    City: " + self.request.POST.get('doc_city') + "\n"
        strBody = strBody + "    County: " + self.request.POST.get('doc_county') + "\n"
        strBody = strBody + "    Latitude: " + data['doc_latitude'] + "\n"
        strBody = strBody + "    Longitude: " + data['doc_longitude'] + "\n"
        strBody = strBody + "Project Description: " + data['prj_description'] + "\n"
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

        send_mail(strSubject,strBody,strFrom,ToList,fail_silently=False)

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

class NOEdescription(ListView):
    template_name="ceqanet/NOEdescription.html"
    context_object_name = "NOE"

    def get_queryset(self):
        queryset = NOEdescriptionQuery(self.request)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(NOEdescription, self).get_context_data(**kwargs)
        doc_pk = self.request.GET.get('doc_pk')
        context['doc_pk'] = doc_pk
        context['latlongs'] = latlongs.objects.filter(doc_pk=doc_pk)

        return context

def NOEdescriptionQuery(request):
    doc_pk = request.GET.get('doc_pk')

    queryset = documents.objects.get(doc_pk=doc_pk)
    return queryset

class NODdescription(ListView):
    template_name="ceqanet/NODdescription.html"
    context_object_name = "NOD"

    def get_queryset(self):
        queryset = NODdescriptionQuery(self.request)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(NODdescription, self).get_context_data(**kwargs)
        doc_pk = self.request.GET.get('doc_pk')
        context['latlongs'] = latlongs.objects.filter(doc_pk=doc_pk)

        return context

def NODdescriptionQuery(request):
    doc_pk = request.GET.get('doc_pk')

    queryset = documents.objects.get(doc_pk=doc_pk)
    return queryset

class docdescription(ListView):
    template_name="ceqanet/docdescription.html"
    context_object_name = "docs"

    def get_queryset(self):
        queryset = docdescriptionQuery(self.request)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(docdescription, self).get_context_data(**kwargs)
        doc_pk = self.request.GET.get('doc_pk')
        context['latlongs'] = latlongs.objects.filter(doc_pk=doc_pk)
        context['dev'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc_pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1010)
        context['actions'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc_pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1001)
        context['issues'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc_pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1002)
        context['lag'] = docreviews.objects.filter(drag_doc_fk__doc_pk=doc_pk)
        return context

def docdescriptionQuery(request):
    doc_pk = request.GET.get('doc_pk')

    queryset = documents.objects.get(doc_pk=doc_pk)
    return queryset

class NOEedit(UpdateView):
    model = documents
    form_class = NOEeditForm
    template_name="ceqanet/NOEedit.html"

    def get_success_url(self):
        success_url = "%s" % (reverse_lazy('NOEdescription'))
        return success_url        

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

class reviewdetail(ListView):
    template_name="ceqanet/reviewdetail.html"
    context_object_name = "detail"

    def get_queryset(self):
        queryset = ReviewDetailQuery(self.request)
        return queryset

def ReviewDetailQuery(request):
    doc_pk = request.GET.get('doc_pk')

    queryset = documents.objects.get(pk=doc_pk)
    return queryset

def accept(request):
    t = loader.get_template("ceqanet/accept.html")
    c = RequestContext(request,{})
    return HttpResponse(t.render(c))
