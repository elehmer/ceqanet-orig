from django.template import RequestContext, Context, loader
from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.generic.list import ListView
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse_lazy, reverse
from ceqanet.forms import QueryForm,SubmitForm,AddPrjForm,AddDocForm,InputForm,nocform,nodform,noeform,nopform
from ceqanet.models import projects,documents,geowords,leadagencies,reviewingagencies,doctypes,dockeywords,docreviews,latlongs
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

    queryset = projects.objects.filter(prj_schno__startswith=prj_schno).order_by('-prj_schno')
    return queryset


class addproject(FormView):
    template_name="ceqanet/addproject.html"
    form_class = AddPrjForm

class adddocument(FormView):
    template_name="ceqanet/adddocument.html"
    form_class = AddDocForm

    def get_context_data(self, **kwargs):
        context = super(adddocument, self).get_context_data(**kwargs)

        #context['date'] = datetime.now()
        context['prj_pk'] = self.request.GET.get("prj_pk")
        context['laglist'] = leadagencies.objects.get(lag_pk__exact=self.request.GET.get('lag_pk'))
        context['citylist'] = geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).order_by('geow_shortname')
        context['countylist'] = geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).order_by('geow_shortname')

        return context
    
    def get_initial(self):
        initial = super(adddocument, self).get_initial()

        la_query = leadagencies.objects.get(lag_pk__exact=self.request.GET.get('lag_pk'))
        initial['doc_lagaddress1'] = la_query.lag_address1.strip
        initial['doc_lagaddress2'] = la_query.lag_address2.strip
        initial['doc_lagcity'] = la_query.lag_city.strip
        initial['doc_lagstate'] = la_query.lag_state.strip
        initial['doc_lagzip'] = la_query.lag_zip.strip
        return initial

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

    #def save(self):
    #    data = self.cleaned_data
    #    docs = documents(doc_lagaddress1=data['doc_lagaddress1'])
    #    docs.save()

    def form_valid(self,form):
        data = self.cleaned_data
        docs = counties(geow_shortname=data['doc_lagaddress1'],geow_longname=data['doc_lagaddress1'])
        docs.save()
        #    datarecord = form.save(commit=False)
        #datarecord.save()
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
        queryset = documents.objects.filter(doc_prj_fk__prj_schno__startswith=prj_schno).order_by('-doc_received','-doc_prj_fk__prj_schno')
    elif mode == "B":
        queryset = documents.objects.order_by('-doc_received','-doc_prj_fk__prj_schno')
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

    queryset = documents.objects.filter(doc_prj_fk__exact=prj_pk).order_by('-doc_received')
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