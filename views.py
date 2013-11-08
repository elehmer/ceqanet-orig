import os
from django.template import RequestContext, Context, loader
from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponseRedirect
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import FormView,UpdateView
from django.core.urlresolvers import reverse_lazy, reverse
from django.core.mail import send_mail
from ceqanet.forms import QueryForm,basicqueryform,prjlistform,doclistform,advancedqueryform,submitform,usersettingsform
from ceqanet.forms import nocform,nodform,noeform,nopform
from ceqanet.forms import editnocform,editnoeform,editnodform,editnopform
from ceqanet.forms import pendingdetailnocform,pendingdetailnodform,pendingdetailnoeform,pendingdetailnopform
from ceqanet.forms import reviewdetailnocform,reviewdetailnodform,reviewdetailnoeform,reviewdetailnopform
from ceqanet.forms import commentdetailform
from ceqanet.models import projects,documents,geowords,leadagencies,reviewingagencies,doctypes,dockeywords,docreviews,latlongs,counties,UserProfile,clearinghouse,keywords
from datetime import datetime

def index(request):
    t = loader.get_template("ceqanet/index.html")
    c = RequestContext(request,{})
    return HttpResponse(t.render(c))

class basicquery(FormView):
    template_name="ceqanet/basicquery.html"
    form_class = basicqueryform

    def get_success_url(self):
        prj_schno = self.request.POST.get('prj_schno')
        colation = self.request.POST.get('colation')

        if colation == "project":
            success_url = "%s?prj_schno=%s&sortfld=-prj_schno&mode=basic" % (reverse_lazy('prjlist'),prj_schno)
        elif colation == "document":
            success_url = "%s?prj_schno=%s&sortfld=-doc_prj_fk__prj_schno&mode=basic" % (reverse_lazy('doclist'),prj_schno)
        return success_url

class advancedquery(FormView):
    template_name="ceqanet/advancedquery.html"
    form_class = advancedqueryform

    def get_success_url(self):
        prj_schno = self.request.POST.get('prj_schno')
        colation = self.request.POST.get('colation')

        if colation == "project":
            success_url = "%s?prj_schno=%s&sortfld=-prj_schno&mode=basic" % (reverse_lazy('prjlist'),prj_schno)
        elif colation == "document":
            success_url = "%s?prj_schno=%s&mode=basic" % (reverse_lazy('projectlist'),prj_schno)
            success_url = "%s?prj_pk=-9999&doctype=%s" % (reverse_lazy('docadd_'+doctype.lower()),doctype)
        return success_url

class prjlist(ListView):
    template_name="ceqanet/prjlist.html"
    context_object_name = "prjs"
    paginate_by = 25

    def get_queryset(self):
        queryset = prjlistquery(self.request)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(prjlist, self).get_context_data(**kwargs)

        mode = self.request.GET.get('mode')
        context['mode'] = mode
        context['sortfld'] = self.request.GET.get('sortfld')
        if mode == "basic":
            context['prj_schno'] = self.request.GET.get('prj_schno')

        qsminuspage = self.request.GET.copy()
        
        if "page" in qsminuspage:
            qsminuspage.pop('page')

        context['restofqs'] = qsminuspage.urlencode()
        context['form'] = prjlistform()
        
        return context

def prjlistquery(request):
    mode = request.GET.get('mode')

    queryset = ""

    if mode == "basic":
        prj_schno = request.GET.get('prj_schno')
        sortfld = request.GET.get('sortfld')

        queryset = projects.objects.filter(prj_visible=True).filter(prj_schno__startswith=prj_schno).order_by(sortfld)
    elif mode == "advanced":
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

class doclist(ListView):
    template_name="ceqanet/doclist.html"
    context_object_name = "docs"
    paginate_by = 25

    def get_queryset(self):
        queryset = doclistquery(self.request)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(doclist, self).get_context_data(**kwargs)

        mode = self.request.GET.get('mode')
        context['mode'] = mode
        context['sortfld'] = self.request.GET.get('sortfld')
        if mode == "basic":
            context['prj_schno'] = self.request.GET.get('prj_schno')

        qsminuspage = self.request.GET.copy()
        
        if "page" in qsminuspage:
            qsminuspage.pop('page')

        context['restofqs'] = qsminuspage.urlencode()
        context['form'] = doclistform()
        
        return context

def doclistquery(request):
    mode = request.GET.get('mode')

    queryset = ""

    if mode == "basic":
        prj_schno = request.GET.get('prj_schno')
        sortfld = request.GET.get('sortfld')

        queryset = documents.objects.filter(doc_visible=True).filter(doc_prj_fk__prj_schno__startswith=prj_schno).order_by(sortfld)
    elif mode == "advanced":
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
    form_class = submitform

    def get_success_url(self):
        doctype = self.request.POST.get('doctype')
        prjtoggle = self.request.POST.get('prjtoggle')

        if prjtoggle == "yes":
            success_url = "%s?prj_schno=&doctype=%s" % (reverse_lazy('findproject'),doctype)
        elif prjtoggle == "no":
            success_url = "%s?prj_pk=-9999&doctype=%s" % (reverse_lazy('docadd_'+doctype.lower()),doctype)
        return success_url

    def get_context_data(self, **kwargs):
        context = super(submit, self).get_context_data(**kwargs)

        context['laginfo'] = leadagencies.objects.get(pk=self.request.user.get_profile().set_lag_fk.lag_pk)
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
        context['formurl'] = 'docadd_'+self.request.GET.get('doctype').lower()
        context['restofqs'] = qsminuspage.urlencode()

        return context

def ClearinghouseQuery(request):
    prj_schno = request.GET.get('prj_schno')

    queryset = projects.objects.filter(prj_visible=True).filter(prj_schno__startswith=prj_schno).order_by('-prj_schno')
    return queryset

class docadd_noc(FormView):
    template_name="ceqanet/docadd_noc.html"
    form_class = nocform

    def get_success_url(self):
        success_url = "%s" % (reverse_lazy('accept'))
        return success_url

    def get_context_data(self, **kwargs):
        context = super(docadd_noc, self).get_context_data(**kwargs)

        context['prj_pk'] = self.request.GET.get("prj_pk")
        context['doctype'] = self.request.GET.get("doctype")
        if self.request.GET.get("prj_pk") != '-9999':
            context['prjinfo'] = projects.objects.get(prj_pk__exact=self.request.GET.get("prj_pk"))
        context['laglist'] = leadagencies.objects.get(pk=self.request.user.get_profile().set_lag_fk.lag_pk)

        return context
    
    def get_initial(self):
        initial = super(docadd_noc, self).get_initial()

        initial['doc_conname'] = self.request.user.first_name + " " + self.request.user.last_name
        initial['doc_conemail'] = self.request.user.email

        la_query = leadagencies.objects.get(pk=self.request.user.get_profile().set_lag_fk.lag_pk)
        initial['doc_conaddress1'] = la_query.lag_address1
        initial['doc_conaddress2'] = la_query.lag_address2
        initial['doc_concity'] = la_query.lag_city
        initial['doc_constate'] = la_query.lag_state
        initial['doc_conzip'] = la_query.lag_zip.strip
        return initial

    def form_valid(self,form):
        data = form.cleaned_data
        today = datetime.now()
        doc_received = today
        lag = leadagencies.objects.get(pk=self.request.user.get_profile().set_lag_fk.lag_pk)
        doc = documents.objects.get(pk=0)
        cnty = counties.objects.get(pk=data['doc_county'].pk)

        if data['doc_city'] != None:
            cityname = geowords.objects.get(pk=data['doc_city'].pk)
        else:
            cityname = None
        if data['doc_county'] != None:
            countyname = geowords.objects.get(pk=data['doc_county'].pk)
        else:
            countyname = None

        if data['doc_conaddress2'] == '':
            doc_conaddress2 = None
        else:
            doc_conaddress2 = data['doc_conaddress2']
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

        if data['doc_city'] != None:
            doc_city = cityname.geow_shortname
        else:
            doc_city = ''
        if data['doc_county'] != None:
            doc_county = countyname.geow_shortname
        else:
            doc_county = ''

        if self.request.POST.get('prj_pk') == '-9999':
            prj = projects(prj_lag_fk=lag,prj_doc_fk=doc,prj_status=data['doctypeid'].keyw_shortname,prj_title=data['prj_title'],prj_description=data['prj_description'],prj_leadagency=lag.lag_name,prj_datefirst=today,prj_datelast=today)
            prj.save()
        else:
            prj = projects.objects.get(pk=self.request.POST.get('prj_pk'))
            prj.prj_status = data['doctypeid'].keyw_shortname
            prj.prj_datelast = today

        adddoc = documents(doc_prj_fk=prj,doc_cnty_fk=cnty,doc_doct_fk=data['doctypeid'],doc_doctype=data['doctypeid'].keyw_shortname,doc_docname=data['doctypeid'].keyw_longname,doc_conname=data['doc_conname'],doc_conagency=lag.lag_name,doc_conemail=data['doc_conemail'],doc_conphone=data['doc_conphone'],doc_conaddress1=data['doc_conaddress1'],doc_conaddress2=doc_conaddress2,doc_concity=data['doc_concity'],doc_constate=data['doc_constate'],doc_conzip=data['doc_conzip'],doc_location=data['doc_location'],doc_city=doc_city,doc_county=doc_county,doc_pending=1,doc_received=doc_received,doc_parcelno=doc_parcelno,doc_xstreets=doc_xstreets,doc_township=doc_township,doc_range=doc_range,doc_section=doc_section,doc_base=doc_base,doc_highways=doc_highways,doc_airports=doc_airports,doc_railways=doc_railways,doc_waterways=doc_waterways,doc_landuse=doc_landuse,doc_schools=doc_schools)
        adddoc.save()

        coords = latlongs(doc_pk=adddoc.pk,doc_prj_fk=prj,doc_doctype=self.request.POST.get('doctype'),doc_latitude=data['doc_latitude'],doc_longitude=data['doc_longitude'])
        coords.save()

        for a in data['actions']:
            if a.keyw_pk == 1018:
                adockeyw = dockeywords(dkey_doc_fk=adddoc,dkey_keyw_fk=a,dkey_comment=data['dkey_comment_actions'],dkey_rank=0)
            else:
                adockeyw = dockeywords(dkey_doc_fk=adddoc,dkey_keyw_fk=a,dkey_rank=0)
            adockeyw.save()

        devtypes = keywords.objects.filter(keyw_keyl_fk__keyl_pk=1010)
        for d in devtypes:
            if self.request.POST.get('dev'+str(d.keyw_pk)) == "1":
                if d.keyw_pk == 11001:
                    ddockeyw = dockeywords(dkey_doc_fk=adddoc,dkey_keyw_fk=d,dkey_comment=data['dkey_comment_dev'],dkey_value1=self.request.POST.get('dev'+str(d.keyw_pk)+'_val1'),dkey_value2=self.request.POST.get('dev'+str(d.keyw_pk)+'_val2'),dkey_value3=self.request.POST.get('dev'+str(d.keyw_pk)+'_val3'),dkey_rank=0)
                else:
                    ddockeyw = dockeywords(dkey_doc_fk=adddoc,dkey_keyw_fk=d,dkey_value1=self.request.POST.get('dev'+str(d.keyw_pk)+'_val1'),dkey_value2=self.request.POST.get('dev'+str(d.keyw_pk)+'_val2'),dkey_value3=self.request.POST.get('dev'+str(d.keyw_pk)+'_val3'),dkey_rank=0)
                ddockeyw.save()
        if self.request.POST.get('devtrans') == "1":
            ddockeyw = dockeywords(dkey_doc_fk=adddoc,dkey_keyw_fk=data['devtrans_id'],dkey_comment=data['devtrans_comment'],dkey_value1=None,dkey_value2=None,dkey_value3=None,dkey_rank=0)
            ddockeyw.save()
        if self.request.POST.get('devpower') == "1":
            ddockeyw = dockeywords(dkey_doc_fk=adddoc,dkey_keyw_fk=data['devpower_id'],dkey_comment=data['devpower_comment'],dkey_value1=self.request.POST.get('devpower_val1'),dkey_value2=None,dkey_value3=None,dkey_rank=0)
            ddockeyw.save()
        if self.request.POST.get('devwaste') == "1":
            ddockeyw = dockeywords(dkey_doc_fk=adddoc,dkey_keyw_fk=data['devwaste_id'],dkey_comment=data['devwaste_comment'],dkey_value1=None,dkey_value2=None,dkey_value3=None,dkey_rank=0)
            ddockeyw.save()

        issues = keywords.objects.filter(keyw_keyl_fk__keyl_pk=1002)
        for i in issues:
            if self.request.POST.get('issue'+str(i.keyw_pk)) == "1":
                if i.keyw_pk == 2034:
                    idockeyw = dockeywords(dkey_doc_fk=adddoc,dkey_keyw_fk=i,dkey_comment=data['dkey_comment_issues'],dkey_rank=0)
                else:
                    idockeyw = dockeywords(dkey_doc_fk=adddoc,dkey_keyw_fk=i,dkey_rank=0)
                idockeyw.save()

        for ra in data['ragencies']:
            docrev = docreviews(drag_doc_fk=adddoc,drag_rag_fk=ra,drag_rank=0,drag_copies=1)
            docrev.save()

        prj.prj_doc_fk=adddoc
        prj.save()

        strFrom = "ceqanet@opr.ca.gov"
        ToList = [data['doc_conemail']]
        strSubject = "Confirmation of Submittal - " + data['doctypeid'].keyw_longname
        strBody = "This confirms receipt of your electronic " + data['doctypeid'].keyw_longname + " form submission on " + doc_received.strftime('%m/%d/%Y') + ".  \n \n"
        strBody = strBody + "The State Clearinghouse will review your submittal and provide a State Clearinghouse Number and filing date within one business day. \n \n"
        strBody = strBody + "If you have questions about the form submittal process, please reply to this email.  Thank you for using CEQAnet. \n"
        strBody = strBody + "\n \n" + "--- Information Submitted ---" + "\n"
        strBody = strBody + "Document Type: " + data['doctypeid'].keyw_shortname + "\n"        
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
        strBody = strBody + "Agency Approving Project: " + lag.lag_name + "\n"
        strBody = strBody + "Primary Contact:  " + "\n"
        strBody = strBody + "    Name: " + data['doc_conname'] + "\n"
        strBody = strBody + "    Phone: " + data['doc_conphone'] + "\n"
        strBody = strBody + "    E-mail: " + data['doc_conemail'] + "\n"
        strBody = strBody + "DATE: " + doc_received.strftime('%m/%d/%Y') + "\n"

        try:
            send_mail(strSubject,strBody,strFrom,ToList,fail_silently=False)
        except Exception as detail:
            print "Not Able to Send Email:", detail

        return super(docadd_noc,self).form_valid(form)

class docadd_nod(FormView):
    template_name="ceqanet/docadd_nod.html"
    form_class = nodform

    def get_success_url(self):
        success_url = "%s" % (reverse_lazy('accept'))
        return success_url

    def get_initial(self):
        initial = super(docadd_nod, self).get_initial()

        if self.request.GET.get("prj_pk") != '-9999':
            prjinfo = projects.objects.get(prj_pk__exact=self.request.GET.get("prj_pk"))
            initial['prj_title'] = prjinfo.prj_title
            initial['prj_description'] = prjinfo.prj_description

        initial['doc_conname'] = self.request.user.first_name + " " + self.request.user.last_name
        initial['doc_conemail'] = self.request.user.email
        initial['doc_conphone'] = self.request.user.get_profile().conphone

        la_query = leadagencies.objects.get(pk=self.request.user.get_profile().set_lag_fk.lag_pk)
        initial['doc_conaddress1'] = la_query.lag_address1
        initial['doc_conaddress2'] = la_query.lag_address2
        initial['doc_concity'] = la_query.lag_city
        initial['doc_constate'] = la_query.lag_state
        initial['doc_conzip'] = la_query.lag_zip.strip
        return initial

    def get_context_data(self, **kwargs):
        context = super(docadd_nod, self).get_context_data(**kwargs)

        context['prj_pk'] = self.request.GET.get("prj_pk")
        context['doctype'] = self.request.GET.get("doctype")
        if self.request.GET.get("prj_pk") != '-9999':
            context['prjinfo'] = projects.objects.get(prj_pk__exact=self.request.GET.get("prj_pk"))
        context['laglist'] = leadagencies.objects.get(pk=self.request.user.get_profile().set_lag_fk.lag_pk)
        return context

    def form_valid(self,form):
        data = form.cleaned_data
        today = datetime.now()
        doc_received = today
        lag = leadagencies.objects.get(pk=self.request.user.get_profile().set_lag_fk.lag_pk)
        doc = documents.objects.get(pk=0)
        cnty = counties.objects.get(pk=data['doc_county'].pk)
        doct = doctypes.objects.get(keyw_shortname__startswith=self.request.POST.get('doctype'))
        if data['doc_conaddress2'] == '':
            doc_conaddress2 = None
        else:
            doc_conaddress2 = data['doc_conaddress2']

        if self.request.POST.get('prj_pk') == '-9999':
            prj = projects(prj_lag_fk=lag,prj_doc_fk=doc,prj_status=self.request.POST.get('doctype'),prj_title=data['prj_title'],prj_description=data['prj_description'],prj_leadagency=lag.lag_name,prj_datefirst=today,prj_datelast=today)
            prj.save()
        else:
            prj = projects.objects.get(pk=self.request.POST.get('prj_pk'))
            prj.prj_status = self.request.POST.get('doctype')
            prj.prj_datelast = today

        adddoc = documents(doc_prj_fk=prj,doc_cnty_fk=cnty,doc_doct_fk=doct,doc_doctype=self.request.POST.get('doctype'),doc_docname=doct.keyw_longname,doc_conname=data['doc_conname'],doc_conagency=lag.lag_name,doc_conemail=data['doc_conemail'],doc_conphone=data['doc_conphone'],doc_conaddress1=data['doc_conaddress1'],doc_conaddress2=doc_conaddress2,doc_concity=data['doc_concity'],doc_constate=data['doc_constate'],doc_conzip=data['doc_conzip'],doc_location=data['doc_location'],doc_city=data['doc_city'].geow_shortname,doc_county=data['doc_county'].geow_shortname,doc_pending=1,doc_received=doc_received,doc_nodbylead=data['doc_nodbylead'],doc_nodbyresp=data['doc_nodbyresp'],doc_nodagency=data['doc_nodagency'],doc_nod=data['doc_nod'],doc_detsigeffect=data['doc_detsigeffect'],doc_detnotsigeffect=data['doc_detnotsigeffect'],doc_deteir=data['doc_deteir'],doc_detnegdec=data['doc_detnegdec'],doc_detmitigation=data['doc_detmitigation'],doc_detnotmitigation=data['doc_detnotmitigation'],doc_detconsider=data['doc_detconsider'],doc_detnotconsider=data['doc_detnotconsider'],doc_detfindings=data['doc_detfindings'],doc_detnotfindings=data['doc_detnotfindings'],doc_eiravailableat=data['doc_eiravailableat'])
        adddoc.save()
        prj.prj_doc_fk=adddoc
        prj.save()

        coords = latlongs(doc_pk=adddoc.pk,doc_prj_fk=prj,doc_doctype=self.request.POST.get('doctype'),doc_latitude=data['doc_latitude'],doc_longitude=data['doc_longitude'])
        coords.save()

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
        strBody = strBody + "    Phone: " + data['doc_conphone'] + "\n"
        strBody = strBody + "    E-mail: " + data['doc_conemail'] + "\n"
        strBody = strBody + "DATE: " + doc_received.strftime('%m/%d/%Y') + "\n"

        try:
            send_mail(strSubject,strBody,strFrom,ToList,fail_silently=False)
        except Exception as detail:
            print "Not Able to Send Email:", detail

        return super(docadd_nod,self).form_valid(form)

class docadd_noe(FormView):
    template_name="ceqanet/docadd_noe.html"
    form_class = noeform

    def get_success_url(self):
        success_url = "%s" % (reverse_lazy('accept'))
        return success_url

    def get_initial(self):
        initial = super(docadd_noe, self).get_initial()

        if self.request.GET.get("prj_pk") != '-9999':
            prjinfo = projects.objects.get(prj_pk__exact=self.request.GET.get("prj_pk"))
            initial['prj_title'] = prjinfo.prj_title
            initial['prj_description'] = prjinfo.prj_description

        initial['doc_conname'] = self.request.user.first_name + " " + self.request.user.last_name
        initial['doc_conemail'] = self.request.user.email
        initial['doc_conphone'] = self.request.user.get_profile().conphone

        la_query = leadagencies.objects.get(pk=self.request.user.get_profile().set_lag_fk.lag_pk)
        initial['doc_conaddress1'] = la_query.lag_address1
        initial['doc_conaddress2'] = la_query.lag_address2
        initial['doc_concity'] = la_query.lag_city
        initial['doc_constate'] = la_query.lag_state
        initial['doc_conzip'] = la_query.lag_zip.strip
        return initial

    def get_context_data(self, **kwargs):
        context = super(docadd_noe, self).get_context_data(**kwargs)

        context['prj_pk'] = self.request.GET.get("prj_pk")
        context['doctype'] = self.request.GET.get("doctype")
        if self.request.GET.get("prj_pk") != '-9999':
            context['prjinfo'] = projects.objects.get(prj_pk__exact=self.request.GET.get("prj_pk"))
        context['laglist'] = leadagencies.objects.get(pk=self.request.user.get_profile().set_lag_fk.lag_pk)
        return context

    def form_valid(self,form):
        data = form.cleaned_data
        today = datetime.now()
        doc_received = today
        lag = leadagencies.objects.get(pk=self.request.user.get_profile().set_lag_fk.lag_pk)
        doc = documents.objects.get(pk=0)
        cnty = counties.objects.get(pk=data['doc_county'].pk)
        doct = doctypes.objects.get(keyw_shortname__startswith=self.request.POST.get('doctype'))
        if data['doc_conaddress2'] == '':
            doc_conaddress2 = None
        else:
            doc_conaddress2 = data['doc_conaddress2']

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
            prj = projects(prj_lag_fk=lag,prj_doc_fk=doc,prj_status=self.request.POST.get('doctype'),prj_title=data['prj_title'],prj_description=data['prj_description'],prj_leadagency=lag.lag_name,prj_datefirst=today,prj_datelast=today)
            prj.save()
        else:
            prj = projects.objects.get(pk=self.request.POST.get('prj_pk'))
            prj.prj_status = self.request.POST.get('doctype')
            prj.prj_datelast = today

        adddoc = documents(doc_prj_fk=prj,doc_cnty_fk=cnty,doc_doct_fk=doct,doc_doctype=self.request.POST.get('doctype'),doc_docname=doct.keyw_longname,doc_conname=data['doc_conname'],doc_conagency=lag.lag_name,doc_conemail=data['doc_conemail'],doc_conphone=data['doc_conphone'],doc_conaddress1=data['doc_conaddress1'],doc_conaddress2=doc_conaddress2,doc_concity=data['doc_concity'],doc_constate=data['doc_constate'],doc_conzip=data['doc_conzip'],doc_location=data['doc_location'],doc_city=data['doc_city'].geow_shortname,doc_county=data['doc_county'].geow_shortname,doc_pending=1,doc_received=doc_received,doc_exministerial=doc_exministerial,doc_exdeclared=doc_exdeclared,doc_exemergency=doc_exemergency,doc_excategorical=doc_excategorical,doc_exstatutory=doc_exstatutory,doc_exnumber=doc_exnumber,doc_exreasons=data['doc_exreasons'])
        adddoc.save()
        prj.prj_doc_fk=adddoc
        prj.save()

        coords = latlongs(doc_pk=adddoc.pk,doc_prj_fk=prj,doc_doctype=self.request.POST.get('doctype'),doc_latitude=data['doc_latitude'],doc_longitude=data['doc_longitude'])
        coords.save()

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
        strBody = strBody + "    Phone: " + data['doc_conphone'] + "\n"
        strBody = strBody + "    E-mail: " + data['doc_conemail'] + "\n"
        strBody = strBody + "Exempt Status: " + status + "\n"
        strBody = strBody + "Reason for Exemption: " + data['doc_exreasons'] + "\n"
        strBody = strBody + "DATE: " + doc_received.strftime('%m/%d/%Y') + "\n"

        try:
            send_mail(strSubject,strBody,strFrom,ToList,fail_silently=False)
        except Exception as detail:
            print "Not Able to Send Email:", detail

        return super(docadd_noe,self).form_valid(form)

class docadd_nop(FormView):
    template_name="ceqanet/docadd_nop.html"
    form_class = nopform

    def get_success_url(self):
        success_url = "%s" % (reverse_lazy('accept'))
        return success_url

    def get_context_data(self, **kwargs):
        context = super(docadd_nop, self).get_context_data(**kwargs)

        context['prj_pk'] = self.request.GET.get("prj_pk")
        context['doctype'] = self.request.GET.get("doctype")
        if self.request.GET.get("prj_pk") != '-9999':
            context['prjinfo'] = projects.objects.get(prj_pk__exact=self.request.GET.get("prj_pk"))
        context['laglist'] = leadagencies.objects.get(pk=self.request.user.get_profile().set_lag_fk.lag_pk)

        return context
    
    def get_initial(self):
        initial = super(docadd_nop, self).get_initial()

        initial['doc_conname'] = self.request.user.first_name + " " + self.request.user.last_name
        initial['doc_conemail'] = self.request.user.email

        la_query = leadagencies.objects.get(pk=self.request.user.get_profile().set_lag_fk.lag_pk)
        initial['doc_conaddress1'] = la_query.lag_address1
        initial['doc_conaddress2'] = la_query.lag_address2
        initial['doc_concity'] = la_query.lag_city
        initial['doc_constate'] = la_query.lag_state
        initial['doc_conzip'] = la_query.lag_zip.strip
        return initial

    def form_valid(self,form):
        data = form.cleaned_data
        today = datetime.now()
        doc_received = today
        lag = leadagencies.objects.get(pk=self.request.user.get_profile().set_lag_fk.lag_pk)
        doc = documents.objects.get(pk=0)
        cnty = counties.objects.get(pk=data['doc_county'].pk)
        doct = doctypes.objects.get(keyw_shortname__startswith=self.request.POST.get('doctype'))

        if data['doc_city'] != None:
            cityname = geowords.objects.get(pk=data['doc_city'].pk)
        else:
            cityname = None
        if data['doc_county'] != None:
            countyname = geowords.objects.get(pk=data['doc_county'].pk)
        else:
            countyname = None
        
        if data['doc_conaddress2'] == '':
            doc_conaddress2 = None
        else:
            doc_conaddress2 = data['doc_conaddress2']
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

        if data['doc_city'] != None:
            doc_city = cityname.geow_shortname
        else:
            doc_city = ''
        if data['doc_county'] != None:
            doc_county = countyname.geow_shortname
        else:
            doc_county = ''

        if self.request.POST.get('prj_pk') == '-9999':
            prj = projects(prj_lag_fk=lag,prj_doc_fk=doc,prj_status=self.request.POST.get('doctype'),prj_title=data['prj_title'],prj_description=data['prj_description'],prj_leadagency=lag.lag_name,prj_datefirst=today,prj_datelast=today)
            prj.save()
        else:
            prj = projects.objects.get(pk=self.request.POST.get('prj_pk'))
            prj.prj_status = self.request.POST.get('doctype')
            prj.prj_datelast = today

        adddoc = documents(doc_prj_fk=prj,doc_cnty_fk=cnty,doc_doct_fk=doct,doc_doctype=doct.keyw_shortname,doc_docname=doct.keyw_longname,doc_conname=data['doc_conname'],doc_conagency=lag.lag_name,doc_conemail=data['doc_conemail'],doc_conphone=data['doc_conphone'],doc_conaddress1=data['doc_conaddress1'],doc_conaddress2=doc_conaddress2,doc_concity=data['doc_concity'],doc_constate=data['doc_constate'],doc_conzip=data['doc_conzip'],doc_location=data['doc_location'],doc_city=doc_city,doc_county=doc_county,doc_pending=1,doc_received=doc_received,doc_parcelno=doc_parcelno,doc_xstreets=doc_xstreets,doc_township=doc_township,doc_range=doc_range,doc_section=doc_section,doc_base=doc_base,doc_highways=doc_highways,doc_airports=doc_airports,doc_railways=doc_railways,doc_waterways=doc_waterways,doc_landuse=doc_landuse,doc_schools=doc_schools)
        adddoc.save()

        coords = latlongs(doc_pk=adddoc.pk,doc_prj_fk=prj,doc_doctype=self.request.POST.get('doctype'),doc_latitude=data['doc_latitude'],doc_longitude=data['doc_longitude'])
        coords.save()

        for a in data['actions']:
            if a.keyw_pk == 1018:
                adockeyw = dockeywords(dkey_doc_fk=adddoc,dkey_keyw_fk=a,dkey_comment=data['dkey_comment_actions'],dkey_rank=0)
            else:
                adockeyw = dockeywords(dkey_doc_fk=adddoc,dkey_keyw_fk=a,dkey_rank=0)
            adockeyw.save()

        devtypes = keywords.objects.filter(keyw_keyl_fk__keyl_pk=1010)
        for d in devtypes:
            if self.request.POST.get('dev'+str(d.keyw_pk)) == "1":
                if d.keyw_pk == 11001:
                    ddockeyw = dockeywords(dkey_doc_fk=adddoc,dkey_keyw_fk=d,dkey_comment=data['dkey_comment_dev'],dkey_value1=self.request.POST.get('dev'+str(d.keyw_pk)+'_val1'),dkey_value2=self.request.POST.get('dev'+str(d.keyw_pk)+'_val2'),dkey_value3=self.request.POST.get('dev'+str(d.keyw_pk)+'_val3'),dkey_rank=0)
                else:
                    ddockeyw = dockeywords(dkey_doc_fk=adddoc,dkey_keyw_fk=d,dkey_value1=self.request.POST.get('dev'+str(d.keyw_pk)+'_val1'),dkey_value2=self.request.POST.get('dev'+str(d.keyw_pk)+'_val2'),dkey_value3=self.request.POST.get('dev'+str(d.keyw_pk)+'_val3'),dkey_rank=0)
                ddockeyw.save()
        if self.request.POST.get('devtrans') == "1":
            ddockeyw = dockeywords(dkey_doc_fk=adddoc,dkey_keyw_fk=data['devtrans_id'],dkey_comment=data['devtrans_comment'],dkey_value1=None,dkey_value2=None,dkey_value3=None,dkey_rank=0)
            ddockeyw.save()
        if self.request.POST.get('devpower') == "1":
            ddockeyw = dockeywords(dkey_doc_fk=adddoc,dkey_keyw_fk=data['devpower_id'],dkey_comment=data['devpower_comment'],dkey_value1=self.request.POST.get('devpower_val1'),dkey_value2=None,dkey_value3=None,dkey_rank=0)
            ddockeyw.save()
        if self.request.POST.get('devwaste') == "1":
            ddockeyw = dockeywords(dkey_doc_fk=adddoc,dkey_keyw_fk=data['devwaste_id'],dkey_comment=data['devwaste_comment'],dkey_value1=None,dkey_value2=None,dkey_value3=None,dkey_rank=0)
            ddockeyw.save()

        issues = keywords.objects.filter(keyw_keyl_fk__keyl_pk=1002)
        for i in issues:
            if self.request.POST.get('issue'+str(i.keyw_pk)) == "1":
                if i.keyw_pk == 2034:
                    idockeyw = dockeywords(dkey_doc_fk=adddoc,dkey_keyw_fk=i,dkey_comment=data['dkey_comment_issues'],dkey_rank=0)
                else:
                    idockeyw = dockeywords(dkey_doc_fk=adddoc,dkey_keyw_fk=i,dkey_rank=0)
                idockeyw.save()

        for ra in data['ragencies']:
            docrev = docreviews(drag_doc_fk=adddoc,drag_rag_fk=ra,drag_rank=0,drag_copies=1)
            docrev.save()

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
        strBody = strBody + "Agency Approving Project: " + lag.lag_name + "\n"
        strBody = strBody + "Primary Contact:  " + "\n"
        strBody = strBody + "    Name: " + data['doc_conname'] + "\n"
        strBody = strBody + "    Phone: " + data['doc_conphone'] + "\n"
        strBody = strBody + "    E-mail: " + data['doc_conemail'] + "\n"
        strBody = strBody + "DATE: " + doc_received.strftime('%m/%d/%Y') + "\n"

        try:
            send_mail(strSubject,strBody,strFrom,ToList,fail_silently=False)
        except Exception as detail:
            print "Not Able to Send Email:", detail

        return super(docadd_nop,self).form_valid(form)

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

class docdesp_noc(DetailView):
    model = documents
    template_name="ceqanet/docdesp_noc.html"
    context_object_name = "doc"

    def get_context_data(self, **kwargs):
        context = super(docdesp_noc, self).get_context_data(**kwargs)
        doc_pk = self.kwargs['pk']
        context['doc_pk'] = doc_pk
        context['latlongs'] = latlongs.objects.filter(doc_pk=doc_pk)
        context['dev'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc_pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1010)
        context['actions'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc_pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1001)
        context['issues'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc_pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1002)
        context['reviews'] = docreviews.objects.filter(drag_doc_fk__doc_pk=doc_pk)
        return context

class docdesp_nod(DetailView):
    model = documents
    template_name="ceqanet/docdesp_nod.html"
    context_object_name = "doc"

    def get_context_data(self, **kwargs):
        context = super(docdesp_nod, self).get_context_data(**kwargs)
        doc_pk = self.kwargs['pk']
        context['doc_pk'] = doc_pk
        context['latlongs'] = latlongs.objects.filter(doc_pk=self.kwargs['pk'])
        return context

class docdesp_noe(DetailView):
    model = documents
    template_name="ceqanet/docdesp_noe.html"
    context_object_name = "doc"

    def get_context_data(self, **kwargs):
        context = super(docdesp_noe, self).get_context_data(**kwargs)
        doc_pk = self.kwargs['pk']
        context['doc_pk'] = doc_pk
        context['latlongs'] = latlongs.objects.filter(doc_pk=self.kwargs['pk'])
        return context

class docdesp_nop(DetailView):
    model = documents
    template_name="ceqanet/docdesp_nop.html"
    context_object_name = "doc"

    def get_context_data(self, **kwargs):
        context = super(docdesp_nop, self).get_context_data(**kwargs)
        doc_pk = self.kwargs['pk']
        context['doc_pk'] = doc_pk
        context['latlongs'] = latlongs.objects.filter(doc_pk=doc_pk)
        context['dev'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc_pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1010)
        context['actions'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc_pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1001)
        context['issues'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc_pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1002)
        context['reviews'] = docreviews.objects.filter(drag_doc_fk__doc_pk=doc_pk)
        return context

class docedit_noc(FormView):
    form_class = editnocform
    template_name="ceqanet/docedit_noc.html"

    def get_success_url(self):
        success_url = reverse_lazy('docdesp_noc', args=[self.request.POST.get('doc_pk')])
        return success_url
    
    def get_initial(self):
        initial = super(docedit_noc, self).get_initial()

        docinfo = documents.objects.get(pk=self.request.GET.get('doc_pk'))
        latlonginfo = latlongs.objects.filter(doc_pk=self.request.GET.get('doc_pk'))
        devinfo = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1010)
        dkey_comment_actions = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_pk=1018)
        dkey_comment_dev = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_pk=11001)
        dkey_comment_issues = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_pk=2034)
        
        initial['prj_title'] = docinfo.doc_prj_fk.prj_title
        initial['prj_description'] = docinfo.doc_prj_fk.prj_description
        initial['doc_conagency'] = docinfo.doc_conagency
        initial['doc_conname'] = docinfo.doc_conname
        initial['doc_conemail'] = docinfo.doc_conemail
        initial['doc_conphone'] = docinfo.doc_conphone
        initial['doc_conaddress1'] = docinfo.doc_conaddress1
        initial['doc_conaddress2'] = docinfo.doc_conaddress2
        initial['doc_concity'] = docinfo.doc_concity
        initial['doc_constate'] = docinfo.doc_constate
        initial['doc_conzip'] = docinfo.doc_conzip.strip
        initial['doc_location'] = docinfo.doc_location
        if latlonginfo.exists():
            initial['doc_latitude'] = latlonginfo[0].doc_latitude
            initial['doc_longitude'] = latlonginfo[0].doc_longitude

        if docinfo.doc_city != None:
            cityinfo = geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).filter(geow_shortname__startswith=docinfo.doc_city)
            if cityinfo.count() == 1:
                initial['doc_city'] = cityinfo[0].geow_pk

        if docinfo.doc_county != None:
            countyinfo = geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).filter(geow_shortname__startswith=docinfo.doc_county)
            if countyinfo.count() == 1:
                initial['doc_county'] = countyinfo[0].geow_pk

        initial['doc_parcelno'] = docinfo.doc_parcelno
        initial['doc_xstreets'] = docinfo.doc_xstreets
        initial['doc_township'] = docinfo.doc_township
        initial['doc_range'] = docinfo.doc_range
        initial['doc_section'] = docinfo.doc_section
        initial['doc_base'] = docinfo.doc_base
        initial['doc_highways'] = docinfo.doc_highways
        initial['doc_railways'] = docinfo.doc_railways
        initial['doc_airports'] = docinfo.doc_airports
        initial['doc_schools'] = docinfo.doc_schools
        initial['doc_waterways'] = docinfo.doc_waterways
        initial['doc_parcelno'] = docinfo.doc_parcelno
        initial['doc_landuse'] = docinfo.doc_landuse

        initial['doctypeid'] = docinfo.doc_doct_fk.keyw_pk
        if dkey_comment_actions.exists():
            initial['dkey_comment_actions'] = dkey_comment_actions[0].dkey_comment
        if dkey_comment_dev.exists():
            initial['dkey_comment_dev'] = dkey_comment_dev[0].dkey_comment
        if dkey_comment_issues.exists():
            initial['dkey_comment_issues'] = dkey_comment_issues[0].dkey_comment

        for dev in devinfo:
            if dev.dkey_keyw_fk.keyw_pk > 4000:
                if dev.dkey_keyw_fk.keyw_pk < 5000:
                    initial['devtrans_id'] = dev.dkey_keyw_fk.keyw_pk
                    initial['devtrans_comment'] = dev.dkey_comment
            if dev.dkey_keyw_fk.keyw_pk > 3000:
                if dev.dkey_keyw_fk.keyw_pk < 4000:
                    initial['devpower_id'] = dev.dkey_keyw_fk.keyw_pk
                    initial['devpower_comment'] = dev.dkey_comment
            if dev.dkey_keyw_fk.keyw_pk == 6001:
                initial['dev6001_val1'] = dev.dkey_value1
                initial['dev6001_val2'] = dev.dkey_value2
            elif dev.dkey_keyw_fk.keyw_pk == 6002:
                initial['dev6002_val1'] = dev.dkey_value1
                initial['dev6002_val2'] = dev.dkey_value2
                initial['dev6002_val3'] = dev.dkey_value3
            elif dev.dkey_keyw_fk.keyw_pk == 6003:
                initial['dev6003_val1'] = dev.dkey_value1
                initial['dev6003_val2'] = dev.dkey_value2
                initial['dev6003_val3'] = dev.dkey_value3
            elif dev.dkey_keyw_fk.keyw_pk == 6004:
                initial['dev6004_val1'] = dev.dkey_value1
                initial['dev6004_val2'] = dev.dkey_value2
                initial['dev6004_val3'] = dev.dkey_value3
            elif dev.dkey_keyw_fk.keyw_pk == 7001:
                initial['dev7001_val1'] = dev.dkey_value1
            elif dev.dkey_keyw_fk.keyw_pk == 8001:
                initial['dev8001_val1'] = dev.dkey_value1
            elif dev.dkey_keyw_fk.keyw_pk == 9001:
                initial['dev9001_val1'] = dev.dkey_value1
            elif dev.dkey_keyw_fk.keyw_pk == 10001:
                initial['dev10001_val1'] = dev.dkey_value1

        return initial

    def get_context_data(self, **kwargs):
        context = super(docedit_noc, self).get_context_data(**kwargs)
        context['doc_pk'] = self.request.GET.get('doc_pk')
        context['lats'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1001)
        context['devs'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1010)
        context['isss'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1002)

        return context

    def form_valid(self,form):
        data = form.cleaned_data
        doc = documents.objects.get(pk=self.request.POST.get('doc_pk'))
        prj = projects.objects.get(pk=doc.doc_prj_fk.prj_pk)

        if data['doc_city'] != None:
            cityname = geowords.objects.get(pk=data['doc_city'].pk)
        else:
            cityname = None
        if data['doc_county'] != None:
            countyname = geowords.objects.get(pk=data['doc_county'].pk)
        else:
            countyname = None

        if data['doc_conaddress2'] == '':
            doc_conaddress2 = None
        else:
            doc_conaddress2 = data['doc_conaddress2']
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

        doc.doc_conagency = data['doc_conagency']
        doc.doc_conname = data['doc_conname']
        doc.doc_conemail = data['doc_conemail']
        doc.doc_conphone = data['doc_conphone']
        doc.doc_conaddress1 = data['doc_conaddress1']
        doc.doc_conaddress2 = doc_conaddress2
        doc.doc_concity = data['doc_concity']
        doc.doc_constate = data['doc_constate']
        doc.doc_conzip = data['doc_conzip']
        doc.doc_location = data['doc_location']
        if data['doc_city'] != None:
            doc.doc_city = cityname.geow_shortname
        else:
            doc.doc_city = ''
        if data['doc_county'] != None:
            doc.doc_county = countyname.geow_shortname
        else:
            doc.doc_county = ''
        doc.doc_parcelno = doc_parcelno
        doc.doc_xstreets = doc_xstreets
        doc.doc_township = doc_township
        doc.doc_range = doc_range
        doc.doc_section = doc_section
        doc.doc_base = doc.doc_base
        doc.doc_highways = doc_highways
        doc.doc_airports = doc_airports
        doc.doc_railways = doc_railways
        doc.doc_waterways = doc_waterways
        doc.doc_landuse = doc_landuse
        doc.doc_schools = doc_schools
        doc.doc_doct_fk = data['doctypeid']
        doc.doc_doctype = data['doctypeid'].keyw_shortname
        doc.doc_docname = data['doctypeid'].keyw_longname
        doc.save()
        prj.prj_title = data['prj_title']
        prj.prj_description = data['prj_description']
        prj.save()

        try:
            coords = latlongs.objects.get(pk=doc.pk)
            coords.doc_latitude = data['doc_latitude']
            coords.doc_longitude = data['doc_longitude']
        except latlongs.DoesNotExist:
            coords = latlongs(doc_pk=doc.pk,doc_prj_fk=prj,doc_doctype="NOC",doc_latitude=data['doc_latitude'],doc_longitude=data['doc_longitude'])
        coords.save()

        dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc.pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1001).delete()

        for a in data['actions']:
            if a.keyw_pk == 1018:
                adockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=a,dkey_comment=data['dkey_comment_actions'],dkey_rank=0)
            else:
                adockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=a,dkey_rank=0)
            adockeyw.save()
        
        dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc.pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1010).delete()

        devtypes = keywords.objects.filter(keyw_keyl_fk__keyl_pk=1010)
        for d in devtypes:
            if self.request.POST.get('dev'+str(d.keyw_pk)) == "1":
                if d.keyw_pk == 11001:
                    ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=d,dkey_comment=data['dkey_comment_dev'],dkey_value1=self.request.POST.get('dev'+str(d.keyw_pk)+'_val1'),dkey_value2=self.request.POST.get('dev'+str(d.keyw_pk)+'_val2'),dkey_value3=self.request.POST.get('dev'+str(d.keyw_pk)+'_val3'),dkey_rank=0)
                else:
                    ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=d,dkey_value1=self.request.POST.get('dev'+str(d.keyw_pk)+'_val1'),dkey_value2=self.request.POST.get('dev'+str(d.keyw_pk)+'_val2'),dkey_value3=self.request.POST.get('dev'+str(d.keyw_pk)+'_val3'),dkey_rank=0)
                ddockeyw.save()
        if self.request.POST.get('devtrans') == "1":
            ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=data['devtrans_id'],dkey_comment=data['devtrans_comment'],dkey_value1=None,dkey_value2=None,dkey_value3=None,dkey_rank=0)
            ddockeyw.save()
        if self.request.POST.get('devpower') == "1":
            ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=data['devpower_id'],dkey_comment=data['devpower_comment'],dkey_value1=self.request.POST.get('devpower_val1'),dkey_value2=None,dkey_value3=None,dkey_rank=0)
            ddockeyw.save()
        if self.request.POST.get('devwaste') == "1":
            ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=data['devwaste_id'],dkey_comment=data['devwaste_comment'],dkey_value1=None,dkey_value2=None,dkey_value3=None,dkey_rank=0)
            ddockeyw.save()

        dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc.pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1002).delete()
        
        for i in data['issues']:
            if i.keyw_pk == 2034:
                idockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=i,dkey_comment=data['dkey_comment_issues'],dkey_rank=0)
            else:
                idockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=i,dkey_rank=0)
            idockeyw.save()

        docreviews.objects.filter(drag_doc_fk=doc.pk).delete()

        for ra in data['ragencies']:
            docrev = docreviews(drag_doc_fk=doc,drag_rag_fk=ra,drag_rank=0,drag_copies=1)
            docrev.save()

        return super(docedit_noc,self).form_valid(form)

class docedit_nod(FormView):
    form_class = editnodform
    template_name="ceqanet/docedit_nod.html"

    def get_success_url(self):
        success_url = reverse_lazy('docdesp_nod', args=[self.request.POST.get('doc_pk')])
        return success_url
    
    def get_initial(self):
        initial = super(docedit_nod, self).get_initial()

        docinfo = documents.objects.get(pk=self.request.GET.get('doc_pk'))
        latlonginfo = latlongs.objects.filter(doc_pk=self.request.GET.get('doc_pk'))

        initial['prj_title'] = docinfo.doc_prj_fk.prj_title
        initial['prj_description'] = docinfo.doc_prj_fk.prj_description
        initial['doc_conagency'] = docinfo.doc_conagency
        initial['doc_conname'] = docinfo.doc_conname
        initial['doc_conemail'] = docinfo.doc_conemail
        initial['doc_conphone'] = docinfo.doc_conphone
        initial['doc_conaddress1'] = docinfo.doc_conaddress1
        initial['doc_conaddress2'] = docinfo.doc_conaddress2
        initial['doc_concity'] = docinfo.doc_concity
        initial['doc_constate'] = docinfo.doc_constate
        initial['doc_conzip'] = docinfo.doc_conzip.strip
        initial['doc_location'] = docinfo.doc_location
        if latlonginfo.exists():
            initial['doc_latitude'] = latlonginfo[0].doc_latitude
            initial['doc_longitude'] = latlonginfo[0].doc_longitude

        if docinfo.doc_city != None:
            cityinfo = geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).filter(geow_shortname__startswith=docinfo.doc_city)
            if cityinfo.count() == 1:
                initial['doc_city'] = cityinfo[0].geow_pk

        if docinfo.doc_county != None:
            countyinfo = geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).filter(geow_shortname__startswith=docinfo.doc_county)
            if countyinfo.count() == 1:
                initial['doc_county'] = countyinfo[0].geow_pk

        initial['doc_nodbylead'] = docinfo.doc_nodbylead
        initial['doc_nodbyresp'] = docinfo.doc_nodbyresp
        initial['doc_nodagency'] = docinfo.doc_nodagency
        initial['doc_nod'] = docinfo.doc_nod
        initial['doc_detsigeffect'] = docinfo.doc_detsigeffect
        initial['doc_detnotsigeffect'] = docinfo.doc_detnotsigeffect
        initial['doc_deteir'] = docinfo.doc_deteir
        initial['doc_detnegdec'] = docinfo.doc_detnegdec
        initial['doc_detmitigation'] = docinfo.doc_detmitigation
        initial['doc_detnotmitigation'] = docinfo.doc_detnotmitigation
        initial['doc_detconsider'] = docinfo.doc_detconsider
        initial['doc_detnotconsider'] = docinfo.doc_detnotconsider
        initial['doc_detfindings'] = docinfo.doc_detfindings
        initial['doc_detnotfindings'] = docinfo.doc_detnotfindings
        initial['doc_eiravailableat'] = docinfo.doc_eiravailableat

        return initial

    def get_context_data(self, **kwargs):
        context = super(docedit_nod, self).get_context_data(**kwargs)
        context['doc_pk'] = self.request.GET.get('doc_pk')

        return context

    def form_valid(self,form):
        data = form.cleaned_data
        doc = documents.objects.get(pk=self.request.POST.get('doc_pk'))
        prj = projects.objects.get(pk=doc.doc_prj_fk.prj_pk)

        if data['doc_city'] != None:
            cityname = geowords.objects.get(pk=data['doc_city'].pk)
        else:
            cityname = None
        if data['doc_county'] != None:
            countyname = geowords.objects.get(pk=data['doc_county'].pk)
        else:
            countyname = None

        doc.doc_conagency = data['doc_conagency']
        doc.doc_conname = data['doc_conname']
        doc.doc_conemail = data['doc_conemail']
        doc.doc_conphone = data['doc_conphone']
        doc.doc_conaddress1 = data['doc_conaddress1']
        doc.doc_conaddress2 = data['doc_conaddress2']
        doc.doc_concity = data['doc_concity']
        doc.doc_constate = data['doc_constate']
        doc.doc_conzip = data['doc_conzip']
        doc.doc_location = data['doc_location']
        if data['doc_city'] != None:
            doc.doc_city = cityname.geow_shortname
        else:
            doc.doc_city = ''
        if data['doc_county'] != None:
            doc.doc_county = countyname.geow_shortname
        else:
            doc.doc_county = ''
        doc.doc_nodbylead = data['doc_nodbylead']
        doc.doc_nodbyresp = data['doc_nodbyresp']
        doc.doc_nodagency = data['doc_nodagency']
        doc.doc_nod = data['doc_nod']
        doc.doc_detsigeffect = data['doc_detsigeffect']
        doc.doc_detnotsigeffect = data['doc_detnotsigeffect']
        doc.doc_deteir = data['doc_deteir']
        doc.doc_detnegdec = data['doc_detnegdec']
        doc.doc_detmitigation = data['doc_detmitigation']
        doc.doc_detnotmitigation = data['doc_detnotmitigation']
        doc.doc_detconsider = data['doc_detconsider']
        doc.doc_detnotconsider = data['doc_detnotconsider']
        doc.doc_detfindings = data['doc_detfindings']
        doc.doc_detnotfindings = data['doc_detnotfindings']
        doc.doc_eiravailableat = data['doc_eiravailableat']
        doc.save()
        prj.prj_title = data['prj_title']
        prj.prj_description = data['prj_description']
        prj.save()

        try:
            coords = latlongs.objects.get(pk=doc.pk)
            coords.doc_latitude = data['doc_latitude']
            coords.doc_longitude = data['doc_longitude']
        except latlongs.DoesNotExist:
            coords = latlongs(doc_pk=doc.pk,doc_prj_fk=prj,doc_doctype="NOD",doc_latitude=data['doc_latitude'],doc_longitude=data['doc_longitude'])
        coords.save()

        return super(docedit_nod,self).form_valid(form)

class docedit_noe(FormView):
    form_class = editnoeform
    template_name="ceqanet/docedit_noe.html"

    def get_success_url(self):
        success_url = reverse_lazy('docdesp_noe', args=[self.request.POST.get('doc_pk')])
        return success_url
    
    def get_initial(self):
        initial = super(docedit_noe, self).get_initial()

        docinfo = documents.objects.get(pk=self.request.GET.get('doc_pk'))
        latlonginfo = latlongs.objects.filter(doc_pk=self.request.GET.get('doc_pk'))

        initial['prj_title'] = docinfo.doc_prj_fk.prj_title
        initial['prj_description'] = docinfo.doc_prj_fk.prj_description
        initial['doc_conagency'] = docinfo.doc_conagency
        initial['doc_conname'] = docinfo.doc_conname
        initial['doc_conemail'] = docinfo.doc_conemail
        initial['doc_conphone'] = docinfo.doc_conphone
        initial['doc_conaddress1'] = docinfo.doc_conaddress1
        initial['doc_conaddress2'] = docinfo.doc_conaddress2
        initial['doc_concity'] = docinfo.doc_concity
        initial['doc_constate'] = docinfo.doc_constate
        initial['doc_conzip'] = docinfo.doc_conzip.strip
        initial['doc_location'] = docinfo.doc_location
        if latlonginfo.exists():
            initial['doc_latitude'] = latlonginfo[0].doc_latitude
            initial['doc_longitude'] = latlonginfo[0].doc_longitude

        if docinfo.doc_city != None:
            cityinfo = geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).filter(geow_shortname__startswith=docinfo.doc_city)
            if cityinfo.count() == 1:
                initial['doc_city'] = cityinfo[0].geow_pk

        if docinfo.doc_county != None:
            countyinfo = geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).filter(geow_shortname__startswith=docinfo.doc_county)
            if countyinfo.count() == 1:
                initial['doc_county'] = countyinfo[0].geow_pk

        if docinfo.doc_exministerial:
            initial['rdoexemptstatus'] = 1
        elif docinfo.doc_exdeclared:
            initial['rdoexemptstatus'] = 2
        elif docinfo.doc_exemergency:
            initial['rdoexemptstatus'] = 3
        elif docinfo.doc_excategorical:
            initial['rdoexemptstatus'] = 4
            initial['strsectionnumber'] = docinfo.doc_exnumber
        elif docinfo.doc_exstatutory:
            initial['rdoexemptstatus'] = 5
            initial['strcodenumber'] = docinfo.doc_exnumber

        initial['doc_exreasons'] = docinfo.doc_exreasons

        return initial

    def get_context_data(self, **kwargs):
        context = super(docedit_noe, self).get_context_data(**kwargs)
        context['doc_pk'] = self.request.GET.get('doc_pk')

        return context

    def form_valid(self,form):
        data = form.cleaned_data
        doc = documents.objects.get(pk=self.request.POST.get('doc_pk'))
        prj = projects.objects.get(pk=doc.doc_prj_fk.prj_pk)

        if data['doc_city'] != None:
            cityname = geowords.objects.get(pk=data['doc_city'].pk)
        else:
            cityname = None
        if data['doc_county'] != None:
            countyname = geowords.objects.get(pk=data['doc_county'].pk)
        else:
            countyname = None
            
        doc_exministerial = False
        doc_exdeclared = False
        doc_exemergency = False
        doc_excategorical = False
        doc_exstatutory = False
        doc_exnumber = ''

        rdoexemptstatus = data['rdoexemptstatus']
        if rdoexemptstatus == '1':
            doc_exministerial = True
        elif rdoexemptstatus == '2':
            doc_exdeclared = True
        elif rdoexemptstatus == '3':
            doc_exemergency = True
        elif rdoexemptstatus == '4':
            doc_excategorical = True
            doc_exnumber = data['strsectionnumber']
        elif rdoexemptstatus == '5':
            doc_exstatutory = True
            doc_exnumber = data['strcodenumber']

        doc.doc_conagency = data['doc_conagency']
        doc.doc_conname = data['doc_conname']
        doc.doc_conemail = data['doc_conemail']
        doc.doc_conphone = data['doc_conphone']
        doc.doc_conaddress1 = data['doc_conaddress1']
        doc.doc_conaddress2 = data['doc_conaddress2']
        doc.doc_concity = data['doc_concity']
        doc.doc_constate = data['doc_constate']
        doc.doc_conzip = data['doc_conzip']
        doc.doc_location = data['doc_location']
        if data['doc_city'] != None:
            doc.doc_city = cityname.geow_shortname
        else:
            doc.doc_city = ''
        if data['doc_county'] != None:
            doc.doc_county = countyname.geow_shortname
        else:
            doc.doc_county = ''
        doc.doc_exministerial = doc_exministerial
        doc.doc_exdeclared = doc_exdeclared
        doc.doc_exemergency = doc_exemergency
        doc.doc_excategorical = doc_excategorical
        doc.doc_exstatutory = doc_exstatutory
        doc.doc_exnumber = doc_exnumber
        doc.doc_exreasons = data['doc_exreasons']
        doc.save()
        prj.prj_title = data['prj_title']
        prj.prj_description = data['prj_description']
        prj.save()

        try:
            coords = latlongs.objects.get(pk=doc.pk)
            coords.doc_latitude = data['doc_latitude']
            coords.doc_longitude = data['doc_longitude']
        except latlongs.DoesNotExist:
            coords = latlongs(doc_pk=doc.pk,doc_prj_fk=prj,doc_doctype="NOE",doc_latitude=data['doc_latitude'],doc_longitude=data['doc_longitude'])
        coords.save()

        return super(docedit_noe,self).form_valid(form)

class docedit_nop(FormView):
    form_class = editnopform
    template_name="ceqanet/docedit_nop.html"

    def get_success_url(self):
        success_url = reverse_lazy('docdesp_nop', args=[self.request.POST.get('doc_pk')])
        return success_url
    
    def get_initial(self):
        initial = super(docedit_nop, self).get_initial()

        docinfo = documents.objects.get(pk=self.request.GET.get('doc_pk'))
        latlonginfo = latlongs.objects.filter(doc_pk=self.request.GET.get('doc_pk'))
        devinfo = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1010)
        dkey_comment_actions = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_pk=1018)
        dkey_comment_dev = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_pk=11001)
        dkey_comment_issues = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_pk=2034)
        
        initial['prj_title'] = docinfo.doc_prj_fk.prj_title
        initial['prj_description'] = docinfo.doc_prj_fk.prj_description
        initial['doc_conagency'] = docinfo.doc_conagency
        initial['doc_conname'] = docinfo.doc_conname
        initial['doc_conemail'] = docinfo.doc_conemail
        initial['doc_conphone'] = docinfo.doc_conphone
        initial['doc_conaddress1'] = docinfo.doc_conaddress1
        initial['doc_conaddress2'] = docinfo.doc_conaddress2
        initial['doc_concity'] = docinfo.doc_concity
        initial['doc_constate'] = docinfo.doc_constate
        initial['doc_conzip'] = docinfo.doc_conzip.strip
        initial['doc_location'] = docinfo.doc_location
        if latlonginfo.exists():
            initial['doc_latitude'] = latlonginfo[0].doc_latitude
            initial['doc_longitude'] = latlonginfo[0].doc_longitude

        if docinfo.doc_city != None:
            cityinfo = geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).filter(geow_shortname__startswith=docinfo.doc_city)
            if cityinfo.count() == 1:
                initial['doc_city'] = cityinfo[0].geow_pk

        if docinfo.doc_county != None:
            countyinfo = geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).filter(geow_shortname__startswith=docinfo.doc_county)
            if countyinfo.count() == 1:
                initial['doc_county'] = countyinfo[0].geow_pk

        initial['doc_parcelno'] = docinfo.doc_parcelno
        initial['doc_xstreets'] = docinfo.doc_xstreets
        initial['doc_township'] = docinfo.doc_township
        initial['doc_range'] = docinfo.doc_range
        initial['doc_section'] = docinfo.doc_section
        initial['doc_base'] = docinfo.doc_base
        initial['doc_highways'] = docinfo.doc_highways
        initial['doc_railways'] = docinfo.doc_railways
        initial['doc_airports'] = docinfo.doc_airports
        initial['doc_schools'] = docinfo.doc_schools
        initial['doc_waterways'] = docinfo.doc_waterways
        initial['doc_parcelno'] = docinfo.doc_parcelno
        initial['doc_landuse'] = docinfo.doc_landuse

        if dkey_comment_actions.exists():
            initial['dkey_comment_actions'] = dkey_comment_actions[0].dkey_comment
        if dkey_comment_dev.exists():
            initial['dkey_comment_dev'] = dkey_comment_dev[0].dkey_comment
        if dkey_comment_issues.exists():
            initial['dkey_comment_issues'] = dkey_comment_issues[0].dkey_comment

        for dev in devinfo:
            if dev.dkey_keyw_fk.keyw_pk > 4000:
                if dev.dkey_keyw_fk.keyw_pk < 5000:
                    initial['devtrans_id'] = dev.dkey_keyw_fk.keyw_pk
                    initial['devtrans_comment'] = dev.dkey_comment
            if dev.dkey_keyw_fk.keyw_pk > 3000:
                if dev.dkey_keyw_fk.keyw_pk < 4000:
                    initial['devpower_id'] = dev.dkey_keyw_fk.keyw_pk
                    initial['devpower_comment'] = dev.dkey_comment
            if dev.dkey_keyw_fk.keyw_pk == 6001:
                initial['dev6001_val1'] = dev.dkey_value1
                initial['dev6001_val2'] = dev.dkey_value2
            elif dev.dkey_keyw_fk.keyw_pk == 6002:
                initial['dev6002_val1'] = dev.dkey_value1
                initial['dev6002_val2'] = dev.dkey_value2
                initial['dev6002_val3'] = dev.dkey_value3
            elif dev.dkey_keyw_fk.keyw_pk == 6003:
                initial['dev6003_val1'] = dev.dkey_value1
                initial['dev6003_val2'] = dev.dkey_value2
                initial['dev6003_val3'] = dev.dkey_value3
            elif dev.dkey_keyw_fk.keyw_pk == 6004:
                initial['dev6004_val1'] = dev.dkey_value1
                initial['dev6004_val2'] = dev.dkey_value2
                initial['dev6004_val3'] = dev.dkey_value3
            elif dev.dkey_keyw_fk.keyw_pk == 7001:
                initial['dev7001_val1'] = dev.dkey_value1
            elif dev.dkey_keyw_fk.keyw_pk == 8001:
                initial['dev8001_val1'] = dev.dkey_value1
            elif dev.dkey_keyw_fk.keyw_pk == 9001:
                initial['dev9001_val1'] = dev.dkey_value1
            elif dev.dkey_keyw_fk.keyw_pk == 10001:
                initial['dev10001_val1'] = dev.dkey_value1

        return initial

    def get_context_data(self, **kwargs):
        context = super(docedit_nop, self).get_context_data(**kwargs)
        context['doc_pk'] = self.request.GET.get('doc_pk')
        context['lats'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1001)
        context['devs'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1010)
        context['isss'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1002)

        return context

    def form_valid(self,form):
        data = form.cleaned_data
        doc = documents.objects.get(pk=self.request.POST.get('doc_pk'))
        prj = projects.objects.get(pk=doc.doc_prj_fk.prj_pk)

        if data['doc_city'] != None:
            cityname = geowords.objects.get(pk=data['doc_city'].pk)
        else:
            cityname = None
        if data['doc_county'] != None:
            countyname = geowords.objects.get(pk=data['doc_county'].pk)
        else:
            countyname = None

        if data['doc_conaddress2'] == '':
            doc_conaddress2 = None
        else:
            doc_conaddress2 = data['doc_conaddress2']
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

        doc.doc_conagency = data['doc_conagency']
        doc.doc_conname = data['doc_conname']
        doc.doc_conemail = data['doc_conemail']
        doc.doc_conphone = data['doc_conphone']
        doc.doc_conaddress1 = data['doc_conaddress1']
        doc.doc_conaddress2 = doc_conaddress2
        doc.doc_concity = data['doc_concity']
        doc.doc_constate = data['doc_constate']
        doc.doc_conzip = data['doc_conzip']
        doc.doc_location = data['doc_location']
        if data['doc_city'] != None:
            doc.doc_city = cityname.geow_shortname
        else:
            doc.doc_city = ''
        if data['doc_county'] != None:
            doc.doc_county = countyname.geow_shortname
        else:
            doc.doc_county = ''
        doc.doc_parcelno = doc_parcelno
        doc.doc_xstreets = doc_xstreets
        doc.doc_township = doc_township
        doc.doc_range = doc_range
        doc.doc_section = doc_section
        doc.doc_base = doc.doc_base
        doc.doc_highways = doc_highways
        doc.doc_airports = doc_airports
        doc.doc_railways = doc_railways
        doc.doc_waterways = doc_waterways
        doc.doc_landuse = doc_landuse
        doc.doc_schools = doc_schools
        doc.save()
        prj.prj_title = data['prj_title']
        prj.prj_description = data['prj_description']
        prj.save()

        try:
            coords = latlongs.objects.get(pk=doc.pk)
            coords.doc_latitude = data['doc_latitude']
            coords.doc_longitude = data['doc_longitude']
        except latlongs.DoesNotExist:
            coords = latlongs(doc_pk=doc.pk,doc_prj_fk=prj,doc_doctype="NOP",doc_latitude=data['doc_latitude'],doc_longitude=data['doc_longitude'])
        coords.save()

        dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc.pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1001).delete()

        for a in data['actions']:
            if a.keyw_pk == 1018:
                adockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=a,dkey_comment=data['dkey_comment_actions'],dkey_rank=0)
            else:
                adockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=a,dkey_rank=0)
            adockeyw.save()
        
        dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc.pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1010).delete()

        devtypes = keywords.objects.filter(keyw_keyl_fk__keyl_pk=1010)
        for d in devtypes:
            if self.request.POST.get('dev'+str(d.keyw_pk)) == "1":
                if d.keyw_pk == 11001:
                    ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=d,dkey_comment=data['dkey_comment_dev'],dkey_value1=self.request.POST.get('dev'+str(d.keyw_pk)+'_val1'),dkey_value2=self.request.POST.get('dev'+str(d.keyw_pk)+'_val2'),dkey_value3=self.request.POST.get('dev'+str(d.keyw_pk)+'_val3'),dkey_rank=0)
                else:
                    ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=d,dkey_value1=self.request.POST.get('dev'+str(d.keyw_pk)+'_val1'),dkey_value2=self.request.POST.get('dev'+str(d.keyw_pk)+'_val2'),dkey_value3=self.request.POST.get('dev'+str(d.keyw_pk)+'_val3'),dkey_rank=0)
                ddockeyw.save()
        if self.request.POST.get('devtrans') == "1":
            ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=data['devtrans_id'],dkey_comment=data['devtrans_comment'],dkey_value1=None,dkey_value2=None,dkey_value3=None,dkey_rank=0)
            ddockeyw.save()
        if self.request.POST.get('devpower') == "1":
            ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=data['devpower_id'],dkey_comment=data['devpower_comment'],dkey_value1=self.request.POST.get('devpower_val1'),dkey_value2=None,dkey_value3=None,dkey_rank=0)
            ddockeyw.save()
        if self.request.POST.get('devwaste') == "1":
            ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=data['devwaste_id'],dkey_comment=data['devwaste_comment'],dkey_value1=None,dkey_value2=None,dkey_value3=None,dkey_rank=0)
            ddockeyw.save()

        dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc.pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1002).delete()
        
        for i in data['issues']:
            if i.keyw_pk == 2034:
                idockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=i,dkey_comment=data['dkey_comment_issues'],dkey_rank=0)
            else:
                idockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=i,dkey_rank=0)
            idockeyw.save()

        docreviews.objects.filter(drag_doc_fk=doc.pk).delete()

        for ra in data['ragencies']:
            docrev = docreviews(drag_doc_fk=doc,drag_rag_fk=ra,drag_rank=0,drag_copies=1)
            docrev.save()

        return super(docedit_nop,self).form_valid(form)

class pending(ListView):
    template_name="ceqanet/pending.html"
    context_object_name = "pendings"
    paginate_by = 25

    def get_queryset(self):
        queryset = PendingListQuery(self.request)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(pending, self).get_context_data(**kwargs)

        qsminuspage = self.request.GET.copy()
        
        if "page" in qsminuspage:
            qsminuspage.pop('page')

        context['restofqs'] = qsminuspage.urlencode()

        return context

def PendingListQuery(request):
    queryset = documents.objects.filter(doc_pending=True).order_by('-doc_received')
    return queryset

class pendingdetail_noc(FormView):
    form_class = pendingdetailnocform
    template_name="ceqanet/pendingdetail_noc.html"
 
    def get_success_url(self):
        success_url = "%s" % reverse_lazy('pending')
        return success_url

    def get_initial(self):
        initial = super(pendingdetail_noc, self).get_initial()

        docinfo = documents.objects.get(pk=self.request.GET.get('doc_pk'))
        latlonginfo = latlongs.objects.filter(doc_pk=self.request.GET.get('doc_pk'))
        latinfo = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1001)
        devinfo = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1010)
        issinfo= dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1002)
        raginfo = docreviews.objects.only('drag_rag_fk__rag_pk').filter(drag_doc_fk__doc_pk=self.request.GET.get('doc_pk'))
        dkey_comment_actions = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_pk=1018)
        dkey_comment_dev = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_pk=11001)
        dkey_comment_issues = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_pk=2034)
        
        initial['prj_title'] = docinfo.doc_prj_fk.prj_title
        initial['prj_description'] = docinfo.doc_prj_fk.prj_description
        initial['doc_conagency'] = docinfo.doc_conagency
        initial['doc_conname'] = docinfo.doc_conname
        initial['doc_conemail'] = docinfo.doc_conemail
        initial['doc_conphone'] = docinfo.doc_conphone
        initial['doc_conaddress1'] = docinfo.doc_conaddress1
        initial['doc_conaddress2'] = docinfo.doc_conaddress2
        initial['doc_concity'] = docinfo.doc_concity
        initial['doc_constate'] = docinfo.doc_constate
        initial['doc_conzip'] = docinfo.doc_conzip.strip
        initial['doc_location'] = docinfo.doc_location
        if latlonginfo.exists():
            initial['doc_latitude'] = latlonginfo[0].doc_latitude
            initial['doc_longitude'] = latlonginfo[0].doc_longitude

        if docinfo.doc_city != None:
            cityinfo = geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).filter(geow_shortname__startswith=docinfo.doc_city)
            if cityinfo.count() == 1:
                initial['doc_city'] = cityinfo[0].geow_pk

        if docinfo.doc_county != None:
            countyinfo = geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).filter(geow_shortname__startswith=docinfo.doc_county)
            if countyinfo.count() == 1:
                initial['doc_county'] = countyinfo[0].geow_pk

        initial['doc_parcelno'] = docinfo.doc_parcelno
        initial['doc_xstreets'] = docinfo.doc_xstreets
        initial['doc_township'] = docinfo.doc_township
        initial['doc_range'] = docinfo.doc_range
        initial['doc_section'] = docinfo.doc_section
        initial['doc_base'] = docinfo.doc_base
        initial['doc_highways'] = docinfo.doc_highways
        initial['doc_railways'] = docinfo.doc_railways
        initial['doc_airports'] = docinfo.doc_airports
        initial['doc_schools'] = docinfo.doc_schools
        initial['doc_waterways'] = docinfo.doc_waterways
        initial['doc_parcelno'] = docinfo.doc_parcelno
        initial['doc_landuse'] = docinfo.doc_landuse

        initial['doctypeid'] = docinfo.doc_doct_fk.keyw_pk
        if dkey_comment_actions.exists():
            initial['dkey_comment_actions'] = dkey_comment_actions[0].dkey_comment
        if dkey_comment_dev.exists():
            initial['dkey_comment_dev'] = dkey_comment_dev[0].dkey_comment
        if dkey_comment_issues.exists():
            initial['dkey_comment_issues'] = dkey_comment_issues[0].dkey_comment

        if latinfo.exists():
            initial['actions'] = latinfo

        for dev in devinfo:
            if dev.dkey_keyw_fk.keyw_pk > 4000:
                if dev.dkey_keyw_fk.keyw_pk < 5000:
                    initial['devtrans_id'] = dev.dkey_keyw_fk.keyw_pk
                    initial['devtrans_comment'] = dev.dkey_comment
            if dev.dkey_keyw_fk.keyw_pk > 3000:
                if dev.dkey_keyw_fk.keyw_pk < 4000:
                    initial['devpower_id'] = dev.dkey_keyw_fk.keyw_pk
                    initial['devpower_comment'] = dev.dkey_comment
            if dev.dkey_keyw_fk.keyw_pk == 6001:
                initial['dev6001_val1'] = dev.dkey_value1
                initial['dev6001_val2'] = dev.dkey_value2
            elif dev.dkey_keyw_fk.keyw_pk == 6002:
                initial['dev6002_val1'] = dev.dkey_value1
                initial['dev6002_val2'] = dev.dkey_value2
                initial['dev6002_val3'] = dev.dkey_value3
            elif dev.dkey_keyw_fk.keyw_pk == 6003:
                initial['dev6003_val1'] = dev.dkey_value1
                initial['dev6003_val2'] = dev.dkey_value2
                initial['dev6003_val3'] = dev.dkey_value3
            elif dev.dkey_keyw_fk.keyw_pk == 6004:
                initial['dev6004_val1'] = dev.dkey_value1
                initial['dev6004_val2'] = dev.dkey_value2
                initial['dev6004_val3'] = dev.dkey_value3
            elif dev.dkey_keyw_fk.keyw_pk == 7001:
                initial['dev7001_val1'] = dev.dkey_value1
            elif dev.dkey_keyw_fk.keyw_pk == 8001:
                initial['dev8001_val1'] = dev.dkey_value1
            elif dev.dkey_keyw_fk.keyw_pk == 9001:
                initial['dev9001_val1'] = dev.dkey_value1
            elif dev.dkey_keyw_fk.keyw_pk == 10001:
                initial['dev10001_val1'] = dev.dkey_value1

        if issinfo.exists():
            initial['issues'] = issinfo

        if raginfo.exists():
            initial['ragencies'] = raginfo

        return initial

    def get_context_data(self, **kwargs):
        context = super(pendingdetail_noc, self).get_context_data(**kwargs)
        context['doc_pk'] = self.request.GET.get('doc_pk')
        context['lats'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1001)
        context['devs'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1010)
        context['isss'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1002)

        return context

    def form_valid(self,form):
        data = form.cleaned_data
        doc = documents.objects.get(pk=self.request.POST.get('doc_pk'))
        prj = projects.objects.get(pk=doc.doc_prj_fk.prj_pk)

        if data['doc_city'] != None:
            cityname = geowords.objects.get(pk=data['doc_city'].pk)
        else:
            cityname = None
        if data['doc_county'] != None:
            countyname = geowords.objects.get(pk=data['doc_county'].pk)
        else:
            countyname = None

        if data['doc_conaddress2'] == '':
            doc_conaddress2 = None
        else:
            doc_conaddress2 = data['doc_conaddress2']
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

        doc.doc_conagency = data['doc_conagency']
        doc.doc_conname = data['doc_conname']
        doc.doc_conemail = data['doc_conemail']
        doc.doc_conphone = data['doc_conphone']
        doc.doc_conaddress1 = data['doc_conaddress1']
        doc.doc_conaddress2 = doc_conaddress2
        doc.doc_concity = data['doc_concity']
        doc.doc_constate = data['doc_constate']
        doc.doc_conzip = data['doc_conzip']
        doc.doc_location = data['doc_location']
        if data['doc_city'] != None:
            doc.doc_city = cityname.geow_shortname
        else:
            doc.doc_city = ''
        if data['doc_county'] != None:
            doc.doc_county = countyname.geow_shortname
        else:
            doc.doc_county = ''
        doc.doc_parcelno = doc_parcelno
        doc.doc_xstreets = doc_xstreets
        doc.doc_township = doc_township
        doc.doc_range = doc_range
        doc.doc_section = doc_section
        doc.doc_base = doc.doc_base
        doc.doc_highways = doc_highways
        doc.doc_airports = doc_airports
        doc.doc_railways = doc_railways
        doc.doc_waterways = doc_waterways
        doc.doc_landuse = doc_landuse
        doc.doc_schools = doc_schools
        doc.doc_doct_fk = data['doctypeid']
        doc.doc_doctype = data['doctypeid'].keyw_shortname
        doc.doc_docname = data['doctypeid'].keyw_longname
        doc.doc_pending = False
        doc.doc_plannerreview = True
        doc.doc_plannerregion = self.request.POST.get('doc_plannerregion')
        doc.save()
        prj.prj_title = data['prj_title']
        prj.prj_description = data['prj_description']
        if prj.prj_pending:
            prj.prj_pending = False
            prj.prj_plannerreview = True
        prj.save()

        try:
            coords = latlongs.objects.get(pk=doc.pk)
            coords.doc_latitude = data['doc_latitude']
            coords.doc_longitude = data['doc_longitude']
        except latlongs.DoesNotExist:
            coords = latlongs(doc_pk=doc.pk,doc_prj_fk=prj,doc_doctype="NOC",doc_latitude=data['doc_latitude'],doc_longitude=data['doc_longitude'])
        coords.save()

        dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc.pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1001).delete()

        for a in data['actions']:
            if a.keyw_pk == 1018:
                adockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=a,dkey_comment=data['dkey_comment_actions'],dkey_rank=0)
            else:
                adockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=a,dkey_rank=0)
            adockeyw.save()
        
        dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc.pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1010).delete()

        devtypes = keywords.objects.filter(keyw_keyl_fk__keyl_pk=1010)
        for d in devtypes:
            if self.request.POST.get('dev'+str(d.keyw_pk)) == "1":
                if d.keyw_pk == 11001:
                    ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=d,dkey_comment=data['dkey_comment_dev'],dkey_value1=self.request.POST.get('dev'+str(d.keyw_pk)+'_val1'),dkey_value2=self.request.POST.get('dev'+str(d.keyw_pk)+'_val2'),dkey_value3=self.request.POST.get('dev'+str(d.keyw_pk)+'_val3'),dkey_rank=0)
                else:
                    ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=d,dkey_value1=self.request.POST.get('dev'+str(d.keyw_pk)+'_val1'),dkey_value2=self.request.POST.get('dev'+str(d.keyw_pk)+'_val2'),dkey_value3=self.request.POST.get('dev'+str(d.keyw_pk)+'_val3'),dkey_rank=0)
                ddockeyw.save()
        if self.request.POST.get('devtrans') == "1":
            ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=data['devtrans_id'],dkey_comment=data['devtrans_comment'],dkey_value1=None,dkey_value2=None,dkey_value3=None,dkey_rank=0)
            ddockeyw.save()
        if self.request.POST.get('devpower') == "1":
            ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=data['devpower_id'],dkey_comment=data['devpower_comment'],dkey_value1=self.request.POST.get('devpower_val1'),dkey_value2=None,dkey_value3=None,dkey_rank=0)
            ddockeyw.save()
        if self.request.POST.get('devwaste') == "1":
            ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=data['devwaste_id'],dkey_comment=data['devwaste_comment'],dkey_value1=None,dkey_value2=None,dkey_value3=None,dkey_rank=0)
            ddockeyw.save()

        dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc.pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1002).delete()
        
        for i in data['issues']:
            if i.keyw_pk == 2034:
                idockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=i,dkey_comment=data['dkey_comment_issues'],dkey_rank=0)
            else:
                idockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=i,dkey_rank=0)
            idockeyw.save()

        docreviews.objects.filter(drag_doc_fk=doc.pk).delete()

        for ra in data['ragencies']:
            docrev = docreviews(drag_doc_fk=doc,drag_rag_fk=ra,drag_rank=0,drag_copies=1)
            docrev.save()

        return super(pendingdetail_noc,self).form_valid(form)

class pendingdetail_nod(FormView):
    form_class = pendingdetailnodform
    template_name="ceqanet/pendingdetail_nod.html"

    def get_success_url(self):
        success_url = "%s" % reverse_lazy('pending')
        return success_url

    def get_initial(self):
        initial = super(pendingdetail_nod, self).get_initial()

        docinfo = documents.objects.get(pk=self.request.GET.get('doc_pk'))
        latlonginfo = latlongs.objects.filter(doc_pk=self.request.GET.get('doc_pk'))

        initial['prj_title'] = docinfo.doc_prj_fk.prj_title
        initial['prj_description'] = docinfo.doc_prj_fk.prj_description
        initial['doc_conagency'] = docinfo.doc_conagency
        initial['doc_conname'] = docinfo.doc_conname
        initial['doc_conemail'] = docinfo.doc_conemail
        initial['doc_conphone'] = docinfo.doc_conphone
        initial['doc_conaddress1'] = docinfo.doc_conaddress1
        initial['doc_conaddress2'] = docinfo.doc_conaddress2
        initial['doc_concity'] = docinfo.doc_concity
        initial['doc_constate'] = docinfo.doc_constate
        initial['doc_conzip'] = docinfo.doc_conzip.strip
        initial['doc_location'] = docinfo.doc_location
        if latlonginfo.exists():
            initial['doc_latitude'] = latlonginfo[0].doc_latitude
            initial['doc_longitude'] = latlonginfo[0].doc_longitude

        if docinfo.doc_city != None:
            cityinfo = geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).filter(geow_shortname__startswith=docinfo.doc_city)
            if cityinfo.count() == 1:
                initial['doc_city'] = cityinfo[0].geow_pk

        if docinfo.doc_county != None:
            countyinfo = geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).filter(geow_shortname__startswith=docinfo.doc_county)
            if countyinfo.count() == 1:
                initial['doc_county'] = countyinfo[0].geow_pk

        initial['doc_nodbylead'] = docinfo.doc_nodbylead
        initial['doc_nodbyresp'] = docinfo.doc_nodbyresp
        initial['doc_nodagency'] = docinfo.doc_nodagency
        initial['doc_nod'] = docinfo.doc_nod
        initial['doc_detsigeffect'] = docinfo.doc_detsigeffect
        initial['doc_detnotsigeffect'] = docinfo.doc_detnotsigeffect
        initial['doc_deteir'] = docinfo.doc_deteir
        initial['doc_detnegdec'] = docinfo.doc_detnegdec
        initial['doc_detmitigation'] = docinfo.doc_detmitigation
        initial['doc_detnotmitigation'] = docinfo.doc_detnotmitigation
        initial['doc_detconsider'] = docinfo.doc_detconsider
        initial['doc_detnotconsider'] = docinfo.doc_detnotconsider
        initial['doc_detfindings'] = docinfo.doc_detfindings
        initial['doc_detnotfindings'] = docinfo.doc_detnotfindings
        initial['doc_eiravailableat'] = docinfo.doc_eiravailableat

        return initial

    def get_context_data(self, **kwargs):
        context = super(pendingdetail_nod, self).get_context_data(**kwargs)

        context['doc_pk'] = self.request.GET.get('doc_pk')

        return context

    def form_valid(self,form):
        data = form.cleaned_data

        doc = documents.objects.get(pk=self.request.POST.get('doc_pk'))
        prj = projects.objects.get(pk=doc.doc_prj_fk.prj_pk)

        if data['doc_city'] != None:
            cityname = geowords.objects.get(pk=data['doc_city'].pk)
        else:
            cityname = None
        if data['doc_county'] != None:
            countyname = geowords.objects.get(pk=data['doc_county'].pk)
        else:
            countyname = None

        doc.doc_conagency = data['doc_conagency']
        doc.doc_conname = data['doc_conname']
        doc.doc_conemail = data['doc_conemail']
        doc.doc_conphone = data['doc_conphone']
        doc.doc_conaddress1 = data['doc_conaddress1']
        doc.doc_conaddress2 = data['doc_conaddress2']
        doc.doc_concity = data['doc_concity']
        doc.doc_constate = data['doc_constate']
        doc.doc_conzip = data['doc_conzip']
        doc.doc_location = data['doc_location']
        if data['doc_city'] != None:
            doc.doc_city = cityname.geow_shortname
        else:
            doc.doc_city = ''
        if data['doc_county'] != None:
            doc.doc_county = countyname.geow_shortname
        else:
            doc.doc_county = ''
        doc.doc_nodbylead = data['doc_nodbylead']
        doc.doc_nodbyresp = data['doc_nodbyresp']
        doc.doc_nodagency = data['doc_nodagency']
        doc.doc_nod = data['doc_nod']
        doc.doc_detsigeffect = data['doc_detsigeffect']
        doc.doc_detnotsigeffect = data['doc_detnotsigeffect']
        doc.doc_deteir = data['doc_deteir']
        doc.doc_detnegdec = data['doc_detnegdec']
        doc.doc_detmitigation = data['doc_detmitigation']
        doc.doc_detnotmitigation = data['doc_detnotmitigation']
        doc.doc_detconsider = data['doc_detconsider']
        doc.doc_detnotconsider = data['doc_detnotconsider']
        doc.doc_detfindings = data['doc_detfindings']
        doc.doc_detnotfindings = data['doc_detnotfindings']
        doc.doc_eiravailableat = data['doc_eiravailableat']
        doc.doc_pending = False
        doc.doc_plannerreview = True
        doc.doc_plannerregion = self.request.POST.get('doc_plannerregion')
        doc.save()
        prj.prj_title = data['prj_title']
        prj.prj_description = data['prj_description']
        if prj.prj_pending:
            prj.prj_pending = False
            prj.prj_plannerreview = True
        prj.save()

        try:
            coords = latlongs.objects.get(pk=doc.pk)
            coords.doc_latitude = data['doc_latitude']
            coords.doc_longitude = data['doc_longitude']
        except latlongs.DoesNotExist:
            coords = latlongs(doc_pk=doc.pk,doc_prj_fk=prj,doc_doctype="NOD",doc_latitude=data['doc_latitude'],doc_longitude=data['doc_longitude'])
        coords.save()

        return super(pendingdetail_nod,self).form_valid(form)

class pendingdetail_noe(FormView):
    form_class = pendingdetailnoeform
    template_name="ceqanet/pendingdetail_noe.html"
 
    def get_success_url(self):
        success_url = "%s" % reverse_lazy('pending')
        return success_url

    def get_initial(self):
        initial = super(pendingdetail_noe, self).get_initial()

        docinfo = documents.objects.get(pk=self.request.GET.get('doc_pk'))
        latlonginfo = latlongs.objects.filter(doc_pk=self.request.GET.get('doc_pk'))

        initial['prj_title'] = docinfo.doc_prj_fk.prj_title
        initial['prj_description'] = docinfo.doc_prj_fk.prj_description
        initial['doc_conagency'] = docinfo.doc_conagency
        initial['doc_conname'] = docinfo.doc_conname
        initial['doc_conemail'] = docinfo.doc_conemail
        initial['doc_conphone'] = docinfo.doc_conphone
        initial['doc_conaddress1'] = docinfo.doc_conaddress1
        initial['doc_conaddress2'] = docinfo.doc_conaddress2
        initial['doc_concity'] = docinfo.doc_concity
        initial['doc_constate'] = docinfo.doc_constate
        initial['doc_conzip'] = docinfo.doc_conzip.strip
        initial['doc_location'] = docinfo.doc_location
        if latlonginfo.exists():
            initial['doc_latitude'] = latlonginfo[0].doc_latitude
            initial['doc_longitude'] = latlonginfo[0].doc_longitude

        if docinfo.doc_city != None:
            cityinfo = geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).filter(geow_shortname__startswith=docinfo.doc_city)
            if cityinfo.count() == 1:
                initial['doc_city'] = cityinfo[0].geow_pk

        if docinfo.doc_county != None:
            countyinfo = geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).filter(geow_shortname__startswith=docinfo.doc_county)
            if countyinfo.count() == 1:
                initial['doc_county'] = countyinfo[0].geow_pk

        if docinfo.doc_exministerial:
            initial['rdoexemptstatus'] = 1
        elif docinfo.doc_exdeclared:
            initial['rdoexemptstatus'] = 2
        elif docinfo.doc_exemergency:
            initial['rdoexemptstatus'] = 3
        elif docinfo.doc_excategorical:
            initial['rdoexemptstatus'] = 4
            initial['strsectionnumber'] = docinfo.doc_exnumber
        elif docinfo.doc_exstatutory:
            initial['rdoexemptstatus'] = 5
            initial['strcodenumber'] = docinfo.doc_exnumber

        initial['doc_exreasons'] = docinfo.doc_exreasons

        return initial

    def get_context_data(self, **kwargs):
        context = super(pendingdetail_noe, self).get_context_data(**kwargs)

        context['doc_pk'] = self.request.GET.get('doc_pk')

        return context

    def form_valid(self,form):
        data = form.cleaned_data

        doc = documents.objects.get(pk=self.request.POST.get('doc_pk'))
        prj = projects.objects.get(pk=doc.doc_prj_fk.prj_pk)

        if data['doc_city'] != None:
            cityname = geowords.objects.get(pk=data['doc_city'].pk)
        else:
            cityname = None
        if data['doc_county'] != None:
            countyname = geowords.objects.get(pk=data['doc_county'].pk)
        else:
            countyname = None
            
        doc_exministerial = False
        doc_exdeclared = False
        doc_exemergency = False
        doc_excategorical = False
        doc_exstatutory = False
        doc_exnumber = ''

        rdoexemptstatus = data['rdoexemptstatus']
        if rdoexemptstatus == '1':
            doc_exministerial = True
        elif rdoexemptstatus == '2':
            doc_exdeclared = True
        elif rdoexemptstatus == '3':
            doc_exemergency = True
        elif rdoexemptstatus == '4':
            doc_excategorical = True
            doc_exnumber = data['strsectionnumber']
        elif rdoexemptstatus == '5':
            doc_exstatutory = True
            doc_exnumber = data['strcodenumber']

        doc.doc_conagency = data['doc_conagency']
        doc.doc_conname = data['doc_conname']
        doc.doc_conemail = data['doc_conemail']
        doc.doc_conphone = data['doc_conphone']
        doc.doc_conaddress1 = data['doc_conaddress1']
        doc.doc_conaddress2 = data['doc_conaddress2']
        doc.doc_concity = data['doc_concity']
        doc.doc_constate = data['doc_constate']
        doc.doc_conzip = data['doc_conzip']
        doc.doc_location = data['doc_location']
        if data['doc_city'] != None:
            doc.doc_city = cityname.geow_shortname
        else:
            doc.doc_city = ''
        if data['doc_county'] != None:
            doc.doc_county = countyname.geow_shortname
        else:
            doc.doc_county = ''
        doc.doc_exministerial = doc_exministerial
        doc.doc_exdeclared = doc_exdeclared
        doc.doc_exemergency = doc_exemergency
        doc.doc_excategorical = doc_excategorical
        doc.doc_exstatutory = doc_exstatutory
        doc.doc_exnumber = doc_exnumber
        doc.doc_exreasons = data['doc_exreasons']
        doc.doc_pending = False
        doc.doc_plannerreview = True
        doc.doc_plannerregion = data['doc_plannerregion']
        doc.save()
        prj.prj_title = data['prj_title']
        prj.prj_description = data['prj_description']

        if prj.prj_pending:
            prj.prj_pending = False
            prj.prj_plannerreview = True
        prj.save()

        try:
            coords = latlongs.objects.get(pk=doc.pk)
            coords.doc_latitude = data['doc_latitude']
            coords.doc_longitude = data['doc_longitude']
        except latlongs.DoesNotExist:
            coords = latlongs(doc_pk=doc.pk,doc_prj_fk=prj,doc_doctype="NOE",doc_latitude=data['doc_latitude'],doc_longitude=data['doc_longitude'])
        coords.save()

        return super(pendingdetail_noe,self).form_valid(form)

class pendingdetail_nop(FormView):
    form_class = pendingdetailnopform
    template_name="ceqanet/pendingdetail_nop.html"

    def get_success_url(self):
        success_url = "%s" % reverse_lazy('pending')
        return success_url
 
    def get_initial(self):
        initial = super(pendingdetail_nop, self).get_initial()

        docinfo = documents.objects.get(pk=self.request.GET.get('doc_pk'))
        latlonginfo = latlongs.objects.filter(doc_pk=self.request.GET.get('doc_pk'))
        devinfo = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1010)
        dkey_comment_actions = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_pk=1018)
        dkey_comment_dev = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_pk=11001)
        dkey_comment_issues = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_pk=2034)
        
        initial['prj_title'] = docinfo.doc_prj_fk.prj_title
        initial['prj_description'] = docinfo.doc_prj_fk.prj_description
        initial['doc_conagency'] = docinfo.doc_conagency
        initial['doc_conname'] = docinfo.doc_conname
        initial['doc_conemail'] = docinfo.doc_conemail
        initial['doc_conphone'] = docinfo.doc_conphone
        initial['doc_conaddress1'] = docinfo.doc_conaddress1
        initial['doc_conaddress2'] = docinfo.doc_conaddress2
        initial['doc_concity'] = docinfo.doc_concity
        initial['doc_constate'] = docinfo.doc_constate
        initial['doc_conzip'] = docinfo.doc_conzip.strip
        initial['doc_location'] = docinfo.doc_location
        if latlonginfo.exists():
            initial['doc_latitude'] = latlonginfo[0].doc_latitude
            initial['doc_longitude'] = latlonginfo[0].doc_longitude

        if docinfo.doc_city != None:
            cityinfo = geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).filter(geow_shortname__startswith=docinfo.doc_city)
            if cityinfo.count() == 1:
                initial['doc_city'] = cityinfo[0].geow_pk

        if docinfo.doc_county != None:
            countyinfo = geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).filter(geow_shortname__startswith=docinfo.doc_county)
            if countyinfo.count() == 1:
                initial['doc_county'] = countyinfo[0].geow_pk

        initial['doc_parcelno'] = docinfo.doc_parcelno
        initial['doc_xstreets'] = docinfo.doc_xstreets
        initial['doc_township'] = docinfo.doc_township
        initial['doc_range'] = docinfo.doc_range
        initial['doc_section'] = docinfo.doc_section
        initial['doc_base'] = docinfo.doc_base
        initial['doc_highways'] = docinfo.doc_highways
        initial['doc_railways'] = docinfo.doc_railways
        initial['doc_airports'] = docinfo.doc_airports
        initial['doc_schools'] = docinfo.doc_schools
        initial['doc_waterways'] = docinfo.doc_waterways
        initial['doc_parcelno'] = docinfo.doc_parcelno
        initial['doc_landuse'] = docinfo.doc_landuse

        if dkey_comment_actions.exists():
            initial['dkey_comment_actions'] = dkey_comment_actions[0].dkey_comment
        if dkey_comment_dev.exists():
            initial['dkey_comment_dev'] = dkey_comment_dev[0].dkey_comment
        if dkey_comment_issues.exists():
            initial['dkey_comment_issues'] = dkey_comment_issues[0].dkey_comment

        for dev in devinfo:
            if dev.dkey_keyw_fk.keyw_pk > 4000:
                if dev.dkey_keyw_fk.keyw_pk < 5000:
                    initial['devtrans_id'] = dev.dkey_keyw_fk.keyw_pk
                    initial['devtrans_comment'] = dev.dkey_comment
            if dev.dkey_keyw_fk.keyw_pk > 3000:
                if dev.dkey_keyw_fk.keyw_pk < 4000:
                    initial['devpower_id'] = dev.dkey_keyw_fk.keyw_pk
                    initial['devpower_comment'] = dev.dkey_comment
            if dev.dkey_keyw_fk.keyw_pk == 6001:
                initial['dev6001_val1'] = dev.dkey_value1
                initial['dev6001_val2'] = dev.dkey_value2
            elif dev.dkey_keyw_fk.keyw_pk == 6002:
                initial['dev6002_val1'] = dev.dkey_value1
                initial['dev6002_val2'] = dev.dkey_value2
                initial['dev6002_val3'] = dev.dkey_value3
            elif dev.dkey_keyw_fk.keyw_pk == 6003:
                initial['dev6003_val1'] = dev.dkey_value1
                initial['dev6003_val2'] = dev.dkey_value2
                initial['dev6003_val3'] = dev.dkey_value3
            elif dev.dkey_keyw_fk.keyw_pk == 6004:
                initial['dev6004_val1'] = dev.dkey_value1
                initial['dev6004_val2'] = dev.dkey_value2
                initial['dev6004_val3'] = dev.dkey_value3
            elif dev.dkey_keyw_fk.keyw_pk == 7001:
                initial['dev7001_val1'] = dev.dkey_value1
            elif dev.dkey_keyw_fk.keyw_pk == 8001:
                initial['dev8001_val1'] = dev.dkey_value1
            elif dev.dkey_keyw_fk.keyw_pk == 9001:
                initial['dev9001_val1'] = dev.dkey_value1
            elif dev.dkey_keyw_fk.keyw_pk == 10001:
                initial['dev10001_val1'] = dev.dkey_value1

        return initial

    def get_context_data(self, **kwargs):
        context = super(pendingdetail_nop, self).get_context_data(**kwargs)
        context['doc_pk'] = self.request.GET.get('doc_pk')
        context['lats'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1001)
        context['devs'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1010)
        context['isss'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1002)

        return context

    def form_valid(self,form):
        data = form.cleaned_data
        doc = documents.objects.get(pk=self.request.POST.get('doc_pk'))
        prj = projects.objects.get(pk=doc.doc_prj_fk.prj_pk)

        if data['doc_city'] != None:
            cityname = geowords.objects.get(pk=data['doc_city'].pk)
        else:
            cityname = None
        if data['doc_county'] != None:
            countyname = geowords.objects.get(pk=data['doc_county'].pk)
        else:
            countyname = None

        if data['doc_conaddress2'] == '':
            doc_conaddress2 = None
        else:
            doc_conaddress2 = data['doc_conaddress2']
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

        doc.doc_conagency = data['doc_conagency']
        doc.doc_conname = data['doc_conname']
        doc.doc_conemail = data['doc_conemail']
        doc.doc_conphone = data['doc_conphone']
        doc.doc_conaddress1 = data['doc_conaddress1']
        doc.doc_conaddress2 = doc_conaddress2
        doc.doc_concity = data['doc_concity']
        doc.doc_constate = data['doc_constate']
        doc.doc_conzip = data['doc_conzip']
        doc.doc_location = data['doc_location']
        if data['doc_city'] != None:
            doc.doc_city = cityname.geow_shortname
        else:
            doc.doc_city = ''
        if data['doc_county'] != None:
            doc.doc_county = countyname.geow_shortname
        else:
            doc.doc_county = ''
        doc.doc_parcelno = doc_parcelno
        doc.doc_xstreets = doc_xstreets
        doc.doc_township = doc_township
        doc.doc_range = doc_range
        doc.doc_section = doc_section
        doc.doc_base = doc.doc_base
        doc.doc_highways = doc_highways
        doc.doc_airports = doc_airports
        doc.doc_railways = doc_railways
        doc.doc_waterways = doc_waterways
        doc.doc_landuse = doc_landuse
        doc.doc_schools = doc_schools
        doc.doc_pending = False
        doc.doc_plannerreview = True
        doc.doc_plannerregion = data['doc_plannerregion']
        doc.save()
        prj.prj_title = data['prj_title']
        prj.prj_description = data['prj_description']
        if prj.prj_pending:
            prj.prj_pending = False
            prj.prj_plannerreview = True
        prj.save()

        try:
            coords = latlongs.objects.get(pk=doc.pk)
            coords.doc_latitude = data['doc_latitude']
            coords.doc_longitude = data['doc_longitude']
        except latlongs.DoesNotExist:
            coords = latlongs(doc_pk=doc.pk,doc_prj_fk=prj,doc_doctype="NOP",doc_latitude=data['doc_latitude'],doc_longitude=data['doc_longitude'])
        coords.save()

        dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc.pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1001).delete()

        for a in data['actions']:
            if a.keyw_pk == 1018:
                adockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=a,dkey_comment=data['dkey_comment_actions'],dkey_rank=0)
            else:
                adockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=a,dkey_rank=0)
            adockeyw.save()
        
        dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc.pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1010).delete()

        devtypes = keywords.objects.filter(keyw_keyl_fk__keyl_pk=1010)
        for d in devtypes:
            if self.request.POST.get('dev'+str(d.keyw_pk)) == "1":
                if d.keyw_pk == 11001:
                    ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=d,dkey_comment=data['dkey_comment_dev'],dkey_value1=self.request.POST.get('dev'+str(d.keyw_pk)+'_val1'),dkey_value2=self.request.POST.get('dev'+str(d.keyw_pk)+'_val2'),dkey_value3=self.request.POST.get('dev'+str(d.keyw_pk)+'_val3'),dkey_rank=0)
                else:
                    ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=d,dkey_value1=self.request.POST.get('dev'+str(d.keyw_pk)+'_val1'),dkey_value2=self.request.POST.get('dev'+str(d.keyw_pk)+'_val2'),dkey_value3=self.request.POST.get('dev'+str(d.keyw_pk)+'_val3'),dkey_rank=0)
                ddockeyw.save()
        if self.request.POST.get('devtrans') == "1":
            ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=data['devtrans_id'],dkey_comment=data['devtrans_comment'],dkey_value1=None,dkey_value2=None,dkey_value3=None,dkey_rank=0)
            ddockeyw.save()
        if self.request.POST.get('devpower') == "1":
            ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=data['devpower_id'],dkey_comment=data['devpower_comment'],dkey_value1=self.request.POST.get('devpower_val1'),dkey_value2=None,dkey_value3=None,dkey_rank=0)
            ddockeyw.save()
        if self.request.POST.get('devwaste') == "1":
            ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=data['devwaste_id'],dkey_comment=data['devwaste_comment'],dkey_value1=None,dkey_value2=None,dkey_value3=None,dkey_rank=0)
            ddockeyw.save()

        dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc.pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1002).delete()
        
        for i in data['issues']:
            if i.keyw_pk == 2034:
                idockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=i,dkey_comment=data['dkey_comment_issues'],dkey_rank=0)
            else:
                idockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=i,dkey_rank=0)
            idockeyw.save()

        docreviews.objects.filter(drag_doc_fk=doc.pk).delete()

        for ra in data['ragencies']:
            docrev = docreviews(drag_doc_fk=doc,drag_rag_fk=ra,drag_rank=0,drag_copies=1)
            docrev.save()

        return super(pendingdetail_nop,self).form_valid(form)

class review(ListView):
    template_name="ceqanet/review.html"
    context_object_name = "reviews"
    paginate_by = 25

    def get_queryset(self):
        queryset = ReviewListQuery(self.request)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(review, self).get_context_data(**kwargs)

        qsminuspage = self.request.GET.copy()
        
        if "page" in qsminuspage:
            qsminuspage.pop('page')

        context['restofqs'] = qsminuspage.urlencode()

        return context

def ReviewListQuery(request):
    region = request.user.get_profile().region 
    queryset = documents.objects.filter(doc_plannerregion=region).filter(doc_plannerreview=True).order_by('-doc_received')
    return queryset

class reviewdetail_noc(FormView):
    form_class = reviewdetailnocform
    template_name="ceqanet/reviewdetail_noc.html"

    def get_success_url(self):
        success_url = "%s" % (reverse_lazy('review'))
        return success_url
 
    def get_initial(self):
        initial = super(reviewdetail_noc, self).get_initial()

        docinfo = documents.objects.get(pk=self.request.GET.get('doc_pk'))
        latlonginfo = latlongs.objects.filter(doc_pk=self.request.GET.get('doc_pk'))
        devinfo = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1010)
        dkey_comment_actions = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_pk=1018)
        dkey_comment_dev = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_pk=11001)
        dkey_comment_issues = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_pk=2034)
        
        initial['prj_title'] = docinfo.doc_prj_fk.prj_title
        initial['prj_description'] = docinfo.doc_prj_fk.prj_description
        initial['doc_conagency'] = docinfo.doc_conagency
        initial['doc_conname'] = docinfo.doc_conname
        initial['doc_conemail'] = docinfo.doc_conemail
        initial['doc_conphone'] = docinfo.doc_conphone
        initial['doc_conaddress1'] = docinfo.doc_conaddress1
        initial['doc_conaddress2'] = docinfo.doc_conaddress2
        initial['doc_concity'] = docinfo.doc_concity
        initial['doc_constate'] = docinfo.doc_constate
        initial['doc_conzip'] = docinfo.doc_conzip.strip
        initial['doc_location'] = docinfo.doc_location
        if latlonginfo.exists():
            initial['doc_latitude'] = latlonginfo[0].doc_latitude
            initial['doc_longitude'] = latlonginfo[0].doc_longitude

        if docinfo.doc_city != None:
            cityinfo = geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).filter(geow_shortname__startswith=docinfo.doc_city)
            if cityinfo.count() == 1:
                initial['doc_city'] = cityinfo[0].geow_pk

        if docinfo.doc_county != None:
            countyinfo = geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).filter(geow_shortname__startswith=docinfo.doc_county)
            if countyinfo.count() == 1:
                initial['doc_county'] = countyinfo[0].geow_pk

        initial['doc_parcelno'] = docinfo.doc_parcelno
        initial['doc_xstreets'] = docinfo.doc_xstreets
        initial['doc_township'] = docinfo.doc_township
        initial['doc_range'] = docinfo.doc_range
        initial['doc_section'] = docinfo.doc_section
        initial['doc_base'] = docinfo.doc_base
        initial['doc_highways'] = docinfo.doc_highways
        initial['doc_railways'] = docinfo.doc_railways
        initial['doc_airports'] = docinfo.doc_airports
        initial['doc_schools'] = docinfo.doc_schools
        initial['doc_waterways'] = docinfo.doc_waterways
        initial['doc_parcelno'] = docinfo.doc_parcelno
        initial['doc_landuse'] = docinfo.doc_landuse

        initial['doctypeid'] = docinfo.doc_doct_fk.keyw_pk
        if dkey_comment_actions.exists():
            initial['dkey_comment_actions'] = dkey_comment_actions[0].dkey_comment
        if dkey_comment_dev.exists():
            initial['dkey_comment_dev'] = dkey_comment_dev[0].dkey_comment
        if dkey_comment_issues.exists():
            initial['dkey_comment_issues'] = dkey_comment_issues[0].dkey_comment

        for dev in devinfo:
            if dev.dkey_keyw_fk.keyw_pk > 4000:
                if dev.dkey_keyw_fk.keyw_pk < 5000:
                    initial['devtrans_id'] = dev.dkey_keyw_fk.keyw_pk
                    initial['devtrans_comment'] = dev.dkey_comment
            if dev.dkey_keyw_fk.keyw_pk > 3000:
                if dev.dkey_keyw_fk.keyw_pk < 4000:
                    initial['devpower_id'] = dev.dkey_keyw_fk.keyw_pk
                    initial['devpower_comment'] = dev.dkey_comment
            if dev.dkey_keyw_fk.keyw_pk == 6001:
                initial['dev6001_val1'] = dev.dkey_value1
                initial['dev6001_val2'] = dev.dkey_value2
            elif dev.dkey_keyw_fk.keyw_pk == 6002:
                initial['dev6002_val1'] = dev.dkey_value1
                initial['dev6002_val2'] = dev.dkey_value2
                initial['dev6002_val3'] = dev.dkey_value3
            elif dev.dkey_keyw_fk.keyw_pk == 6003:
                initial['dev6003_val1'] = dev.dkey_value1
                initial['dev6003_val2'] = dev.dkey_value2
                initial['dev6003_val3'] = dev.dkey_value3
            elif dev.dkey_keyw_fk.keyw_pk == 6004:
                initial['dev6004_val1'] = dev.dkey_value1
                initial['dev6004_val2'] = dev.dkey_value2
                initial['dev6004_val3'] = dev.dkey_value3
            elif dev.dkey_keyw_fk.keyw_pk == 7001:
                initial['dev7001_val1'] = dev.dkey_value1
            elif dev.dkey_keyw_fk.keyw_pk == 8001:
                initial['dev8001_val1'] = dev.dkey_value1
            elif dev.dkey_keyw_fk.keyw_pk == 9001:
                initial['dev9001_val1'] = dev.dkey_value1
            elif dev.dkey_keyw_fk.keyw_pk == 10001:
                initial['dev10001_val1'] = dev.dkey_value1

        return initial

    def get_context_data(self, **kwargs):
        context = super(reviewdetail_noc, self).get_context_data(**kwargs)
        context['doc_pk'] = self.request.GET.get('doc_pk')
        context['lats'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1001)
        context['devs'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1010)
        context['isss'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1002)

        return context

    def form_valid(self,form):
        data = form.cleaned_data
        doc = documents.objects.get(pk=self.request.POST.get('doc_pk'))
        prj = projects.objects.get(pk=doc.doc_prj_fk.prj_pk)

        if data['doc_city'] != None:
            cityname = geowords.objects.get(pk=data['doc_city'].pk)
        else:
            cityname = None
        if data['doc_county'] != None:
            countyname = geowords.objects.get(pk=data['doc_county'].pk)
        else:
            countyname = None

        if data['doc_conaddress2'] == '':
            doc_conaddress2 = None
        else:
            doc_conaddress2 = data['doc_conaddress2']
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

        doc.doc_conagency = data['doc_conagency']
        doc.doc_conname = data['doc_conname']
        doc.doc_conemail = data['doc_conemail']
        doc.doc_conphone = data['doc_conphone']
        doc.doc_conaddress1 = data['doc_conaddress1']
        doc.doc_conaddress2 = doc_conaddress2
        doc.doc_concity = data['doc_concity']
        doc.doc_constate = data['doc_constate']
        doc.doc_conzip = data['doc_conzip']
        doc.doc_location = data['doc_location']
        if data['doc_city'] != None:
            doc.doc_city = cityname.geow_shortname
        else:
            doc.doc_city = ''
        if data['doc_county'] != None:
            doc.doc_county = countyname.geow_shortname
        else:
            doc.doc_county = ''
        doc.doc_parcelno = doc_parcelno
        doc.doc_xstreets = doc_xstreets
        doc.doc_township = doc_township
        doc.doc_range = doc_range
        doc.doc_section = doc_section
        doc.doc_base = doc.doc_base
        doc.doc_highways = doc_highways
        doc.doc_airports = doc_airports
        doc.doc_railways = doc_railways
        doc.doc_waterways = doc_waterways
        doc.doc_landuse = doc_landuse
        doc.doc_schools = doc_schools
        doc.doc_doct_fk = data['doctypeid']
        doc.doc_doctype = data['doctypeid'].keyw_shortname
        doc.doc_docname = data['doctypeid'].keyw_longname

        ch = clearinghouse.objects.get(pk=1)
        currentidnum = str(ch.currentid)
        if len(currentidnum) == 1:
            currentidnum = "00"+currentidnum
        elif len(currentidnum) == 2:
            currentidnum = "0"+currentidnum
        schno = ch.schnoprefix + str(doc.doc_plannerregion) + currentidnum
        ch.currentid = ch.currentid+1
        ch.save()

        doc.doc_dept = data['doc_dept']
        doc.doc_clear = data['doc_clear']
        doc.doc_review = True
        doc.doc_plannerreview = False
        doc.doc_schno = schno
        doc.save()
        prj.prj_title = data['prj_title']
        prj.prj_description = data['prj_description']

        if prj.prj_pending:
            prj.prj_schno = schno
            prj.prj_plannerreview = False
        prj.save()

        try:
            coords = latlongs.objects.get(pk=doc.pk)
            coords.doc_latitude = data['doc_latitude']
            coords.doc_longitude = data['doc_longitude']
        except latlongs.DoesNotExist:
            coords = latlongs(doc_pk=doc.pk,doc_prj_fk=prj,doc_doctype="NOC",doc_latitude=data['doc_latitude'],doc_longitude=data['doc_longitude'])
        coords.save()

        dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc.pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1001).delete()

        for a in data['actions']:
            if a.keyw_pk == 1018:
                adockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=a,dkey_comment=data['dkey_comment_actions'],dkey_rank=0)
            else:
                adockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=a,dkey_rank=0)
            adockeyw.save()
        
        dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc.pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1010).delete()

        devtypes = keywords.objects.filter(keyw_keyl_fk__keyl_pk=1010)
        for d in devtypes:
            if self.request.POST.get('dev'+str(d.keyw_pk)) == "1":
                if d.keyw_pk == 11001:
                    ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=d,dkey_comment=data['dkey_comment_dev'],dkey_value1=self.request.POST.get('dev'+str(d.keyw_pk)+'_val1'),dkey_value2=self.request.POST.get('dev'+str(d.keyw_pk)+'_val2'),dkey_value3=self.request.POST.get('dev'+str(d.keyw_pk)+'_val3'),dkey_rank=0)
                else:
                    ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=d,dkey_value1=self.request.POST.get('dev'+str(d.keyw_pk)+'_val1'),dkey_value2=self.request.POST.get('dev'+str(d.keyw_pk)+'_val2'),dkey_value3=self.request.POST.get('dev'+str(d.keyw_pk)+'_val3'),dkey_rank=0)
                ddockeyw.save()
        if self.request.POST.get('devtrans') == "1":
            ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=data['devtrans_id'],dkey_comment=data['devtrans_comment'],dkey_value1=None,dkey_value2=None,dkey_value3=None,dkey_rank=0)
            ddockeyw.save()
        if self.request.POST.get('devpower') == "1":
            ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=data['devpower_id'],dkey_comment=data['devpower_comment'],dkey_value1=self.request.POST.get('devpower_val1'),dkey_value2=None,dkey_value3=None,dkey_rank=0)
            ddockeyw.save()
        if self.request.POST.get('devwaste') == "1":
            ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=data['devwaste_id'],dkey_comment=data['devwaste_comment'],dkey_value1=None,dkey_value2=None,dkey_value3=None,dkey_rank=0)
            ddockeyw.save()

        dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc.pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1002).delete()
        
        for i in data['issues']:
            if i.keyw_pk == 2034:
                idockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=i,dkey_comment=data['dkey_comment_issues'],dkey_rank=0)
            else:
                idockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=i,dkey_rank=0)
            idockeyw.save()

        docreviews.objects.filter(drag_doc_fk=doc.pk).delete()

        for ra in data['ragencies']:
            docrev = docreviews(drag_doc_fk=doc,drag_rag_fk=ra,drag_rank=0,drag_copies=1)
            docrev.save()

        return super(reviewdetail_noc,self).form_valid(form)

class reviewdetail_nod(FormView):
    form_class = reviewdetailnodform
    template_name="ceqanet/reviewdetail_nod.html"

    def get_success_url(self):
        success_url = "%s" % (reverse_lazy('review'))
        return success_url
 
    def get_initial(self):
        initial = super(pendingdetail_nod, self).get_initial()

        docinfo = documents.objects.get(pk=self.request.GET.get('doc_pk'))
        latlonginfo = latlongs.objects.filter(doc_pk=self.request.GET.get('doc_pk'))

        initial['prj_title'] = docinfo.doc_prj_fk.prj_title
        initial['prj_description'] = docinfo.doc_prj_fk.prj_description
        initial['doc_conagency'] = docinfo.doc_conagency
        initial['doc_conname'] = docinfo.doc_conname
        initial['doc_conemail'] = docinfo.doc_conemail
        initial['doc_conphone'] = docinfo.doc_conphone
        initial['doc_conaddress1'] = docinfo.doc_conaddress1
        initial['doc_conaddress2'] = docinfo.doc_conaddress2
        initial['doc_concity'] = docinfo.doc_concity
        initial['doc_constate'] = docinfo.doc_constate
        initial['doc_conzip'] = docinfo.doc_conzip.strip
        initial['doc_location'] = docinfo.doc_location
        if latlonginfo.exists():
            initial['doc_latitude'] = latlonginfo[0].doc_latitude
            initial['doc_longitude'] = latlonginfo[0].doc_longitude

        if docinfo.doc_city != None:
            cityinfo = geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).filter(geow_shortname__startswith=docinfo.doc_city)
            if cityinfo.count() == 1:
                initial['doc_city'] = cityinfo[0].geow_pk

        if docinfo.doc_county != None:
            countyinfo = geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).filter(geow_shortname__startswith=docinfo.doc_county)
            if countyinfo.count() == 1:
                initial['doc_county'] = countyinfo[0].geow_pk

        initial['doc_nodbylead'] = docinfo.doc_nodbylead
        initial['doc_nodbyresp'] = docinfo.doc_nodbyresp
        initial['doc_nodagency'] = docinfo.doc_nodagency
        initial['doc_nod'] = docinfo.doc_nod
        initial['doc_detsigeffect'] = docinfo.doc_detsigeffect
        initial['doc_detnotsigeffect'] = docinfo.doc_detnotsigeffect
        initial['doc_deteir'] = docinfo.doc_deteir
        initial['doc_detnegdec'] = docinfo.doc_detnegdec
        initial['doc_detmitigation'] = docinfo.doc_detmitigation
        initial['doc_detnotmitigation'] = docinfo.doc_detnotmitigation
        initial['doc_detconsider'] = docinfo.doc_detconsider
        initial['doc_detnotconsider'] = docinfo.doc_detnotconsider
        initial['doc_detfindings'] = docinfo.doc_detfindings
        initial['doc_detnotfindings'] = docinfo.doc_detnotfindings
        initial['doc_eiravailableat'] = docinfo.doc_eiravailableat

        return initial

    def get_context_data(self, **kwargs):
        context = super(reviewdetail_nod, self).get_context_data(**kwargs)

        context['doc_pk'] = self.request.GET.get('doc_pk')

        return context

    def form_valid(self,form):
        data = form.cleaned_data

        doc = documents.objects.get(pk=self.request.POST.get('doc_pk'))
        prj = projects.objects.get(pk=doc.doc_prj_fk.prj_pk)

        if data['doc_city'] != None:
            cityname = geowords.objects.get(pk=data['doc_city'].pk)
        else:
            cityname = None
        if data['doc_county'] != None:
            countyname = geowords.objects.get(pk=data['doc_county'].pk)
        else:
            countyname = None

        doc.doc_conagency = data['doc_conagency']
        doc.doc_conname = data['doc_conname']
        doc.doc_conemail = data['doc_conemail']
        doc.doc_conphone = data['doc_conphone']
        doc.doc_conaddress1 = data['doc_conaddress1']
        doc.doc_conaddress2 = data['doc_conaddress2']
        doc.doc_concity = data['doc_concity']
        doc.doc_constate = data['doc_constate']
        doc.doc_conzip = data['doc_conzip']
        doc.doc_location = data['doc_location']
        if data['doc_city'] != None:
            doc.doc_city = cityname.geow_shortname
        else:
            doc.doc_city = ''
        if data['doc_county'] != None:
            doc.doc_county = countyname.geow_shortname
        else:
            doc.doc_county = ''
        doc.doc_nodbylead = data['doc_nodbylead']
        doc.doc_nodbyresp = data['doc_nodbyresp']
        doc.doc_nodagency = data['doc_nodagency']
        doc.doc_nod = data['doc_nod']
        doc.doc_detsigeffect = data['doc_detsigeffect']
        doc.doc_detnotsigeffect = data['doc_detnotsigeffect']
        doc.doc_deteir = data['doc_deteir']
        doc.doc_detnegdec = data['doc_detnegdec']
        doc.doc_detmitigation = data['doc_detmitigation']
        doc.doc_detnotmitigation = data['doc_detnotmitigation']
        doc.doc_detconsider = data['doc_detconsider']
        doc.doc_detnotconsider = data['doc_detnotconsider']
        doc.doc_detfindings = data['doc_detfindings']
        doc.doc_detnotfindings = data['doc_detnotfindings']
        doc.doc_eiravailableat = data['doc_eiravailableat']

        ch = clearinghouse.objects.get(pk=1)
        currentidnum = str(ch.currentid)
        if len(currentidnum) == 1:
            currentidnum = "00"+currentidnum
        elif len(currentidnum) == 2:
            currentidnum = "0"+currentidnum
        schno = ch.schnoprefix + str(doc.doc_plannerregion) + currentidnum
        ch.currentid = ch.currentid+1
        ch.save()

        doc.doc_visible = True
        doc.doc_plannerreview = False
        doc.doc_schno = schno
        doc.save()
        prj.prj_title = data['prj_title']
        prj.prj_description = data['prj_description']
        if prj.prj_pending:
            prj.prj_schno = schno
            prj.prj_plannerreview = False
        prj.save()

        try:
            coords = latlongs.objects.get(pk=doc.pk)
            coords.doc_latitude = data['doc_latitude']
            coords.doc_longitude = data['doc_longitude']
        except latlongs.DoesNotExist:
            coords = latlongs(doc_pk=doc.pk,doc_prj_fk=prj,doc_doctype="NOD",doc_latitude=data['doc_latitude'],doc_longitude=data['doc_longitude'])
        coords.save()

        return super(reviewdetail_nod,self).form_valid(form)

class reviewdetail_noe(FormView):
    form_class = reviewdetailnoeform
    template_name="ceqanet/reviewdetail_noe.html"
 
    def get_success_url(self):
        success_url = "%s" % (reverse_lazy('review'))
        return success_url

    def get_initial(self):
        initial = super(reviewdetail_noe, self).get_initial()

        docinfo = documents.objects.get(pk=self.request.GET.get('doc_pk'))
        latlonginfo = latlongs.objects.filter(doc_pk=self.request.GET.get('doc_pk'))

        initial['prj_title'] = docinfo.doc_prj_fk.prj_title
        initial['prj_description'] = docinfo.doc_prj_fk.prj_description
        initial['doc_conagency'] = docinfo.doc_conagency
        initial['doc_conname'] = docinfo.doc_conname
        initial['doc_conemail'] = docinfo.doc_conemail
        initial['doc_conphone'] = docinfo.doc_conphone
        initial['doc_conaddress1'] = docinfo.doc_conaddress1
        initial['doc_conaddress2'] = docinfo.doc_conaddress2
        initial['doc_concity'] = docinfo.doc_concity
        initial['doc_constate'] = docinfo.doc_constate
        initial['doc_conzip'] = docinfo.doc_conzip.strip
        initial['doc_location'] = docinfo.doc_location
        if latlonginfo.exists():
            initial['doc_latitude'] = latlonginfo[0].doc_latitude
            initial['doc_longitude'] = latlonginfo[0].doc_longitude

        if docinfo.doc_city != None:
            cityinfo = geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).filter(geow_shortname__startswith=docinfo.doc_city)
            if cityinfo.count() == 1:
                initial['doc_city'] = cityinfo[0].geow_pk

        if docinfo.doc_county != None:
            countyinfo = geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).filter(geow_shortname__startswith=docinfo.doc_county)
            if countyinfo.count() == 1:
                initial['doc_county'] = countyinfo[0].geow_pk

        if docinfo.doc_exministerial:
            initial['rdoexemptstatus'] = 1
        elif docinfo.doc_exdeclared:
            initial['rdoexemptstatus'] = 2
        elif docinfo.doc_exemergency:
            initial['rdoexemptstatus'] = 3
        elif docinfo.doc_excategorical:
            initial['rdoexemptstatus'] = 4
            initial['strsectionnumber'] = docinfo.doc_exnumber
        elif docinfo.doc_exstatutory:
            initial['rdoexemptstatus'] = 5
            initial['strcodenumber'] = docinfo.doc_exnumber

        initial['doc_exreasons'] = docinfo.doc_exreasons

        return initial

    def get_context_data(self, **kwargs):
        context = super(reviewdetail_noe, self).get_context_data(**kwargs)

        context['doc_pk'] = self.request.GET.get('doc_pk')

        return context

    def form_valid(self,form):
        data = form.cleaned_data

        doc = documents.objects.get(pk=self.request.POST.get('doc_pk'))
        prj = projects.objects.get(pk=doc.doc_prj_fk.prj_pk)

        if data['doc_city'] != None:
            cityname = geowords.objects.get(pk=data['doc_city'].pk)
        else:
            cityname = None
        if data['doc_county'] != None:
            countyname = geowords.objects.get(pk=data['doc_county'].pk)
        else:
            countyname = None
            
        doc_exministerial = False
        doc_exdeclared = False
        doc_exemergency = False
        doc_excategorical = False
        doc_exstatutory = False
        doc_exnumber = ''

        rdoexemptstatus = data['rdoexemptstatus']
        if rdoexemptstatus == '1':
            doc_exministerial = True
        elif rdoexemptstatus == '2':
            doc_exdeclared = True
        elif rdoexemptstatus == '3':
            doc_exemergency = True
        elif rdoexemptstatus == '4':
            doc_excategorical = True
            doc_exnumber = data['strsectionnumber']
        elif rdoexemptstatus == '5':
            doc_exstatutory = True
            doc_exnumber = data['strcodenumber']

        doc.doc_conagency = data['doc_conagency']
        doc.doc_conname = data['doc_conname']
        doc.doc_conemail = data['doc_conemail']
        doc.doc_conphone = data['doc_conphone']
        doc.doc_conaddress1 = data['doc_conaddress1']
        doc.doc_conaddress2 = data['doc_conaddress2']
        doc.doc_concity = data['doc_concity']
        doc.doc_constate = data['doc_constate']
        doc.doc_conzip = data['doc_conzip']
        doc.doc_location = data['doc_location']
        if data['doc_city'] != None:
            doc.doc_city = cityname.geow_shortname
        else:
            doc.doc_city = ''
        if data['doc_county'] != None:
            doc.doc_county = countyname.geow_shortname
        else:
            doc.doc_county = ''
        doc.doc_exministerial = doc_exministerial
        doc.doc_exdeclared = doc_exdeclared
        doc.doc_exemergency = doc_exemergency
        doc.doc_excategorical = doc_excategorical
        doc.doc_exstatutory = doc_exstatutory
        doc.doc_exnumber = doc_exnumber
        doc.doc_exreasons = data['doc_exreasons']

        ch = clearinghouse.objects.get(pk=1)
        currentidnum = str(ch.currentid)
        if len(currentidnum) == 1:
            currentidnum = "00"+currentidnum
        elif len(currentidnum) == 2:
            currentidnum = "0"+currentidnum
        schno = ch.schnoprefix + str(doc.doc_plannerregion) + currentidnum
        ch.currentid = ch.currentid+1
        ch.save()

        doc.doc_visible = True
        doc.doc_plannerreview = False
        doc.doc_schno = schno

        prj = projects.objects.get(pk=doc.doc_prj_fk.prj_pk)

        if prj.prj_pending:
            prj.prj_schno = schno
            prj.prj_plannerreview = False
        doc.save()
        prj.save()

        try:
            coords = latlongs.objects.get(pk=doc.pk)
            coords.doc_latitude = data['doc_latitude']
            coords.doc_longitude = data['doc_longitude']
        except latlongs.DoesNotExist:
            coords = latlongs(doc_pk=doc.pk,doc_prj_fk=prj,doc_doctype="NOE",doc_latitude=data['doc_latitude'],doc_longitude=data['doc_longitude'])
        coords.save()

        return super(reviewdetail_noe,self).form_valid(form)

class reviewdetail_nop(FormView):
    form_class = reviewdetailnopform
    template_name="ceqanet/reviewdetail_nop.html"

    def get_success_url(self):
        success_url = "%s" % (reverse_lazy('review'))
        return success_url
 
    def get_initial(self):
        initial = super(reviewdetail_nop, self).get_initial()

        docinfo = documents.objects.get(pk=self.request.GET.get('doc_pk'))
        latlonginfo = latlongs.objects.filter(doc_pk=self.request.GET.get('doc_pk'))
        devinfo = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1010)
        dkey_comment_actions = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_pk=1018)
        dkey_comment_dev = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_pk=11001)
        dkey_comment_issues = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_pk=2034)
        
        initial['prj_title'] = docinfo.doc_prj_fk.prj_title
        initial['prj_description'] = docinfo.doc_prj_fk.prj_description
        initial['doc_conagency'] = docinfo.doc_conagency
        initial['doc_conname'] = docinfo.doc_conname
        initial['doc_conemail'] = docinfo.doc_conemail
        initial['doc_conphone'] = docinfo.doc_conphone
        initial['doc_conaddress1'] = docinfo.doc_conaddress1
        initial['doc_conaddress2'] = docinfo.doc_conaddress2
        initial['doc_concity'] = docinfo.doc_concity
        initial['doc_constate'] = docinfo.doc_constate
        initial['doc_conzip'] = docinfo.doc_conzip.strip
        initial['doc_location'] = docinfo.doc_location
        if latlonginfo.exists():
            initial['doc_latitude'] = latlonginfo[0].doc_latitude
            initial['doc_longitude'] = latlonginfo[0].doc_longitude

        if docinfo.doc_city != None:
            cityinfo = geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).filter(geow_shortname__startswith=docinfo.doc_city)
            if cityinfo.count() == 1:
                initial['doc_city'] = cityinfo[0].geow_pk

        if docinfo.doc_county != None:
            countyinfo = geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).filter(geow_shortname__startswith=docinfo.doc_county)
            if countyinfo.count() == 1:
                initial['doc_county'] = countyinfo[0].geow_pk

        initial['doc_parcelno'] = docinfo.doc_parcelno
        initial['doc_xstreets'] = docinfo.doc_xstreets
        initial['doc_township'] = docinfo.doc_township
        initial['doc_range'] = docinfo.doc_range
        initial['doc_section'] = docinfo.doc_section
        initial['doc_base'] = docinfo.doc_base
        initial['doc_highways'] = docinfo.doc_highways
        initial['doc_railways'] = docinfo.doc_railways
        initial['doc_airports'] = docinfo.doc_airports
        initial['doc_schools'] = docinfo.doc_schools
        initial['doc_waterways'] = docinfo.doc_waterways
        initial['doc_parcelno'] = docinfo.doc_parcelno
        initial['doc_landuse'] = docinfo.doc_landuse

        if dkey_comment_actions.exists():
            initial['dkey_comment_actions'] = dkey_comment_actions[0].dkey_comment
        if dkey_comment_dev.exists():
            initial['dkey_comment_dev'] = dkey_comment_dev[0].dkey_comment
        if dkey_comment_issues.exists():
            initial['dkey_comment_issues'] = dkey_comment_issues[0].dkey_comment

        for dev in devinfo:
            if dev.dkey_keyw_fk.keyw_pk > 4000:
                if dev.dkey_keyw_fk.keyw_pk < 5000:
                    initial['devtrans_id'] = dev.dkey_keyw_fk.keyw_pk
                    initial['devtrans_comment'] = dev.dkey_comment
            if dev.dkey_keyw_fk.keyw_pk > 3000:
                if dev.dkey_keyw_fk.keyw_pk < 4000:
                    initial['devpower_id'] = dev.dkey_keyw_fk.keyw_pk
                    initial['devpower_comment'] = dev.dkey_comment
            if dev.dkey_keyw_fk.keyw_pk == 6001:
                initial['dev6001_val1'] = dev.dkey_value1
                initial['dev6001_val2'] = dev.dkey_value2
            elif dev.dkey_keyw_fk.keyw_pk == 6002:
                initial['dev6002_val1'] = dev.dkey_value1
                initial['dev6002_val2'] = dev.dkey_value2
                initial['dev6002_val3'] = dev.dkey_value3
            elif dev.dkey_keyw_fk.keyw_pk == 6003:
                initial['dev6003_val1'] = dev.dkey_value1
                initial['dev6003_val2'] = dev.dkey_value2
                initial['dev6003_val3'] = dev.dkey_value3
            elif dev.dkey_keyw_fk.keyw_pk == 6004:
                initial['dev6004_val1'] = dev.dkey_value1
                initial['dev6004_val2'] = dev.dkey_value2
                initial['dev6004_val3'] = dev.dkey_value3
            elif dev.dkey_keyw_fk.keyw_pk == 7001:
                initial['dev7001_val1'] = dev.dkey_value1
            elif dev.dkey_keyw_fk.keyw_pk == 8001:
                initial['dev8001_val1'] = dev.dkey_value1
            elif dev.dkey_keyw_fk.keyw_pk == 9001:
                initial['dev9001_val1'] = dev.dkey_value1
            elif dev.dkey_keyw_fk.keyw_pk == 10001:
                initial['dev10001_val1'] = dev.dkey_value1

        return initial

    def get_context_data(self, **kwargs):
        context = super(reviewdetail_nop, self).get_context_data(**kwargs)
        context['doc_pk'] = self.request.GET.get('doc_pk')
        context['lats'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1001)
        context['devs'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1010)
        context['isss'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1002)

        return context

    def form_valid(self,form):
        data = form.cleaned_data
        doc = documents.objects.get(pk=self.request.POST.get('doc_pk'))
        prj = projects.objects.get(pk=doc.doc_prj_fk.prj_pk)

        if data['doc_city'] != None:
            cityname = geowords.objects.get(pk=data['doc_city'].pk)
        else:
            cityname = None
        if data['doc_county'] != None:
            countyname = geowords.objects.get(pk=data['doc_county'].pk)
        else:
            countyname = None

        if data['doc_conaddress2'] == '':
            doc_conaddress2 = None
        else:
            doc_conaddress2 = data['doc_conaddress2']
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

        doc.doc_conagency = data['doc_conagency']
        doc.doc_conname = data['doc_conname']
        doc.doc_conemail = data['doc_conemail']
        doc.doc_conphone = data['doc_conphone']
        doc.doc_conaddress1 = data['doc_conaddress1']
        doc.doc_conaddress2 = doc_conaddress2
        doc.doc_concity = data['doc_concity']
        doc.doc_constate = data['doc_constate']
        doc.doc_conzip = data['doc_conzip']
        doc.doc_location = data['doc_location']
        if data['doc_city'] != None:
            doc.doc_city = cityname.geow_shortname
        else:
            doc.doc_city = ''
        if data['doc_county'] != None:
            doc.doc_county = countyname.geow_shortname
        else:
            doc.doc_county = ''
        doc.doc_parcelno = doc_parcelno
        doc.doc_xstreets = doc_xstreets
        doc.doc_township = doc_township
        doc.doc_range = doc_range
        doc.doc_section = doc_section
        doc.doc_base = doc.doc_base
        doc.doc_highways = doc_highways
        doc.doc_airports = doc_airports
        doc.doc_railways = doc_railways
        doc.doc_waterways = doc_waterways
        doc.doc_landuse = doc_landuse
        doc.doc_schools = doc_schools

        ch = clearinghouse.objects.get(pk=1)
        currentidnum = str(ch.currentid)
        if len(currentidnum) == 1:
            currentidnum = "00"+currentidnum
        elif len(currentidnum) == 2:
            currentidnum = "0"+currentidnum
        schno = ch.schnoprefix + str(doc.doc_plannerregion) + currentidnum
        ch.currentid = ch.currentid+1
        ch.save()

        doc.doc_dept = data['doc_dept']
        doc.doc_clear = data['doc_clear']
        doc.doc_review = True
        doc.doc_plannerreview = False
        doc.doc_schno = schno
        doc.save()

        prj.prj_title = data['prj_title']
        prj.prj_description = data['prj_description']
        if prj.prj_pending:
            prj.prj_schno = schno
            prj.prj_plannerreview = False
        prj.save()

        try:
            coords = latlongs.objects.get(pk=doc.pk)
            coords.doc_latitude = data['doc_latitude']
            coords.doc_longitude = data['doc_longitude']
        except latlongs.DoesNotExist:
            coords = latlongs(doc_pk=doc.pk,doc_prj_fk=prj,doc_doctype="NOP",doc_latitude=data['doc_latitude'],doc_longitude=data['doc_longitude'])
        coords.save()

        dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc.pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1001).delete()

        for a in data['actions']:
            if a.keyw_pk == 1018:
                adockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=a,dkey_comment=data['dkey_comment_actions'],dkey_rank=0)
            else:
                adockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=a,dkey_rank=0)
            adockeyw.save()
        
        dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc.pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1010).delete()

        devtypes = keywords.objects.filter(keyw_keyl_fk__keyl_pk=1010)
        for d in devtypes:
            if self.request.POST.get('dev'+str(d.keyw_pk)) == "1":
                if d.keyw_pk == 11001:
                    ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=d,dkey_comment=data['dkey_comment_dev'],dkey_value1=self.request.POST.get('dev'+str(d.keyw_pk)+'_val1'),dkey_value2=self.request.POST.get('dev'+str(d.keyw_pk)+'_val2'),dkey_value3=self.request.POST.get('dev'+str(d.keyw_pk)+'_val3'),dkey_rank=0)
                else:
                    ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=d,dkey_value1=self.request.POST.get('dev'+str(d.keyw_pk)+'_val1'),dkey_value2=self.request.POST.get('dev'+str(d.keyw_pk)+'_val2'),dkey_value3=self.request.POST.get('dev'+str(d.keyw_pk)+'_val3'),dkey_rank=0)
                ddockeyw.save()
        if self.request.POST.get('devtrans') == "1":
            ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=data['devtrans_id'],dkey_comment=data['devtrans_comment'],dkey_value1=None,dkey_value2=None,dkey_value3=None,dkey_rank=0)
            ddockeyw.save()
        if self.request.POST.get('devpower') == "1":
            ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=data['devpower_id'],dkey_comment=data['devpower_comment'],dkey_value1=self.request.POST.get('devpower_val1'),dkey_value2=None,dkey_value3=None,dkey_rank=0)
            ddockeyw.save()
        if self.request.POST.get('devwaste') == "1":
            ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=data['devwaste_id'],dkey_comment=data['devwaste_comment'],dkey_value1=None,dkey_value2=None,dkey_value3=None,dkey_rank=0)
            ddockeyw.save()

        dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc.pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1002).delete()
        
        for i in data['issues']:
            if i.keyw_pk == 2034:
                idockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=i,dkey_comment=data['dkey_comment_issues'],dkey_rank=0)
            else:
                idockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=i,dkey_rank=0)
            idockeyw.save()

        docreviews.objects.filter(drag_doc_fk=doc.pk).delete()

        for ra in data['ragencies']:
            docrev = docreviews(drag_doc_fk=doc,drag_rag_fk=ra,drag_rank=0,drag_copies=1)
            docrev.save()

        return super(reviewdetail_nop,self).form_valid(form)

class comment(ListView):
    template_name="ceqanet/comment.html"
    context_object_name = "comments"
    paginate_by = 25

    def get_queryset(self):
        queryset = CommentListQuery(self.request)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(comment, self).get_context_data(**kwargs)

        qsminuspage = self.request.GET.copy()
        
        if "page" in qsminuspage:
            qsminuspage.pop('page')

        context['restofqs'] = qsminuspage.urlencode()

        return context

def CommentListQuery(request):
    set_rag_fk = request.user.get_profile().set_rag_fk.rag_pk
    queryset = docreviews.objects.filter(drag_rag_fk__rag_pk=set_rag_fk).filter(drag_doc_fk__doc_review=True).order_by('-drag_doc_fk__doc_received')
    return queryset

class commentdetail_noc(FormView):
    form_class = commentdetailform
    template_name="ceqanet/commentdetail_noc.html"
 
    def get_success_url(self):
        success_url = "%s" % (reverse_lazy('comment'))
        return success_url

    def get_initial(self):
        initial = super(commentdetail_noc, self).get_initial()

        dr_query = docreviews.objects.get(drag_doc_fk__doc_pk=self.request.GET.get('doc_pk'),drag_rag_fk__rag_pk=self.request.user.get_profile().set_rag_fk.rag_pk)
        initial['drag_ragcomment'] = dr_query.drag_ragcomment
        return initial

    def get_context_data(self, **kwargs):
        context = super(commentdetail_noc, self).get_context_data(**kwargs)

        doc_pk = self.request.GET.get('doc_pk')
        context['detail'] = documents.objects.get(doc_pk__exact=self.request.GET.get('doc_pk'))
        context['doc_pk'] = doc_pk
        context['latlongs'] = latlongs.objects.filter(doc_pk=doc_pk)
        context['dev'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc_pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1010)
        context['actions'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc_pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1001)
        context['issues'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc_pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1002)
        context['reviews'] = docreviews.objects.filter(drag_doc_fk__doc_pk=doc_pk)
        context['file'] = docreviews.objects.get(drag_doc_fk__doc_pk=doc_pk,drag_rag_fk__rag_pk=self.request.user.get_profile().set_rag_fk.rag_pk)
        return context

    def form_valid(self,form):
        data = form.cleaned_data
        today = datetime.now()

        docreview = docreviews.objects.get(drag_doc_fk__doc_pk=self.request.GET.get('doc_pk'),drag_rag_fk__rag_pk=self.request.user.get_profile().set_rag_fk.rag_pk)

        docreview.drag_ragcomment = data['drag_ragcomment']
        if self.request.FILES['drag_file']:
            if docreview.drag_file:
                os.remove(os.path.join(settings.MEDIA_ROOT, docreview.drag_file.name))
            docreview.drag_file = self.request.FILES['drag_file']
        else:
            if docreview.drag_file:
                os.remove(os.path.join(settings.MEDIA_ROOT, docreview.drag_file.name))
                docreview.drag_file = None
        docreview.drag_received = today
        docreview.save()

        return super(commentdetail_noc,self).form_valid(form)

class commentdetail_nod(FormView):
    form_class = commentdetailform
    template_name="ceqanet/commentdetail_nod.html"
 
    def get_success_url(self):
        success_url = "%s" % (reverse_lazy('comment'))
        return success_url

    def get_initial(self):
        initial = super(commentdetail_nod, self).get_initial()

        dr_query = docreviews.objects.get(drag_pk__exact=self.request.GET.get('drag_pk'))
        initial['drag_ragcomment'] = dr_query.drag_ragcomment
        return initial

    def get_context_data(self, **kwargs):
        context = super(commentdetail_nod, self).get_context_data(**kwargs)

        doc_pk = self.request.GET.get('doc_pk')
        context['doc_pk'] = doc_pk
        context['detail'] = documents.objects.get(doc_pk__exact=self.request.GET.get('doc_pk'))
        context['drag_pk'] = self.request.GET.get('drag_pk')
        context['latlongs'] = latlongs.objects.filter(doc_pk=doc_pk)
        context['reviews'] = docreviews.objects.filter(drag_doc_fk__doc_pk=doc_pk)
        return context

    def form_valid(self,form):
        data = form.cleaned_data

        docreview = docreviews.objects.get(drag_pk=self.request.POST.get('drag_pk'))

        docreview.drag_ragcomment = data['drag_ragcomment']
        docreview.drag_file = self.request.FILES['dcmf_file']
        docreview.save()

        return super(commentdetail_nod,self).form_valid(form)

class commentdetail_noe(FormView):
    form_class = commentdetailform
    template_name="ceqanet/commentdetail_noe.html"
 
    def get_success_url(self):
        success_url = "%s" % (reverse_lazy('comment'))
        return success_url

    def get_initial(self):
        initial = super(commentdetail_noe, self).get_initial()

        dr_query = docreviews.objects.get(drag_pk__exact=self.request.GET.get('drag_pk'))
        initial['drag_ragcomment'] = dr_query.drag_ragcomment
        return initial

    def get_context_data(self, **kwargs):
        context = super(commentdetail_noe, self).get_context_data(**kwargs)

        doc_pk = self.request.GET.get('doc_pk')
        context['doc_pk'] = doc_pk
        context['detail'] = documents.objects.get(doc_pk__exact=self.request.GET.get('doc_pk'))
        context['drag_pk'] = self.request.GET.get('drag_pk')
        context['latlongs'] = latlongs.objects.filter(doc_pk=doc_pk)
        context['reviews'] = docreviews.objects.filter(drag_doc_fk__doc_pk=doc_pk)
        return context

    def form_valid(self,form):
        data = form.cleaned_data

        docreview = docreviews.objects.get(drag_pk=self.request.POST.get('drag_pk'))

        docreview.drag_ragcomment = data['drag_ragcomment']
        docreview.drag_file = self.request.FILES['dcmf_file']
        docreview.save()

        return super(commentdetail_noe,self).form_valid(form)

class commentdetail_nop(FormView):
    form_class = commentdetailform
    template_name="ceqanet/commentdetail_nop.html"
 
    def get_success_url(self):
        success_url = "%s" % (reverse_lazy('comment'))
        return success_url

    def get_initial(self):
        initial = super(commentdetail_nop, self).get_initial()

        dr_query = docreviews.objects.get(drag_pk__exact=self.request.GET.get('drag_pk'))
        initial['drag_ragcomment'] = dr_query.drag_ragcomment
        return initial

    def get_context_data(self, **kwargs):
        context = super(commentdetail_nop, self).get_context_data(**kwargs)

        doc_pk = self.request.GET.get('doc_pk')
        context['doc_pk'] = doc_pk
        context['detail'] = documents.objects.get(doc_pk__exact=self.request.GET.get('doc_pk'))
        context['drag_pk'] = self.request.GET.get('drag_pk')
        context['latlongs'] = latlongs.objects.filter(doc_pk=doc_pk)
        context['dev'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc_pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1010)
        context['actions'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc_pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1001)
        context['issues'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc_pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1002)
        context['reviews'] = docreviews.objects.filter(drag_doc_fk__doc_pk=doc_pk)
        return context

    def form_valid(self,form):
        data = form.cleaned_data

        docreview = docreviews.objects.get(drag_pk=self.request.POST.get('drag_pk'))

        docreview.drag_ragcomment = data['drag_ragcomment']
        docreview.drag_file = self.request.FILES['dcmf_file']
        docreview.save()

        return super(commentdetail_nop,self).form_valid(form)


def accept(request):
    t = loader.get_template("ceqanet/accept.html")
    c = RequestContext(request,{})
    return HttpResponse(t.render(c))

class usersettings(FormView):
    form_class = usersettingsform
    template_name="ceqanet/usersettings.html"

    def get_success_url(self):
        success_url = "%s" % (reverse_lazy('index'))
        return success_url

    def get_initial(self):
        initial = super(usersettings, self).get_initial()

        us_query = self.request.user.get_profile()
        initial['region'] = us_query.region
        initial['set_lag_fk'] = us_query.set_lag_fk.lag_pk
        initial['set_rag_fk'] = us_query.set_rag_fk.rag_pk
        initial['conphone'] = us_query.conphone
        return initial

    def get_context_data(self, **kwargs):
        context = super(usersettings, self).get_context_data(**kwargs)

        islead = False
        isplanner = False
        isreview = False
        for g in self.request.user.groups.all():
            if g.name == 'leads':
                islead = True
            if g.name == 'planners':
                isplanner = True
            if g.name == 'reviewers':
                isreview = True
        context['islead'] = islead
        context['isplanner'] = isplanner
        context['isreview'] = isreview

        return context

    def form_valid(self,form):
        data = form.cleaned_data

        region = data['region']
        if region == None:
            region = -1

        set_lag_fk = data['set_lag_fk']
        if set_lag_fk == None:
            set_lag_fk = leadagencies.objects.get(pk=0)

        set_rag_fk = data['set_rag_fk']
        if set_rag_fk == None:
            set_rag_fk = reviewingagencies.objects.get(pk=0)

        conphone = data['conphone']

        us = self.request.user.get_profile()
        us.region = region
        us.set_lag_fk = set_lag_fk
        us.set_rag_fk = set_rag_fk
        us.conphone = conphone
        us.save()

        return super(usersettings,self).form_valid(form)