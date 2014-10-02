import os
from django.template import RequestContext, Context, loader
from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponseRedirect
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import FormView,CreateView,UpdateView
from django.core.urlresolvers import reverse_lazy, reverse
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from ceqanet.forms import basicsearchform,prjlistform,doclistform,advancedsearchform,submitform,usersettingsform,attachmentsform,chqueryform,findprojectform,manageaccountform,requestupgrdform,manageupgradeform,manageusersform,manageuserform
from ceqanet.forms import nocform,nodform,noeform,nopform
from ceqanet.forms import editnocform,editnoeform,editnodform,editnopform
from ceqanet.forms import pendingdetailnocform,pendingdetailnodform,pendingdetailnoeform,pendingdetailnopform
from ceqanet.forms import addleadagencyform,addreviewingagencyform,addholidayform
from ceqanet.forms import reviewdetailnocform,reviewdetailnopform
from ceqanet.forms import commentaddform
from ceqanet.models import projects,documents,geowords,leadagencies,reviewingagencies,doctypes,dockeywords,docgeowords,docreviews,latlongs,counties,UserProfile,clearinghouse,keywords,docattachments,requestupgrade,doccomments,holidays
from ceqanet.forms import geocode, locationEditForm
#split geo imports for simplicity
from ceqanet.models import Locations
from django.contrib.auth.models import User,Group

from datetime import datetime
#vectorformats trick
from vectorformats.Formats import Django, GeoJSON, KML
#import simplejson
from django.utils import simplejson
from django.core import serializers
from ceqanet.functions import generate_schno,generate_biaschno,delete_clearinghouse_document,email_rejection,email_submission,email_inreview,email_upgraderejection,email_upgradeacceptance,email_commentacceptance,email_acceptance,email_requestforupgrade,email_assigned,email_demotiontodraft

import django.contrib.gis

def index(request):
    t = loader.get_template("ceqanet/index.html")
    c = RequestContext(request,{})
    return HttpResponse(t.render(c))

class basicsearch(FormView):
    template_name="ceqanet/basicsearch.html"
    form_class = basicsearchform

    def get_success_url(self):
        prj_schno = self.request.POST.get('prj_schno')
        colation = self.request.POST.get('colation')

        if colation == "project":
            success_url = "%s?prj_schno=%s&sortfld=-prj_schno&mode=basic" % (reverse_lazy('prjlist'),prj_schno)
        elif colation == "document":
            success_url = "%s?prj_schno=%s&sortfld=-doc_prj_fk__prj_schno&mode=basic" % (reverse_lazy('doclist'),prj_schno)
        return success_url

class advancedsearch(FormView):
    template_name="ceqanet/advancedsearch.html"
    form_class = advancedsearchform

    def get_success_url(self):
        rdodate = self.request.POST.get('rdodate')
        date_from = self.request.POST.get('date_from')
        date_to = self.request.POST.get('date_to')
        rdoplace = self.request.POST.get('rdoplace')
        cityid = self.request.POST.get('cityid')
        countyid = self.request.POST.get('countyid')
        rdolag = self.request.POST.get('rdolag')
        lagid = self.request.POST.get('lagid')
        rdorag = self.request.POST.get('rdorag')
        ragid = self.request.POST.get('ragid')
        rdodoctype = self.request.POST.get('rdodoctype')
        doctypeid = self.request.POST.get('doctypeid')
        rdolat = self.request.POST.get('rdolat')
        latid = self.request.POST.get('latid')
        rdodevtype = self.request.POST.get('rdodevtype')
        devtypeid = self.request.POST.get('devtypeid')
        rdoissue = self.request.POST.get('rdoissue')
        issueid = self.request.POST.get('issueid')
        rdotitle = self.request.POST.get('rdotitle')
        titlestr = self.request.POST.get('titlestr')
        rdodescription = self.request.POST.get('rdodescription')
        descriptionstr = self.request.POST.get('descriptionstr')
        colation = self.request.POST.get('colation')

        if colation == "project":
            success_url = reverse_lazy('prjlist') + "?"
            if rdodate == "range":
                success_url += "date_from=" + date_from + "&date_to=" + date_to + "&"
            if rdoplace == "city":
                success_url += "cityid=" + cityid + "&"
            elif rdoplace == "county":
                success_url += "countyid=" + countyid + "&"
            if rdolag == "agency":
                success_url += "lagid=" + lagid + "&"
            if rdorag == "agency":
                success_url += "ragid=" + ragid + "&"
            if rdodoctype == "type":
                success_url += "doctypeid=" + doctypeid + "&"
            if rdolat == "type":
                success_url += "latid=" + latid + "&"
            if rdodevtype == "type":
                success_url += "devtypeid=" + devtypeid + "&"
            if rdoissue == "issue":
                success_url += "issueid=" + issueid + "&"
            if rdotitle == "title":
                success_url += "titlestr=" + titlestr + "&"
            if rdodescription == "description":
                success_url += "descriptionstr=" + descriptionstr + "&"
            success_url += "sortfld=-prj_schno&mode=advanced"
        elif colation == "document":
            success_url = reverse_lazy('doclist') + "?"
            if rdodate == "range":
                success_url += "date_from=" + date_from + "&date_to=" + date_to + "&"
            if rdoplace == "city":
                success_url += "cityid=" + cityid + "&"
            elif rdoplace == "county":
                success_url += "countyid=" + countyid + "&"
            if rdolag == "agency":
                success_url += "lagid=" + lagid + "&"
            if rdorag == "agency":
                success_url += "ragid=" + ragid + "&"
            if rdodoctype == "type":
                success_url += "doctypeid=" + doctypeid + "&"
            if rdolat == "type":
                success_url += "latid=" + latid + "&"
            if rdodevtype == "type":
                success_url += "devtypeid=" + devtypeid + "&"
            if rdoissue == "issue":
                success_url += "issueid=" + issueid + "&"
            if rdotitle == "title":
                success_url += "titlestr=" + titlestr + "&"
            if rdodescription == "description":
                success_url += "descriptionstr=" + descriptionstr + "&"
            success_url += "sortfld=-doc_prj_fk__prj_schno&mode=advanced"
        return success_url

class prjlist(ListView):
    template_name="ceqanet/prjlist.html"
    context_object_name = "prjs"
    paginate_by = 25

    def get_queryset(self):
        mode = self.request.GET.get('mode')

        queryset = ""

        if mode == "basic":
            prj_schno = self.request.GET.get('prj_schno')
            sortfld = self.request.GET.get('sortfld')

            queryset = projects.objects.filter(prj_visible=True).filter(prj_schno__startswith=prj_schno).order_by(sortfld)
        elif mode == "advanced":
            date_from = self.request.GET.get('date_from')
            date_to = self.request.GET.get('date_to')
            cityid = self.request.GET.get('cityid')
            countyid = self.request.GET.get('countyid')
            lagid = self.request.GET.get('lagid')
            ragid = self.request.GET.get('ragid')
            doctypeid = self.request.GET.get('doctypeid')
            latid = self.request.GET.get('latid')
            devtypeid = self.request.GET.get('devtypeid')
            issueid = self.request.GET.get('issueid')
            titlestr = self.request.GET.get('titlestr')
            descriptionstr = self.request.GET.get('descriptionstr')
            sortfld = self.request.GET.get('sortfld')

            self.locname = "All"
            self.lagname = "All"
            self.ragname = "All"
            self.latname = "All"
            self.devtypename = "All"
            self.issuename = "All"
            self.titlestrname = "All"
            self.descriptionstrname = "All"
            self.docname = "All"

            queryset = projects.objects.filter(prj_visible=True).order_by(sortfld)
            if date_from:
                queryset = queryset.filter(prj_datefirst__gte=(date_from))
            if date_to:
                queryset = queryset.filter(prj_datelast__lte=(date_to))
            if cityid:
                queryset = queryset.filter(documents__docgeowords__dgeo_geow_fk__geow_pk=cityid)
                self.locname = "City of " + geowords.objects.get(pk=cityid).geow_shortname
            if countyid:
                queryset = queryset.filter(documents__docgeowords__dgeo_geow_fk__geow_pk=countyid)
                self.locname = geowords.objects.get(pk=countyid).geow_shortname + " County"
            if lagid:
                queryset = queryset.filter(prj_lag_fk__lag_pk=lagid)
                self.lagname = leadagencies.objects.get(pk=lagid).lag_name
            if ragid:
                queryset = queryset.filter(documents__docreviews__drag_rag_fk__rag_pk=ragid)
                self.ragname = reviewingagencies.objects.get(pk=ragid).rag_name
            if doctypeid:
                queryset = queryset.filter(prj_doc_fk__doc_doct_fk__keyw_pk=doctypeid)
                self.docname = doctypes.objects.get(pk=doctypeid).keyw_longname
            if latid:
                queryset = queryset.filter(documents__dockeywords__dkey_keyw_fk__keyw_pk=latid)
                self.latname = keywords.objects.get(pk=latid).keyw_longname
            if devtypeid:
                queryset = queryset.filter(documents__dockeywords__dkey_keyw_fk__keyw_pk=devtypeid)
                self.devtypename = keywords.objects.get(pk=devtypeid).keyw_longname
            if issueid:
                queryset = queryset.filter(documents__dockeywords__dkey_keyw_fk__keyw_pk=issueid)
                self.issuename = keywords.objects.get(pk=issueid).keyw_longname
            if titlestr:
                queryset = queryset.filter(prj_title__icontains=titlestr)
                self.titlestrname = titlestr
            if descriptionstr:
                queryset = queryset.filter(prj_description__icontains=descriptionstr)
                self.descriptionstrname = descriptionstr
        return queryset

    def get_context_data(self, **kwargs):
        context = super(prjlist, self).get_context_data(**kwargs)

        mode = self.request.GET.get('mode')
        context['mode'] = mode
        context['sortfld'] = self.request.GET.get('sortfld')
        if mode == "basic":
            context['prj_schno'] = self.request.GET.get('prj_schno')
        elif mode == "advanced":
            context['date_from'] = self.request.GET.get('date_from')
            context['date_to'] = self.request.GET.get('date_to')
            context['cityid'] = self.request.GET.get('cityid')
            context['countyid'] = self.request.GET.get('countyid')
            context['locname'] = self.locname
            context['lagid'] = self.request.GET.get('lagid')
            context['lagname'] = self.lagname
            context['ragid'] = self.request.GET.get('ragid')
            context['ragname'] = self.ragname
            context['doctypeid'] = self.request.GET.get('doctypeid')
            context['docname'] = self.docname
            context['latid'] = self.request.GET.get('latid')
            context['latname'] = self.latname
            context['devtypeid'] = self.request.GET.get('devtypeid')
            context['devtypename'] = self.devtypename
            context['issueid'] = self.request.GET.get('issueid')
            context['issuename'] = self.issuename
            context['titlestr'] = self.request.GET.get('titlestr')
            context['titlestrname'] = self.titlestrname
            context['descriptionstr'] = self.request.GET.get('descriptionstr')
            context['descriptionstrname'] = self.descriptionstrname

        qsminuspage = self.request.GET.copy()
        
        if "page" in qsminuspage:
            qsminuspage.pop('page')

        context['restofqs'] = qsminuspage.urlencode()
        context['form'] = prjlistform()
        
        return context

class doclist(ListView):
    template_name="ceqanet/doclist.html"
    context_object_name = "docs"
    paginate_by = 25

    def get_queryset(self):
        mode = self.request.GET.get('mode')

        queryset = ""

        if mode == "basic":
            prj_schno = self.request.GET.get('prj_schno')
            sortfld = self.request.GET.get('sortfld')

            queryset = documents.objects.filter(doc_visible=True).filter(doc_prj_fk__prj_schno__startswith=prj_schno).order_by(sortfld)
        elif mode == "advanced":
            date_from = self.request.GET.get('date_from')
            date_to = self.request.GET.get('date_to')
            cityid = self.request.GET.get('cityid')
            countyid = self.request.GET.get('countyid')
            lagid = self.request.GET.get('lagid')
            ragid = self.request.GET.get('ragid')
            doctypeid = self.request.GET.get('doctypeid')
            latid = self.request.GET.get('latid')
            devtypeid = self.request.GET.get('devtypeid')
            issueid = self.request.GET.get('issueid')
            titlestr = self.request.GET.get('titlestr')
            descriptionstr = self.request.GET.get('descriptionstr')
            sortfld = self.request.GET.get('sortfld')

            self.locname = "All"
            self.lagname = "All"
            self.ragname = "All"
            self.latname = "All"
            self.devtypename = "All"
            self.issuename = "All"
            self.titlestrname = "All"
            self.descriptionstrname = "All"
            self.docname = "All"

            queryset = documents.objects.filter(doc_visible=True).order_by(sortfld)
            if date_from:
                queryset = queryset.filter(doc_received__range=(date_from,date_to))
            if cityid:
                queryset = queryset.filter(docgeowords__dgeo_geow_fk__geow_pk=cityid)
                self.locname = "City of " + geowords.objects.get(pk=cityid).geow_shortname
            elif countyid:
                queryset = queryset.filter(docgeowords__dgeo_geow_fk__geow_pk=countyid)
                self.locname = geowords.objects.get(pk=countyid).geow_shortname + " County"
            if lagid:
                queryset = queryset.filter(doc_prj_fk__prj_lag_fk__lag_pk=lagid)
                self.lagname = leadagencies.objects.get(pk=lagid).lag_name
            if ragid:
                queryset = queryset.filter(docreviews__drag_rag_fk__rag_pk=ragid)
                self.ragname = reviewingagencies.objects.get(pk=ragid).rag_name
            if doctypeid:
                queryset = queryset.filter(doc_doct_fk__keyw_pk=doctypeid)
                self.docname = doctypes.objects.get(pk=doctypeid).keyw_longname
            if latid:
                queryset = queryset.filter(dockeywords__dkey_keyw_fk__keyw_pk=latid)
                self.latname = keywords.objects.get(pk=latid).keyw_longname
            if devtypeid:
                queryset = queryset.filter(dockeywords__dkey_keyw_fk__keyw_pk=devtypeid)
                self.devtypename = keywords.objects.get(pk=devtypeid).keyw_longname
            if issueid:
                queryset = queryset.filter(dockeywords__dkey_keyw_fk__keyw_pk=issueid)
                self.issuename = keywords.objects.get(pk=issueid).keyw_longname
            if titlestr:
                queryset = queryset.filter(doc_prj_fk__prj_title__icontains=titlestr)
                self.titlestrname = titlestr
            if descriptionstr:
                queryset = queryset.filter(doc_prj_fk__prj_description__icontains=descriptionstr)
                self.descriptionstrname = descriptionstr
        return queryset

    def get_context_data(self, **kwargs):
        context = super(doclist, self).get_context_data(**kwargs)

        mode = self.request.GET.get('mode')
        context['mode'] = mode
        context['sortfld'] = self.request.GET.get('sortfld')
        if mode == "basic":
            context['prj_schno'] = self.request.GET.get('prj_schno')
        elif mode == "advanced":
            context['date_from'] = self.request.GET.get('date_from')
            context['date_to'] = self.request.GET.get('date_to')
            context['cityid'] = self.request.GET.get('cityid')
            context['countyid'] = self.request.GET.get('countyid')
            context['locname'] = self.locname
            context['lagid'] = self.request.GET.get('lagid')
            context['lagname'] = self.lagname
            context['ragid'] = self.request.GET.get('ragid')
            context['ragname'] = self.ragname
            context['doctypeid'] = self.request.GET.get('doctypeid')
            context['docname'] = self.docname
            context['latid'] = self.request.GET.get('latid')
            context['latname'] = self.latname
            context['devtypeid'] = self.request.GET.get('devtypeid')
            context['devtypename'] = self.devtypename
            context['issueid'] = self.request.GET.get('issueid')
            context['issuename'] = self.issuename
            context['titlestr'] = self.request.GET.get('titlestr')
            context['titlestrname'] = self.titlestrname
            context['descriptionstr'] = self.request.GET.get('descriptionstr')
            context['descriptionstrname'] = self.descriptionstrname

        qsminuspage = self.request.GET.copy()
        
        if "page" in qsminuspage:
            qsminuspage.pop('page')

        context['restofqs'] = qsminuspage.urlencode()
        context['form'] = doclistform()
        
        return context

class submit(FormView):
    template_name="ceqanet/submit.html"
    form_class = submitform

    def get_success_url(self):
        doctype = self.request.POST.get('doctype')
        prjtoggle = self.request.POST.get('prjtoggle')

        if prjtoggle == "yes":
            success_url = "%s?doctype=%s" % (reverse_lazy('chquery'),doctype)
        elif prjtoggle == "no":
            if doctype == '108':
                success_url = "%s?doctype=%s&prj_pk=%s" % (reverse_lazy('docadd_nod'),doctype,None)
            elif doctype == '109':
                success_url = "%s?doctype=%s&prj_pk=%s" % (reverse_lazy('docadd_noe'),doctype,None)
            elif doctype == '102':
                success_url = "%s?doctype=%s&prj_pk=%s" % (reverse_lazy('docadd_nop'),doctype,None)
            else:
                success_url = "%s?doctype=%s&prj_pk=%s" % (reverse_lazy('docadd_noc'),doctype,None)
        return success_url

    def get_context_data(self, **kwargs):
        context = super(submit, self).get_context_data(**kwargs)

        context['laginfo'] = leadagencies.objects.get(pk=self.request.user.get_profile().set_lag_fk.lag_pk)
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(submit, self).dispatch(*args, **kwargs)

class draftsbylag(ListView):
    template_name ="ceqanet/draftsbylag.html"
    context_object_name = "draftsbylag"
    paginate_by = 25

    def get_queryset(self):
        queryset = DraftsByLAGQuery(self.request)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(draftsbylag, self).get_context_data(**kwargs)

        qsminuspage = self.request.GET.copy()
        
        if "page" in qsminuspage:
            qsminuspage.pop('page')

        context['restofqs'] = qsminuspage.urlencode()

        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(draftsbylag, self).dispatch(*args, **kwargs)

def DraftsByLAGQuery(request):
    queryset = documents.objects.filter(projects__prj_lag_fk__lag_pk=request.user.get_profile().set_lag_fk.lag_pk).filter(doc_draft=True)
    return queryset

class pendingsbylag(ListView):
    template_name ="ceqanet/pendingsbylag.html"
    context_object_name = "pendingsbylag"

    def get_queryset(self):
        queryset = PendingsByLAGQuery(self.request)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(pendingsbylag, self).get_context_data(**kwargs)

        qsminuspage = self.request.GET.copy()
        
        if "page" in qsminuspage:
            qsminuspage.pop('page')

        context['restofqs'] = qsminuspage.urlencode()
        context['la'] = self.request.user.get_profile().set_lag_fk.lag_name

        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(pendingsbylag, self).dispatch(*args, **kwargs)

def PendingsByLAGQuery(request):
    queryset = documents.objects.filter(projects__prj_lag_fk__lag_pk=request.user.get_profile().set_lag_fk.lag_pk).filter(doc_pending=True).order_by('-doc_received','-doc_pk')
    return queryset

class reviewsbylag(ListView):
    template_name="ceqanet/reviewsbylag.html"
    context_object_name = "reviewsbylag"
    paginate_by = 25

    def get_queryset(self):
        queryset = ReviewsByLAGQuery(self.request)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(reviewsbylag, self).get_context_data(**kwargs)

        qsminuspage = self.request.GET.copy()
        
        if "page" in qsminuspage:
            qsminuspage.pop('page')

        context['restofqs'] = qsminuspage.urlencode()
        context['la'] = self.request.user.get_profile().set_lag_fk.lag_name

        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(reviewsbylag, self).dispatch(*args, **kwargs)

def ReviewsByLAGQuery(request):
    queryset = documents.objects.filter(projects__prj_lag_fk__lag_pk=request.user.get_profile().set_lag_fk.lag_pk).filter(doc_review=True).order_by('-doc_received','-doc_pk')
    return queryset

class chquery(FormView):
    template_name="ceqanet/chquery.html"
    form_class = chqueryform

    def get_success_url(self):
        success_url = "%s?prj_schno=%s&doctype=%s&leadorresp=%s&nodagency=%s" % (reverse_lazy('findproject'),self.prj_schno,self.doctype,self.leadorresp,self.nodagency)
        return success_url

    def get_initial(self):
        initial = super(chquery, self).get_initial()

        initial['doctype'] = self.request.GET.get("doctype")
        initial['leadorresp'] = 'lead'

        return initial

    def get_context_data(self, **kwargs):
        context = super(chquery, self).get_context_data(**kwargs)

        context['doctype'] = self.request.GET.get('doctype')
        context['laglist'] = leadagencies.objects.get(pk=self.request.user.get_profile().set_lag_fk.lag_pk)

        return context

    def form_valid(self,form):
        data = form.cleaned_data
        self.prj_schno = data['prj_schno']
        self.doctype = data['doctype']
        self.leadorresp = data['leadorresp']
        if data['nodagency'] != None:
            self.nodagency = data['nodagency'].lag_pk
        else:
            self.nodagency = None
        return super(chquery,self).form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(chquery, self).dispatch(*args, **kwargs)

class findproject(FormView):
    template_name="ceqanet/findproject.html"
    form_class = findprojectform

    def get_success_url(self):
        if self.doctype == '108':
            success_url = "%s?doctype=%s&prj_pk=%s&leadorresp=%s&nodagency=%s" % (reverse_lazy('docadd_nod'),self.doctype,self.prj_pk,self.leadorresp,self.nodagency)
        elif self.doctype == '109':
            success_url = "%s?doctype=%s&prj_pk=%s" % (reverse_lazy('docadd_noe'),self.doctype,self.prj_pk)
        elif self.doctype == '102':
            success_url = "%s?doctype=%s&prj_pk=%s" % (reverse_lazy('docadd_nop'),self.doctype,self.prj_pk)
        else:
            success_url = "%s?doctype=%s&prj_pk=%s" % (reverse_lazy('docadd_noc'),self.doctype,self.prj_pk)
        return success_url

    def get_context_data(self, **kwargs):
        context = super(findproject, self).get_context_data(**kwargs)

        prj_schno = self.request.GET.get('prj_schno')
        usr = User.objects.get(pk=self.request.user.pk)

        for g in usr.groups.all():
            if g.name == "planners" or g.name == "clearinghouse":
                context['schnos'] = projects.objects.filter(prj_visible=True).filter(prj_schno__startswith=prj_schno).order_by('-prj_schno')
            if g.name == "leads":
                if self.request.GET.get('leadorresp') == 'lead':
                    context['schnos'] = projects.objects.filter(prj_visible=True).filter(prj_schno__startswith=prj_schno).filter(prj_lag_fk__lag_pk=self.request.user.get_profile().set_lag_fk.lag_pk).order_by('-prj_schno')
                else:
                    context['schnos'] = projects.objects.filter(prj_visible=True).filter(prj_schno__startswith=prj_schno).filter(prj_lag_fk__lag_pk=self.request.GET.get('nodagency')).order_by('-prj_schno')
        context['doctype'] = self.request.GET.get('doctype')
        context['leadorresp'] = self.request.GET.get('leadorresp')
        context['nodagency'] = self.request.GET.get('nodagency')

        return context

    def form_valid(self,form):
        self.prj_pk = self.request.POST.get('prj_pk')
        self.doctype = self.request.POST.get('doctype')
        self.leadorresp = self.request.POST.get('leadorresp')
        self.nodagency = self.request.POST.get('nodagency')
        return super(findproject,self).form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(findproject, self).dispatch(*args, **kwargs)

class attachments(FormView):
    template_name="ceqanet/attachments.html"
    form_class = attachmentsform    
    
    def get_success_url(self):
        if self.request.POST.get('mode') == 'attach':
            success_url = "%s?doc_pk=%s" % (reverse_lazy('attachments'),self.request.POST.get('doc_pk'))
        elif self.request.POST.get('mode') == 'delete':
            success_url = "%s" % reverse_lazy('draftsbylag')
        elif self.request.POST.get('mode') == 'remove':
            success_url = "%s?doc_pk=%s" % (reverse_lazy('attachments'),self.request.POST.get('doc_pk'))
        elif self.request.POST.get('mode') == 'draft':
            success_url = "%s" % reverse_lazy('draftsbylag')
        elif self.request.POST.get('mode') == 'submitch':
            success_url = "%s" % reverse_lazy('accept')
        return success_url

    def get_context_data(self, **kwargs):
        context = super(attachments , self).get_context_data(**kwargs)

        doc_pk = self.request.GET.get('doc_pk')
        context['doc_pk'] = doc_pk
        context['doc'] = documents.objects.get(pk=doc_pk)
        context['attachments'] = docattachments.objects.filter(datt_doc_fk=doc_pk)

        return context

    def form_valid(self,form):
        doc = documents.objects.get(pk=self.request.POST.get('doc_pk'))

        if self.request.POST.get('mode') == 'attach':
            if self.request.FILES['datt_file']:
                docatt = docattachments(datt_doc_fk=doc,datt_file=self.request.FILES['datt_file'])
                docatt.save()
        elif self.request.POST.get('mode') == 'remove':
            docatts = docattachments.objects.filter(datt_pk=self.request.POST.get('attpk'))
            for att in docatts:
                os.remove(os.path.join(settings.MEDIA_ROOT, att.datt_file.name))
            docatts.delete()            
        elif self.request.POST.get('mode') == 'delete':
            delete_clearinghouse_document(self)
        elif self.request.POST.get('mode') == 'submitch':
            doc.doc_draft = False
            doc.doc_pending = True
            doc.save()
        
            if settings.SENDEMAIL:
                email_submission(self,doc)

        return super(attachments,self).form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(attachments, self).dispatch(*args, **kwargs)

class docadd_noc(FormView):
    template_name="ceqanet/docadd_noc.html"
    form_class = nocform

    def get_success_url(self):
        success_url = "%s?doc_pk=%s" % (reverse_lazy('attachments'),self.doc_pk)
        return success_url

    def get_initial(self):
        initial = super(docadd_noc, self).get_initial()

        if self.request.GET.get("doctype") != 'None':
            initial['doctypeid'] = self.request.GET.get("doctype")

        if self.request.GET.get("prj_pk") != 'None':
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
        context = super(docadd_noc, self).get_context_data(**kwargs)

        prj_pk = self.request.GET.get("prj_pk")
        context['prj_pk'] = prj_pk
        context['doctype'] = self.request.GET.get("doctype")
        if prj_pk != 'None':
            context['prjinfo'] = projects.objects.get(prj_pk__exact=self.request.GET.get("prj_pk"))
        context['laglist'] = leadagencies.objects.get(pk=self.request.user.get_profile().set_lag_fk.lag_pk)

        return context
    
    def form_valid(self,form):
        data = form.cleaned_data
        today = datetime.now()
        doc_received = today
        lag = leadagencies.objects.get(pk=self.request.user.get_profile().set_lag_fk.lag_pk)
        doc = documents.objects.get(pk=0)
        cnty_fk = counties.objects.get(pk=0)

        doc_title = None
        doc_description = None
        doc_conaddress2 = None
        doc_parcelno = None
        doc_xstreets = None
        doc_township = None
        doc_range = None
        doc_section = None
        doc_base = None
        doc_highways = None
        doc_airports = None
        doc_railways = None
        doc_waterways = None
        doc_landuse = None
        doc_schools = None

        if data['doc_title']:
            doc_title = data['doc_title']
        if data['doc_description']:
            doc_description = data['doc_description']
        if data['doc_conaddress2']:
            doc_conaddress2 = data['doc_conaddress2']
        if data['doc_parcelno']:
            doc_parcelno = data['doc_parcelno']
        if data['doc_xstreets']:
            doc_xstreets = data['doc_xstreets']
        if data['doc_township']:
            doc_township = data['doc_township']
        if data['doc_range']:
            doc_range = data['doc_range']
        if data['doc_section']:
            doc_section = data['doc_section']
        if data['doc_base']:
            doc_base = data['doc_base']
        if data['doc_highways']:
            doc_highways = data['doc_highways']
        if data['doc_airports']:
            doc_airports = data['doc_airports']
        if data['doc_railways']:
            doc_railways = data['doc_railways']
        if data['doc_waterways']:
            doc_waterways = data['doc_waterways']
        if data['doc_landuse']:
            doc_landuse = data['doc_landuse']
        if data['doc_schools']:
            doc_schools = data['doc_schools']

        if self.request.POST.get('prj_pk') == 'None':
            prj = projects(prj_lag_fk=lag,prj_doc_fk=doc,prj_status=data['doctypeid'].keyw_shortname,prj_title=data['prj_title'],prj_description=data['prj_description'],prj_leadagency=lag.lag_name,prj_datefirst=today,prj_datelast=today)
            prj.save()
        else:
            prj = projects.objects.get(pk=self.request.POST.get('prj_pk'))
            prj.prj_status = data['doctypeid'].keyw_shortname
            prj.prj_datelast = today
            prj.save()

        doc_statewide = False

        if data['statewide'] == 'yes':
            doc_statewide = True

        doc_county = ""

        if data['statewide'] == 'no':
            for cnty in data['counties']:
                doc_county += cnty.geow_shortname + ","

            doc_county = doc_county[:-1]
            if len(doc_county) > 64:
                doc_county = doc_county[:64]

        doc_city = ""

        if data['statewide'] == 'no':
            for cty in data['cities']:
                doc_city += cty.geow_shortname + ","

            doc_city = doc_city[:-1]
            if len(doc_city) > 64:
                doc_city = doc_city[:64]

        adddoc = documents(doc_prj_fk=prj,doc_cnty_fk=cnty_fk,doc_doct_fk=data['doctypeid'],doc_doctype=data['doctypeid'].keyw_shortname,doc_docname=data['doctypeid'].keyw_longname,doc_title=data['doc_title'],doc_description=data['doc_description'],doc_conname=data['doc_conname'],doc_conagency=lag.lag_name,doc_conemail=data['doc_conemail'],doc_conphone=data['doc_conphone'],doc_conaddress1=data['doc_conaddress1'],doc_conaddress2=doc_conaddress2,doc_concity=data['doc_concity'],doc_constate=data['doc_constate'],doc_conzip=data['doc_conzip'],doc_location=data['doc_location'],doc_city=doc_city,doc_county=doc_county,doc_draft=1,doc_pending=0,doc_received=doc_received,doc_added=today,doc_parcelno=doc_parcelno,doc_xstreets=doc_xstreets,doc_township=doc_township,doc_range=doc_range,doc_section=doc_section,doc_base=doc_base,doc_highways=doc_highways,doc_airports=doc_airports,doc_railways=doc_railways,doc_waterways=doc_waterways,doc_landuse=doc_landuse,doc_schools=doc_schools,doc_added_userid=self.request.user,doc_assigned_userid=User.objects.get(pk=-1),doc_lastlooked_userid=User.objects.get(pk=-1))
        adddoc.save()

        if data['statewide'] == 'no':
            for cnty in data['counties']:
                geowrds_cnty = docgeowords(dgeo_geow_fk=cnty,dgeo_doc_fk=adddoc,dgeo_rank=1)
                geowrds_cnty.save()

            for cty in data['cities']:
                geowrds_city = docgeowords(dgeo_geow_fk=cty,dgeo_doc_fk=adddoc,dgeo_rank=1)
                geowrds_city.save()

        geometry = Locations(document=adddoc,geom=data['geom'])
        geometry.save()

        coords = latlongs(doc_pk=adddoc.pk,doc_prj_fk=prj,doc_doctype=data['doctypeid'].keyw_shortname,doc_latitude=data['doc_latitude'],doc_longitude=data['doc_longitude'])
        coords.save()

        for a in data['actions']:
            if a.keyw_pk == 1018:
                adockeyw = dockeywords(dkey_doc_fk=adddoc,dkey_keyw_fk=a,dkey_comment=data['dkey_comment_actions'],dkey_rank=0)
            else:
                adockeyw = dockeywords(dkey_doc_fk=adddoc,dkey_keyw_fk=a,dkey_rank=0)
            adockeyw.save()

        devtypes = keywords.objects.filter(keyw_keyl_fk__keyl_pk=1010).filter(keyw_pk__gte=6001).filter(keyw_pk__lte=11001)
        for d in devtypes:
            if self.request.POST.get('dev'+str(d.keyw_pk)):
                if d.keyw_pk == 11001:
                    ddockeyw = dockeywords(dkey_doc_fk=adddoc,dkey_keyw_fk=d,dkey_comment=self.request.POST.get('dkey_comment_dev'),dkey_value1=self.request.POST.get('dev'+str(d.keyw_pk)+'_val1'),dkey_value2=self.request.POST.get('dev'+str(d.keyw_pk)+'_val2'),dkey_value3=self.request.POST.get('dev'+str(d.keyw_pk)+'_val3'),dkey_rank=0)
                else:
                    ddockeyw = dockeywords(dkey_doc_fk=adddoc,dkey_keyw_fk=d,dkey_value1=self.request.POST.get('dev'+str(d.keyw_pk)+'_val1'),dkey_value2=self.request.POST.get('dev'+str(d.keyw_pk)+'_val2'),dkey_value3=self.request.POST.get('dev'+str(d.keyw_pk)+'_val3'),dkey_rank=0)
                ddockeyw.save()
        if data['devtrans']:
            ddockeyw = dockeywords(dkey_doc_fk=adddoc,dkey_keyw_fk=data['devtrans_id'],dkey_comment=data['devtrans_comment'],dkey_value1=None,dkey_value2=None,dkey_value3=None,dkey_rank=0)
            ddockeyw.save()
        if data['devpower']:
            ddockeyw = dockeywords(dkey_doc_fk=adddoc,dkey_keyw_fk=data['devpower_id'],dkey_comment=data['devpower_comment'],dkey_value1=data['devpower_val1'],dkey_value2=None,dkey_value3=None,dkey_rank=0)
            ddockeyw.save()
        if data['devwaste']:
            ddockeyw = dockeywords(dkey_doc_fk=adddoc,dkey_keyw_fk=data['devwaste_id'],dkey_comment=data['devwaste_comment'],dkey_value1=None,dkey_value2=None,dkey_value3=None,dkey_rank=0)
            ddockeyw.save()

        for i in data['issues']:
            if i.keyw_pk == 2034:
                idockeyw = dockeywords(dkey_doc_fk=adddoc,dkey_keyw_fk=i,dkey_comment=data['dkey_comment_issues'],dkey_rank=0)
            else:
                idockeyw = dockeywords(dkey_doc_fk=adddoc,dkey_keyw_fk=i,dkey_rank=0)
            idockeyw.save()

        for ra in data['ragencies']:
            docrev = docreviews(drag_doc_fk=adddoc,drag_rag_fk=ra,drag_rank=0,drag_copies=1,drag_numcomments=0)
            docrev.save()

        prj.prj_doc_fk=adddoc
        prj.save()

        self.doc_pk = adddoc.pk

        return super(docadd_noc,self).form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(docadd_noc, self).dispatch(*args, **kwargs)

class docadd_nod(FormView):
    template_name="ceqanet/docadd_nod.html"
    form_class = nodform

    def get_success_url(self):
        success_url = "%s?doc_pk=%s" % (reverse_lazy('attachments'),self.doc_pk)
        return success_url

    def get_initial(self):
        initial = super(docadd_nod, self).get_initial()

        if self.request.GET.get("prj_pk") != 'None':
            prjinfo = projects.objects.get(prj_pk__exact=self.request.GET.get("prj_pk"))
            initial['prj_title'] = prjinfo.prj_title
            initial['prj_applicant'] = prjinfo.prj_applicant
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

        if self.request.GET.get("leadorresp") != None:
            initial['leadorresp'] = self.request.GET.get("leadorresp")
        if self.request.GET.get("nodagency") != None:
            initial['doc_nodagency'] = self.request.GET.get("nodagency")
        return initial

    def get_context_data(self, **kwargs):
        context = super(docadd_nod, self).get_context_data(**kwargs)

        prj_pk = self.request.GET.get("prj_pk")
        context['prj_pk'] = prj_pk
        context['doctype'] = self.request.GET.get("doctype")
        #context['leadorresp'] = self.request.GET.get("leadorresp")
        #context['nodagency'] = leadagencies.objects.get(pk=self.request.GET.get("nodagency"))
        if prj_pk != 'None':
            context['prjinfo'] = projects.objects.get(prj_pk__exact=self.request.GET.get("prj_pk"))
        context['laglist'] = leadagencies.objects.get(pk=self.request.user.get_profile().set_lag_fk.lag_pk)
        return context

    def form_valid(self,form):
        data = form.cleaned_data
        today = datetime.now()
        doc_received = today
        lag = leadagencies.objects.get(pk=self.request.user.get_profile().set_lag_fk.lag_pk)
        doc = documents.objects.get(pk=0)
        cnty_fk = counties.objects.get(pk=0)
        doct = doctypes.objects.get(pk=self.request.POST.get('doctype'))

        doc_title = None
        doc_description = None
        doc_conaddress2 = None
        doc_nodbylead = None
        doc_nodbyresp = None
        doc_detsigeffect = None
        doc_detnotsigeffect = None
        doc_deteir = None
        doc_detnegdec = None
        doc_detmitigation = None
        doc_detnotmitigation = None
        doc_detconsider = None
        doc_detnotconsider = None
        doc_detfindings = None
        doc_detnotfindings = None
        
        if data['doc_title']:
            doc_title = data['doc_title']
        if data['doc_description']:
            doc_description = data['doc_description']
        if data['doc_conaddress2']:
            doc_conaddress2 = data['doc_conaddress2']

        if data['leadorresp']:
            if data['leadorresp'] == 'lead':
                doc_nodbylead = True
                doc_nodbyresp = False
            elif data['leadorresp'] == 'resp':
                doc_nodbylead = False
                doc_nodbyresp = True

        #doc_nodagency = leadagencies.objects.get(pk=data["doc_nodagency"])

        if data['det1']:
            if data['det1'] == 'True':
                doc_detsigeffect = True
                doc_detnotsigeffect = False
            elif data['det1'] == 'False':
                doc_detsigeffect = False
                doc_detnotsigeffect = True
        if data['det2']:
            if data['det2'] == 'True':
                doc_deteir = True
                doc_detnegdec = False
            elif data['det2'] == 'False':
                doc_deteir = False
                doc_detnegdec = True
        if data['det3']:
            if data['det3'] == 'True':
                doc_detmitigation = True
                doc_detnotmitigation = False
            elif data['det3'] == 'False':
                doc_detmitigation = False
                doc_detnotmitigation = True
        if data['det4']:
            if data['det4'] == 'True':
                doc_detconsider = True
                doc_detnotconsider = False
            elif data['det4'] == 'False':
                doc_detconsider = False
                doc_detnotconsider = True
        if data['det5']:
            if data['det5'] == 'True':
                doc_detfindings = True
                doc_detnotfindings = False
            elif data['det5'] == 'False':
                doc_detfindings = False
                doc_detnotfindings = True

        if data['doc_nodfeespaid']:
            if data['doc_nodfeespaid'] == 'yes':
                doc_nodfeespaid = True
            elif data['doc_nodfeespaid'] == 'no':
                doc_nodfeespaid = False

        if self.request.POST.get('prj_pk') == 'None':
            prj = projects(prj_lag_fk=lag,prj_doc_fk=doc,prj_status=doct.keyw_shortname,prj_title=data['prj_title'],prj_description=data['prj_description'],prj_leadagency=lag.lag_name,prj_datefirst=today,prj_datelast=today,prj_applicant=data['prj_applicant'])
            prj.save()
        else:
            prj = projects.objects.get(pk=self.request.POST.get('prj_pk'))
            prj.prj_status = doct.keyw_shortname
            prj.prj_datelast = today
            prj.save()

        doc_statewide = False

        if data['statewide'] == 'yes':
            doc_statewide = True

        doc_county = ""

        if data['statewide'] == 'no':
            for cnty in data['counties']:
                doc_county += cnty.geow_shortname + ","

            doc_county = doc_county[:-1]
            if len(doc_county) > 64:
                doc_county = doc_county[:64]

        doc_city = ""

        if data['statewide'] == 'no':
            for cty in data['cities']:
                doc_city += cty.geow_shortname + ","

            doc_city = doc_city[:-1]
            if len(doc_city) > 64:
                doc_city = doc_city[:64]

        adddoc = documents(doc_prj_fk=prj,doc_cnty_fk=cnty_fk,doc_doct_fk=doct,doc_doctype=doct.keyw_shortname,doc_docname=doct.keyw_longname,doc_title=doc_title,doc_description=doc_description,doc_conname=data['doc_conname'],doc_conagency=lag.lag_name,doc_conemail=data['doc_conemail'],doc_conphone=data['doc_conphone'],doc_conaddress1=data['doc_conaddress1'],doc_conaddress2=doc_conaddress2,doc_concity=data['doc_concity'],doc_constate=data['doc_constate'],doc_conzip=data['doc_conzip'],doc_location=data['doc_location'],doc_county=doc_county,doc_city=doc_city,doc_draft=1,doc_pending=0,doc_received=doc_received,doc_added=today,doc_nodbylead=doc_nodbylead,doc_nodbyresp=doc_nodbyresp,doc_nodagency=data['doc_nodagency'].lag_name,doc_nod=data['doc_nod'],doc_detsigeffect=doc_detsigeffect,doc_detnotsigeffect=doc_detnotsigeffect,doc_deteir=doc_deteir,doc_detnegdec=doc_detnegdec,doc_detmitigation=doc_detmitigation,doc_detnotmitigation=doc_detnotmitigation,doc_detconsider=doc_detconsider,doc_detnotconsider=doc_detnotconsider,doc_detfindings=doc_detfindings,doc_detnotfindings=doc_detnotfindings,doc_eiravailableat=data['doc_eiravailableat'],doc_added_userid=self.request.user,doc_assigned_userid=User.objects.get(pk=-1),doc_lastlooked_userid=User.objects.get(pk=-1),doc_nodfeespaid=doc_nodfeespaid)
        adddoc.save()

        if data['statewide'] == 'no':
            for cnty in data['counties']:
                geowrds_cnty = docgeowords(dgeo_geow_fk=cnty,dgeo_doc_fk=adddoc,dgeo_rank=1)
                geowrds_cnty.save()
            for cty in data['cities']:
                geowrds_city = docgeowords(dgeo_geow_fk=cty,dgeo_doc_fk=adddoc,dgeo_rank=1)
                geowrds_city.save()

        geometry = Locations(document=adddoc,geom=data['geom'])
        geometry.save()

        coords = latlongs(doc_pk=adddoc.pk,doc_prj_fk=prj,doc_doctype=doct.keyw_shortname,doc_latitude=data['doc_latitude'],doc_longitude=data['doc_longitude'])
        coords.save()

        prj.prj_doc_fk=adddoc
        prj.save()

        self.doc_pk = adddoc.pk

        if settings.SENDEMAIL:
            email_submission(self,adddoc)

        return super(docadd_nod,self).form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(docadd_nod, self).dispatch(*args, **kwargs)

class docadd_noe(FormView):
    template_name="ceqanet/docadd_noe.html"
    form_class = noeform

    def get_success_url(self):
        success_url = "%s?doc_pk=%s" % (reverse_lazy('attachments'),self.doc_pk)
        return success_url

    def get_initial(self):
        initial = super(docadd_noe, self).get_initial()

        if self.request.GET.get("prj_pk") != 'None':
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

        prj_pk = self.request.GET.get("prj_pk")
        context['prj_pk'] = prj_pk
        context['doctype'] = self.request.GET.get("doctype")
        if prj_pk != 'None':
            context['prjinfo'] = projects.objects.get(prj_pk__exact=self.request.GET.get("prj_pk"))
        context['laglist'] = leadagencies.objects.get(pk=self.request.user.get_profile().set_lag_fk.lag_pk)
        return context

    def form_valid(self,form):
        data = form.cleaned_data
        today = datetime.now()
        doc_received = today
        lag = leadagencies.objects.get(pk=self.request.user.get_profile().set_lag_fk.lag_pk)
        doc = documents.objects.get(pk=0)
        cnty_fk = counties.objects.get(pk=0)
        doct = doctypes.objects.get(pk=self.request.POST.get('doctype'))

        doc_title = None
        doc_description = None
        doc_conaddress2 = None
        doc_exministerial = False
        doc_exdeclared = False
        doc_exemergency = False
        doc_excategorical = False
        doc_exstatutory = False
        doc_exnumber = None
        status = None

        if data['doc_title']:
            doc_title = data['doc_title']
        if data['doc_description']:
            doc_description = data['doc_description']
        if data['doc_conaddress2']:
            doc_conaddress2 = data['doc_conaddress2']

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

        if self.request.POST.get('prj_pk') == 'None':
            prj = projects(prj_lag_fk=lag,prj_doc_fk=doc,prj_status=doct.keyw_shortname,prj_title=data['prj_title'],prj_description=data['prj_description'],prj_leadagency=lag.lag_name,prj_datefirst=today,prj_datelast=today)
            prj.save()
        else:
            prj = projects.objects.get(pk=self.request.POST.get('prj_pk'))
            prj.prj_status = doct.keyw_shortname
            prj.prj_datelast = today
            prj.save()

        doc_statewide = False

        if data['statewide'] == 'yes':
            doc_statewide = True

        doc_county = ""

        if data['statewide'] == 'no':
            for cnty in data['counties']:
                doc_county += cnty.geow_shortname + ","

            doc_county = doc_county[:-1]
            if len(doc_county) > 64:
                doc_county = doc_county[:64]

        doc_city = ""

        if data['statewide'] == 'no':
            for cty in data['cities']:
                doc_city += cty.geow_shortname + ","

            doc_city = doc_city[:-1]
            if len(doc_city) > 64:
                doc_city = doc_city[:64]

        adddoc = documents(doc_prj_fk=prj,doc_cnty_fk=cnty_fk,doc_doct_fk=doct,doc_doctype=doct.keyw_shortname,doc_docname=doct.keyw_longname,doc_title=doc_title,doc_description=doc_description,doc_conname=data['doc_conname'],doc_conagency=lag.lag_name,doc_conemail=data['doc_conemail'],doc_conphone=data['doc_conphone'],doc_conaddress1=data['doc_conaddress1'],doc_conaddress2=doc_conaddress2,doc_concity=data['doc_concity'],doc_constate=data['doc_constate'],doc_conzip=data['doc_conzip'],doc_location=data['doc_location'],doc_city=doc_city,doc_county=doc_county,doc_draft=1,doc_pending=0,doc_received=doc_received,doc_added=today,doc_approve_noe=data['doc_approve_noe'],doc_carryout_noe=data['doc_carryout_noe'],doc_exministerial=doc_exministerial,doc_exdeclared=doc_exdeclared,doc_exemergency=doc_exemergency,doc_excategorical=doc_excategorical,doc_exstatutory=doc_exstatutory,doc_exnumber=doc_exnumber,doc_exreasons=data['doc_exreasons'],doc_added_userid=self.request.user,doc_assigned_userid=User.objects.get(pk=-1),doc_lastlooked_userid=User.objects.get(pk=-1))
        adddoc.save()

        if data['statewide'] == 'no':
            for cnty in data['counties']:
                geowrds_cnty = docgeowords(dgeo_geow_fk=cnty,dgeo_doc_fk=adddoc,dgeo_rank=1)
                geowrds_cnty.save()

            for cty in data['cities']:
                geowrds_city = docgeowords(dgeo_geow_fk=cty,dgeo_doc_fk=adddoc,dgeo_rank=1)
                geowrds_city.save()

        geometry = Locations(document=adddoc,geom=data['geom'])
        geometry.save()

        coords = latlongs(doc_pk=adddoc.pk,doc_prj_fk=prj,doc_doctype=doct.keyw_shortname,doc_latitude=data['doc_latitude'],doc_longitude=data['doc_longitude'])
        coords.save()

        prj.prj_doc_fk=adddoc
        prj.save()

        self.doc_pk = adddoc.pk

        if settings.SENDEMAIL:
            email_submission(self,adddoc)

        return super(docadd_noe,self).form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(docadd_noe, self).dispatch(*args, **kwargs)

class docadd_nop(FormView):
    template_name="ceqanet/docadd_nop.html"
    form_class = nopform

    def get_success_url(self):
        success_url = "%s?doc_pk=%s" % (reverse_lazy('attachments'),self.doc_pk)
        return success_url

    def get_initial(self):
        initial = super(docadd_nop, self).get_initial()

        if self.request.GET.get("prj_pk") != 'None':
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
        context = super(docadd_nop, self).get_context_data(**kwargs)

        prj_pk = self.request.GET.get("prj_pk")
        context['prj_pk'] = prj_pk
        context['doctype'] = self.request.GET.get("doctype")
        if prj_pk != 'None':
            context['prjinfo'] = projects.objects.get(prj_pk__exact=self.request.GET.get("prj_pk"))
        context['laglist'] = leadagencies.objects.get(pk=self.request.user.get_profile().set_lag_fk.lag_pk)

        return context
    
    def form_valid(self,form):
        data = form.cleaned_data
        today = datetime.now()
        doc_received = today
        lag = leadagencies.objects.get(pk=self.request.user.get_profile().set_lag_fk.lag_pk)
        doc = documents.objects.get(pk=0)
        cnty_fk = counties.objects.get(pk=0)
        doct = doctypes.objects.get(pk=self.request.POST.get('doctype'))

        doc_title = None
        doc_description = None
        doc_conaddress2 = None
        doc_parcelno = None
        doc_xstreets = None
        doc_township = None
        doc_range = None
        doc_section = None
        doc_base = None
        doc_highways = None
        doc_airports = None
        doc_railways = None
        doc_waterways = None
        doc_landuse = None
        doc_schools = None

        if data['doc_title']:
            doc_title = data['doc_title']
        if data['doc_description']:
            doc_description = data['doc_description']
        if data['doc_conaddress2']:
            doc_conaddress2 = data['doc_conaddress2']
        if data['doc_parcelno']:
            doc_parcelno = data['doc_parcelno']
        if data['doc_xstreets']:
            doc_xstreets = data['doc_xstreets']
        if data['doc_township']:
            doc_township = data['doc_township']
        if data['doc_range']:
            doc_range = data['doc_range']
        if data['doc_section']:
            doc_section = data['doc_section']
        if data['doc_base']:
            doc_base = data['doc_base']
        if data['doc_highways']:
            doc_highways = data['doc_highways']
        if data['doc_airports']:
            doc_airports = data['doc_airports']
        if data['doc_railways']:
            doc_railways = data['doc_railways']
        if data['doc_waterways']:
            doc_waterways = data['doc_waterways']
        if data['doc_landuse']:
            doc_landuse = data['doc_landuse']
        if data['doc_schools']:
            doc_schools = data['doc_schools']

        if self.request.POST.get('prj_pk') == 'None':
            prj = projects(prj_lag_fk=lag,prj_doc_fk=doc,prj_status=doct.keyw_shortname,prj_title=data['prj_title'],prj_description=data['prj_description'],prj_leadagency=lag.lag_name,prj_datefirst=today,prj_datelast=today)
            prj.save()
        else:
            prj = projects.objects.get(pk=self.request.POST.get('prj_pk'))
            prj.prj_status = doct.keyw_shortname
            prj.prj_datelast = today
            prj.save()

        doc_statewide = False

        if data['statewide'] == 'yes':
            doc_statewide = True

        doc_county = ""

        if data['statewide'] == 'no':
            for cnty in data['counties']:
                doc_county += cnty.geow_shortname + ","

            doc_county = doc_county[:-1]
            if len(doc_county) > 64:
                doc_county = doc_county[:64]

        doc_city = ""

        if data['statewide'] == 'no':
            for cty in data['cities']:
                doc_city += cty.geow_shortname + ","

            doc_city = doc_city[:-1]
            if len(doc_city) > 64:
                doc_city = doc_city[:64]

        adddoc = documents(doc_prj_fk=prj,doc_cnty_fk=cnty_fk,doc_doct_fk=doct,doc_doctype=doct.keyw_shortname,doc_docname=doct.keyw_longname,doc_title=data['doc_title'],doc_description=data['doc_description'],doc_conname=data['doc_conname'],doc_conagency=lag.lag_name,doc_conemail=data['doc_conemail'],doc_conphone=data['doc_conphone'],doc_conaddress1=data['doc_conaddress1'],doc_conaddress2=doc_conaddress2,doc_concity=data['doc_concity'],doc_constate=data['doc_constate'],doc_conzip=data['doc_conzip'],doc_location=data['doc_location'],doc_city=doc_city,doc_county=doc_county,doc_statewide=doc_statewide,doc_draft=1,doc_pending=0,doc_received=doc_received,doc_added=today,doc_parcelno=doc_parcelno,doc_xstreets=doc_xstreets,doc_township=doc_township,doc_range=doc_range,doc_section=doc_section,doc_base=doc_base,doc_highways=doc_highways,doc_airports=doc_airports,doc_railways=doc_railways,doc_waterways=doc_waterways,doc_landuse=doc_landuse,doc_schools=doc_schools,doc_added_userid=self.request.user,doc_assigned_userid=User.objects.get(pk=-1),doc_lastlooked_userid=User.objects.get(pk=-1))
        adddoc.save()

        if data['statewide'] == 'no':
            for cnty in data['counties']:
                geowrds_cnty = docgeowords(dgeo_geow_fk=cnty,dgeo_doc_fk=adddoc,dgeo_rank=1)
                geowrds_cnty.save()

            for cty in data['cities']:
                geowrds_city = docgeowords(dgeo_geow_fk=cty,dgeo_doc_fk=adddoc,dgeo_rank=1)
                geowrds_city.save()

        geometry = Locations(document=adddoc,geom=data['geom'])
        geometry.save()

        coords = latlongs(doc_pk=adddoc.pk,doc_prj_fk=prj,doc_doctype=doct.keyw_shortname,doc_latitude=data['doc_latitude'],doc_longitude=data['doc_longitude'])
        coords.save()

        for a in data['actions']:
            if a.keyw_pk == 1018:
                adockeyw = dockeywords(dkey_doc_fk=adddoc,dkey_keyw_fk=a,dkey_comment=data['dkey_comment_actions'],dkey_rank=0)
            else:
                adockeyw = dockeywords(dkey_doc_fk=adddoc,dkey_keyw_fk=a,dkey_rank=0)
            adockeyw.save()

        devtypes = keywords.objects.filter(keyw_keyl_fk__keyl_pk=1010).filter(keyw_pk__gte=6001).filter(keyw_pk__lte=11001)
        for d in devtypes:
            if self.request.POST.get('dev'+str(d.keyw_pk)):
                if d.keyw_pk == 11001:
                    ddockeyw = dockeywords(dkey_doc_fk=adddoc,dkey_keyw_fk=d,dkey_comment=self.request.POST.get('dkey_comment_dev'),dkey_value1=self.request.POST.get('dev'+str(d.keyw_pk)+'_val1'),dkey_value2=self.request.POST.get('dev'+str(d.keyw_pk)+'_val2'),dkey_value3=self.request.POST.get('dev'+str(d.keyw_pk)+'_val3'),dkey_rank=0)
                else:
                    ddockeyw = dockeywords(dkey_doc_fk=adddoc,dkey_keyw_fk=d,dkey_value1=self.request.POST.get('dev'+str(d.keyw_pk)+'_val1'),dkey_value2=self.request.POST.get('dev'+str(d.keyw_pk)+'_val2'),dkey_value3=self.request.POST.get('dev'+str(d.keyw_pk)+'_val3'),dkey_rank=0)
                ddockeyw.save()
        if data['devtrans']:
            ddockeyw = dockeywords(dkey_doc_fk=adddoc,dkey_keyw_fk=data['devtrans_id'],dkey_comment=data['devtrans_comment'],dkey_value1=None,dkey_value2=None,dkey_value3=None,dkey_rank=0)
            ddockeyw.save()
        if data['devpower']:
            ddockeyw = dockeywords(dkey_doc_fk=adddoc,dkey_keyw_fk=data['devpower_id'],dkey_comment=data['devpower_comment'],dkey_value1=data['devpower_val1'],dkey_value2=None,dkey_value3=None,dkey_rank=0)
            ddockeyw.save()
        if data['devwaste']:
            ddockeyw = dockeywords(dkey_doc_fk=adddoc,dkey_keyw_fk=data['devwaste_id'],dkey_comment=data['devwaste_comment'],dkey_value1=None,dkey_value2=None,dkey_value3=None,dkey_rank=0)
            ddockeyw.save()

        for i in data['issues']:
            if i.keyw_pk == 2034:
                idockeyw = dockeywords(dkey_doc_fk=adddoc,dkey_keyw_fk=i,dkey_comment=data['dkey_comment_issues'],dkey_rank=0)
            else:
                idockeyw = dockeywords(dkey_doc_fk=adddoc,dkey_keyw_fk=i,dkey_rank=0)
            idockeyw.save()

        for ra in data['ragencies']:
            docrev = docreviews(drag_doc_fk=adddoc,drag_rag_fk=ra,drag_rank=0,drag_copies=1,drag_numcomments=0)
            docrev.save()

        prj.prj_doc_fk=adddoc
        prj.save()

        self.doc_pk = adddoc.pk

        return super(docadd_nop,self).form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(docadd_nop, self).dispatch(*args, **kwargs)

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

    queryset = documents.objects.filter(doc_visible=True).filter(doc_prj_fk__exact=prj_pk).order_by('-doc_received','-doc_pk')
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
        context['comments'] = doccomments.objects.filter(dcom_doc_fk=doc_pk)
        context['attachments'] = docattachments.objects.filter(datt_doc_fk=doc_pk)
        context['counties'] = geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).filter(docgeowords__dgeo_doc_fk__doc_pk=doc_pk)
        context['cities'] = geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).filter(docgeowords__dgeo_doc_fk__doc_pk=doc_pk)
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
        context['attachments'] = docattachments.objects.filter(datt_doc_fk=doc_pk)
        context['counties'] = geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).filter(docgeowords__dgeo_doc_fk__doc_pk=doc_pk)
        context['cities'] = geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).filter(docgeowords__dgeo_doc_fk__doc_pk=doc_pk)
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
        context['attachments'] = docattachments.objects.filter(datt_doc_fk=doc_pk)
        context['counties'] = geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).filter(docgeowords__dgeo_doc_fk__doc_pk=doc_pk)
        context['cities'] = geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).filter(docgeowords__dgeo_doc_fk__doc_pk=doc_pk)
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
        context['comments'] = doccomments.objects.filter(dcom_doc_fk=doc_pk)
        context['attachments'] = docattachments.objects.filter(datt_doc_fk=doc_pk)
        context['counties'] = geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).filter(docgeowords__dgeo_doc_fk__doc_pk=doc_pk)
        context['cities'] = geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).filter(docgeowords__dgeo_doc_fk__doc_pk=doc_pk)
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
        latinfo = keywords.objects.filter(dockeywords__dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(keyw_keyl_fk__keyl_pk=1001)
        devinfo = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1010)
        issinfo= keywords.objects.filter(dockeywords__dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(keyw_keyl_fk__keyl_pk=1002)
        raginfo = reviewingagencies.objects.filter(docreviews__drag_doc_fk__doc_pk=self.request.GET.get('doc_pk'))
        dkey_comment_actions = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_pk=1018)
        dkey_comment_dev = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_pk=11001)
        dkey_comment_issues = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_pk=2034)
        
        initial['prj_title'] = docinfo.doc_prj_fk.prj_title
        initial['prj_description'] = docinfo.doc_prj_fk.prj_description
        initial['doc_title'] = docinfo.doc_title
        initial['doc_description'] = docinfo.doc_description
        initial['doc_conname'] = docinfo.doc_conname
        initial['doc_conemail'] = docinfo.doc_conemail
        initial['doc_conphone'] = docinfo.doc_conphone
        initial['doc_conaddress1'] = docinfo.doc_conaddress1
        initial['doc_conaddress2'] = docinfo.doc_conaddress2
        initial['doc_concity'] = docinfo.doc_concity
        initial['doc_constate'] = docinfo.doc_constate
        initial['doc_conzip'] = docinfo.doc_conzip.strip
        initial['doc_location'] = docinfo.doc_location

        geominfo = Locations.objects.filter(document=self.request.GET.get('doc_pk'))
        if geominfo.exists():
            initial['geom'] = geominfo[0].geom

        if latlonginfo.exists():
            initial['doc_latitude'] = latlonginfo[0].doc_latitude
            initial['doc_longitude'] = latlonginfo[0].doc_longitude

        if docinfo.doc_statewide:
            initial['statewide'] = "yes"
        else:
            initial['statewide'] = "no"
        initial['counties'] = geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).filter(docgeowords__dgeo_doc_fk__doc_pk=self.request.GET.get('doc_pk'))
        initial['cities'] = geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).filter(docgeowords__dgeo_doc_fk__doc_pk=self.request.GET.get('doc_pk'))

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
                    initial['devtrans'] = True
                    initial['devtrans_id'] = dev.dkey_keyw_fk.keyw_pk
                    initial['devtrans_comment'] = dev.dkey_comment
            if dev.dkey_keyw_fk.keyw_pk > 3000:
                if dev.dkey_keyw_fk.keyw_pk < 4000:
                    initial['devpower'] = True
                    initial['devpower_id'] = dev.dkey_keyw_fk.keyw_pk
                    initial['devpower_comment'] = dev.dkey_comment
                    initial['devpower_val1'] = dev.dkey_value1
            if dev.dkey_keyw_fk.keyw_pk > 5000:
                if dev.dkey_keyw_fk.keyw_pk < 6000:
                    initial['devwaste'] = True
                    initial['devwaste_id'] = dev.dkey_keyw_fk.keyw_pk
                    initial['devwaste_comment'] = dev.dkey_comment
            if dev.dkey_keyw_fk.keyw_pk == 6001:
                initial['dev6001'] = True
                initial['dev6001_val1'] = dev.dkey_value1
                initial['dev6001_val2'] = dev.dkey_value2
            elif dev.dkey_keyw_fk.keyw_pk == 6002:
                initial['dev6002'] = True
                initial['dev6002_val1'] = dev.dkey_value1
                initial['dev6002_val2'] = dev.dkey_value2
                initial['dev6002_val3'] = dev.dkey_value3
            elif dev.dkey_keyw_fk.keyw_pk == 6003:
                initial['dev6003'] = True
                initial['dev6003_val1'] = dev.dkey_value1
                initial['dev6003_val2'] = dev.dkey_value2
                initial['dev6003_val3'] = dev.dkey_value3
            elif dev.dkey_keyw_fk.keyw_pk == 6004:
                initial['dev6004'] = True
                initial['dev6004_val1'] = dev.dkey_value1
                initial['dev6004_val2'] = dev.dkey_value2
                initial['dev6004_val3'] = dev.dkey_value3
            elif dev.dkey_keyw_fk.keyw_pk == 7001:
                initial['dev7001'] = True
                initial['dev7001_val1'] = dev.dkey_value1
            elif dev.dkey_keyw_fk.keyw_pk == 8001:
                initial['dev8001'] = True
                initial['dev8001_val1'] = dev.dkey_value1
            elif dev.dkey_keyw_fk.keyw_pk == 9001:
                initial['dev9001'] = True
                initial['dev9001_val1'] = dev.dkey_value1
                initial['dev9001_val2'] = dev.dkey_value2
            elif dev.dkey_keyw_fk.keyw_pk == 10001:
                initial['dev10001'] = True
                initial['dev10001_val1'] = dev.dkey_value1
            elif dev.dkey_keyw_fk.keyw_pk == 11001:
                initial['dev11001'] = True

        if issinfo.exists():
            initial['issues'] = issinfo

        if raginfo.exists():
            initial['ragencies'] = raginfo

        initial['doc_dept'] = docinfo.doc_dept
        initial['doc_clear'] = docinfo.doc_clear

        initial['doc_clerknotes'] = docinfo.doc_clerknotes

        return initial

    def get_context_data(self, **kwargs):
        context = super(docedit_noc, self).get_context_data(**kwargs)
        context['doc'] = documents.objects.get(doc_pk=self.request.GET.get('doc_pk'))
        context['lats'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1001)
        context['devs'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1010)
        context['isss'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1002)
        context['attachments'] = docattachments.objects.filter(datt_doc_fk=self.request.GET.get('doc_pk'))
        holidayslist = holidays.objects.filter(hday_date__gte=datetime.now())
        hlist = "["
        for h in holidayslist:
            hlist += "\"" + h.hday_date.strftime('%Y-%m-%d') + "\"" + ","

        hlist = hlist[:-1]
        hlist += "];"
        context['holidays'] = hlist

        return context

    def form_valid(self,form):
        data = form.cleaned_data
        doc = documents.objects.get(pk=self.request.POST.get('doc_pk'))
        prj = projects.objects.get(pk=doc.doc_prj_fk.prj_pk)

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

        doc.doc_title = data['doc_title']
        doc.doc_description = data['doc_description']
        doc.doc_conname = data['doc_conname']
        doc.doc_conemail = data['doc_conemail']
        doc.doc_conphone = data['doc_conphone']
        doc.doc_conaddress1 = data['doc_conaddress1']
        doc.doc_conaddress2 = doc_conaddress2
        doc.doc_concity = data['doc_concity']
        doc.doc_constate = data['doc_constate']
        doc.doc_conzip = data['doc_conzip']
        doc.doc_location = data['doc_location']

        doc_statewide = False

        if data['statewide'] == 'yes':
            doc_statewide = True

        doc.doc_statewide = doc_statewide

        doc_county = ""

        if data['statewide'] == 'no':
            for cnty in data['counties']:
                doc_county += cnty.geow_shortname + ","

            doc_county = doc_county[:-1]
            if len(doc_county) > 64:
                doc_county = doc_county[:64]

        doc_city = ""

        if data['statewide'] == 'no':
            for cty in data['cities']:
                doc_city += cty.geow_shortname + ","

            doc_city = doc_city[:-1]
            if len(doc_city) > 64:
                doc_city = doc_city[:64]

        doc.doc_county = doc_county
        doc.doc_city = doc_city
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
        doc.doc_dept = data['doc_dept']
        doc.doc_clear = data['doc_clear']
        doc.doc_clerknotes = data['doc_clerknotes']
        doc.save()
        prj.prj_title = data['prj_title']
        prj.prj_description = data['prj_description']
        prj.save()

        try:
            geometry = Locations.objects.get(document=doc.pk)
            geometry.geom = data['geom']
        except Locations.DoesNotExist:
            geometry = Locations(document=doc,geom=data['geom'])
        geometry.save()

        try:
            coords = latlongs.objects.get(pk=doc.pk)
            coords.doc_latitude = data['doc_latitude']
            coords.doc_longitude = data['doc_longitude']
        except latlongs.DoesNotExist:
            coords = latlongs(doc_pk=doc.pk,doc_prj_fk=prj,doc_doctype="NOC",doc_latitude=data['doc_latitude'],doc_longitude=data['doc_longitude'])
        coords.save()

        docgeowords.objects.filter(dgeo_doc_fk__doc_pk=doc.pk).delete()

        if data['statewide'] == 'no':
            for cnty in data['counties']:
                geowrds_cnty = docgeowords(dgeo_geow_fk=cnty,dgeo_doc_fk=doc,dgeo_rank=1)
                geowrds_cnty.save()

            for cty in data['cities']:
                geowrds_city = docgeowords(dgeo_geow_fk=cty,dgeo_doc_fk=doc,dgeo_rank=1)
                geowrds_city.save()

        dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc.pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1001).delete()

        for a in data['actions']:
            if a.keyw_pk == 1018:
                adockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=a,dkey_comment=data['dkey_comment_actions'],dkey_rank=0)
            else:
                adockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=a,dkey_rank=0)
            adockeyw.save()

        dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc.pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1010).delete()

        devtypes = keywords.objects.filter(keyw_keyl_fk__keyl_pk=1010).filter(keyw_pk__gte=6001).filter(keyw_pk__lte=11001)
        for d in devtypes:
            if self.request.POST.get('dev'+str(d.keyw_pk)):
                if d.keyw_pk == 11001:
                    ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=d,dkey_comment=self.request.POST.get('dkey_comment_dev'),dkey_value1=self.request.POST.get('dev'+str(d.keyw_pk)+'_val1'),dkey_value2=self.request.POST.get('dev'+str(d.keyw_pk)+'_val2'),dkey_value3=self.request.POST.get('dev'+str(d.keyw_pk)+'_val3'),dkey_rank=0)
                else:
                    ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=d,dkey_value1=self.request.POST.get('dev'+str(d.keyw_pk)+'_val1'),dkey_value2=self.request.POST.get('dev'+str(d.keyw_pk)+'_val2'),dkey_value3=self.request.POST.get('dev'+str(d.keyw_pk)+'_val3'),dkey_rank=0)
                ddockeyw.save()
        if data['devtrans']:
            ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=data['devtrans_id'],dkey_comment=data['devtrans_comment'],dkey_value1=None,dkey_value2=None,dkey_value3=None,dkey_rank=0)
            ddockeyw.save()
        if data['devpower']:
            ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=data['devpower_id'],dkey_comment=data['devpower_comment'],dkey_value1=data['devpower_val1'],dkey_value2=None,dkey_value3=None,dkey_rank=0)
            ddockeyw.save()
        if data['devwaste']:
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

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(docedit_noc, self).dispatch(*args, **kwargs)

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
        initial['prj_applicant'] = docinfo.doc_prj_fk.prj_applicant
        initial['doc_title'] = docinfo.doc_title
        initial['doc_description'] = docinfo.doc_description
        initial['doc_conname'] = docinfo.doc_conname
        initial['doc_conemail'] = docinfo.doc_conemail
        initial['doc_conphone'] = docinfo.doc_conphone
        initial['doc_conaddress1'] = docinfo.doc_conaddress1
        initial['doc_conaddress2'] = docinfo.doc_conaddress2
        initial['doc_concity'] = docinfo.doc_concity
        initial['doc_constate'] = docinfo.doc_constate
        initial['doc_conzip'] = docinfo.doc_conzip.strip
        initial['doc_location'] = docinfo.doc_location

        geominfo = Locations.objects.filter(document=self.request.GET.get('doc_pk'))
        if geominfo.exists():
            initial['geom'] = geominfo[0].geom

        if latlonginfo.exists():
            initial['doc_latitude'] = latlonginfo[0].doc_latitude
            initial['doc_longitude'] = latlonginfo[0].doc_longitude

        if docinfo.doc_statewide:
            initial['statewide'] = "yes"
        else:
            initial['statewide'] = "no"
        initial['counties'] = geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).filter(docgeowords__dgeo_doc_fk__doc_pk=self.request.GET.get('doc_pk'))
        initial['cities'] = geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).filter(docgeowords__dgeo_doc_fk__doc_pk=self.request.GET.get('doc_pk'))

        if docinfo.doc_nodbylead:
            initial['leadorresp'] = 'lead'
        elif docinfo.doc_nodbyresp:
            initial['leadorresp'] = 'resp'
        initial['doc_nodagency'] = docinfo.doc_nodagency
        initial['doc_nod'] = docinfo.doc_nod
        if docinfo.doc_detsigeffect:
            initial['det1'] = 'True'
        elif docinfo.doc_detnotsigeffect:
            initial['det1'] = 'False'
        if docinfo.doc_deteir:
            initial['det2'] = 'True'
        elif docinfo.doc_detnegdec:
            initial['det2'] = 'False'
        if docinfo.doc_detmitigation:
            initial['det3'] = 'True'
        elif docinfo.doc_detnotmitigation:
            initial['det3'] = 'False'
        if docinfo.doc_detconsider:
            initial['det4'] = 'True'
        elif docinfo.doc_detnotconsider:
            initial['det4'] = 'False'
        if docinfo.doc_detfindings:
            initial['det5'] = 'True'
        elif docinfo.doc_detnotfindings:
            initial['det5'] = 'False'

        initial['doc_eiravailableat'] = docinfo.doc_eiravailableat

        return initial

    def get_context_data(self, **kwargs):
        context = super(docedit_nod, self).get_context_data(**kwargs)
        context['doc'] = documents.objects.get(doc_pk=self.request.GET.get('doc_pk'))
        context['attachments'] = docattachments.objects.filter(datt_doc_fk=self.request.GET.get('doc_pk'))

        return context

    def form_valid(self,form):
        data = form.cleaned_data
        doc = documents.objects.get(pk=self.request.POST.get('doc_pk'))
        prj = projects.objects.get(pk=doc.doc_prj_fk.prj_pk)

        doc.doc_title = data['doc_title']
        doc.doc_description = data['doc_description']
        doc.doc_conname = data['doc_conname']
        doc.doc_conemail = data['doc_conemail']
        doc.doc_conphone = data['doc_conphone']
        doc.doc_conaddress1 = data['doc_conaddress1']
        doc.doc_conaddress2 = data['doc_conaddress2']
        doc.doc_concity = data['doc_concity']
        doc.doc_constate = data['doc_constate']
        doc.doc_conzip = data['doc_conzip']
        doc.doc_location = data['doc_location']

        doc_statewide = False

        if data['statewide'] == 'yes':
            doc_statewide = True

        doc.doc_statewide = doc_statewide

        doc_county = ""

        if data['statewide'] == 'no':
            for cnty in data['counties']:
                doc_county += cnty.geow_shortname + ","

            doc_county = doc_county[:-1]
            if len(doc_county) > 64:
                doc_county = doc_county[:64]

        doc_city = ""

        if data['statewide'] == 'no':
            for cty in data['cities']:
                doc_city += cty.geow_shortname + ","

            doc_city = doc_city[:-1]
            if len(doc_city) > 64:
                doc_city = doc_city[:64]

        doc.doc_county = doc_county
        doc.doc_city = doc_city

        if data['leadorresp']:
            if data['leadorresp'] == 'lead':
                doc.doc_nodbylead = True
                doc.doc_nodbyresp = False
            elif data['leadorresp'] == 'resp':
                doc.doc_nodbylead = False
                doc.doc_nodbyresp = True

        if data['det1']:
            if data['det1'] == 'True':
                doc.doc_detsigeffect = True
                doc.doc_detnotsigeffect = False
            elif data['det1'] == 'False':
                doc.doc_detsigeffect = False
                doc.doc_detnotsigeffect = True
        if data['det2']:
            if data['det2'] == 'True':
                doc.doc_deteir = True
                doc.doc_detnegdec = False
            elif data['det2'] == 'False':
                doc.doc_deteir = False
                doc.doc_detnegdec = True
        if data['det3']:
            if data['det3'] == 'True':
                doc.doc_detmitigation = True
                doc.doc_detnotmitigation = False
            elif data['det3'] == 'False':
                doc.doc_detmitigation = False
                doc.doc_detnotmitigation = True
        if data['det4']:
            if data['det4'] == 'True':
                doc.doc_detconsider = True
                doc.doc_detnotconsider = False
            elif data['det4'] == 'False':
                doc.doc_detconsider = False
                doc.doc_detnotconsider = True
        if data['det5']:
            if data['det5'] == 'True':
                doc.doc_detfindings = True
                doc.doc_detnotfindings = False
            elif data['det5'] == 'False':
                doc.doc_detfindings = False
                doc.doc_detnotfindings = True

        doc.doc_eiravailableat = data['doc_eiravailableat']
        doc.save()
        prj.prj_title = data['prj_title']
        prj.prj_applicant = data['prj_applicant']
        prj.prj_description = data['prj_description']
        prj.save()

        try:
            geometry = Locations.objects.get(document=doc.pk)
            geometry.geom = data['geom']
        except Locations.DoesNotExist:
            geometry = Locations(document=doc,geom=data['geom'])
        geometry.save()

        try:
            coords = latlongs.objects.get(pk=doc.pk)
            coords.doc_latitude = data['doc_latitude']
            coords.doc_longitude = data['doc_longitude']
        except latlongs.DoesNotExist:
            coords = latlongs(doc_pk=doc.pk,doc_prj_fk=prj,doc_doctype="NOD",doc_latitude=data['doc_latitude'],doc_longitude=data['doc_longitude'])
        coords.save()

        docgeowords.objects.filter(dgeo_doc_fk__doc_pk=doc.pk).delete()

        if data['statewide'] == 'no':
            for cnty in data['counties']:
                geowrds_cnty = docgeowords(dgeo_geow_fk=cnty,dgeo_doc_fk=doc,dgeo_rank=1)
                geowrds_cnty.save()

            for cty in data['cities']:
                geowrds_city = docgeowords(dgeo_geow_fk=cty,dgeo_doc_fk=doc,dgeo_rank=1)
                geowrds_city.save()

        return super(docedit_nod,self).form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(docedit_nod, self).dispatch(*args, **kwargs)

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
        initial['doc_title'] = docinfo.doc_title
        initial['doc_description'] = docinfo.doc_description
        initial['doc_conname'] = docinfo.doc_conname
        initial['doc_conemail'] = docinfo.doc_conemail
        initial['doc_conphone'] = docinfo.doc_conphone
        initial['doc_conaddress1'] = docinfo.doc_conaddress1
        initial['doc_conaddress2'] = docinfo.doc_conaddress2
        initial['doc_concity'] = docinfo.doc_concity
        initial['doc_constate'] = docinfo.doc_constate
        initial['doc_conzip'] = docinfo.doc_conzip.strip
        initial['doc_location'] = docinfo.doc_location

        geominfo = Locations.objects.filter(document=self.request.GET.get('doc_pk'))
        if geominfo.exists():
            initial['geom'] = geominfo[0].geom

        if latlonginfo.exists():
            initial['doc_latitude'] = latlonginfo[0].doc_latitude
            initial['doc_longitude'] = latlonginfo[0].doc_longitude

        if docinfo.doc_statewide:
            initial['statewide'] = "yes"
        else:
            initial['statewide'] = "no"
        initial['counties'] = geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).filter(docgeowords__dgeo_doc_fk__doc_pk=self.request.GET.get('doc_pk'))
        initial['cities'] = geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).filter(docgeowords__dgeo_doc_fk__doc_pk=self.request.GET.get('doc_pk'))

        initial['doc_approve_noe'] = docinfo.doc_approve_noe
        initial['doc_carryout_noe'] = docinfo.doc_carryout_noe

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
        context['doc'] = documents.objects.get(doc_pk=self.request.GET.get('doc_pk'))
        context['attachments'] = docattachments.objects.filter(datt_doc_fk=self.request.GET.get('doc_pk'))

        return context

    def form_valid(self,form):
        data = form.cleaned_data
        doc = documents.objects.get(pk=self.request.POST.get('doc_pk'))
        prj = projects.objects.get(pk=doc.doc_prj_fk.prj_pk)
            
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

        doc.doc_title = data['doc_title']
        doc.doc_description = data['doc_description']
        doc.doc_conname = data['doc_conname']
        doc.doc_conemail = data['doc_conemail']
        doc.doc_conphone = data['doc_conphone']
        doc.doc_conaddress1 = data['doc_conaddress1']
        doc.doc_conaddress2 = data['doc_conaddress2']
        doc.doc_concity = data['doc_concity']
        doc.doc_constate = data['doc_constate']
        doc.doc_conzip = data['doc_conzip']
        doc.doc_location = data['doc_location']

        doc_statewide = False

        if data['statewide'] == 'yes':
            doc_statewide = True

        doc.doc_statewide = doc_statewide

        doc_county = ""

        if data['statewide'] == 'no':
            for cnty in data['counties']:
                doc_county += cnty.geow_shortname + ","

            doc_county = doc_county[:-1]
            if len(doc_county) > 64:
                doc_county = doc_county[:64]

        doc_city = ""

        if data['statewide'] == 'no':
            for cty in data['cities']:
                doc_city += cty.geow_shortname + ","

            doc_city = doc_city[:-1]
            if len(doc_city) > 64:
                doc_city = doc_city[:64]

        doc.doc_county = doc_county
        doc.doc_city = doc_city
        doc.doc_approve_noe = data['doc_approve_noe']
        doc.doc_carryout_noe = data['doc_carryout_noe']
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
            geometry = Locations.objects.get(document=doc.pk)
            geometry.geom = data['geom']
        except Locations.DoesNotExist:
            geometry = Locations(document=doc,geom=data['geom'])
        geometry.save()

        try:
            coords = latlongs.objects.get(pk=doc.pk)
            coords.doc_latitude = data['doc_latitude']
            coords.doc_longitude = data['doc_longitude']
        except latlongs.DoesNotExist:
            coords = latlongs(doc_pk=doc.pk,doc_prj_fk=prj,doc_doctype="NOE",doc_latitude=data['doc_latitude'],doc_longitude=data['doc_longitude'])
        coords.save()

        docgeowords.objects.filter(dgeo_doc_fk__doc_pk=doc.pk).delete()

        if data['statewide'] == 'no':
            for cnty in data['counties']:
                geowrds_cnty = docgeowords(dgeo_geow_fk=cnty,dgeo_doc_fk=doc,dgeo_rank=1)
                geowrds_cnty.save()

            for cty in data['cities']:
                geowrds_city = docgeowords(dgeo_geow_fk=cty,dgeo_doc_fk=doc,dgeo_rank=1)
                geowrds_city.save()

        return super(docedit_noe,self).form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(docedit_noe, self).dispatch(*args, **kwargs)

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
        latinfo = keywords.objects.filter(dockeywords__dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(keyw_keyl_fk__keyl_pk=1001)
        devinfo = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1010)
        issinfo= keywords.objects.filter(dockeywords__dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(keyw_keyl_fk__keyl_pk=1002)
        raginfo = reviewingagencies.objects.filter(docreviews__drag_doc_fk__doc_pk=self.request.GET.get('doc_pk'))
        dkey_comment_actions = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_pk=1018)
        dkey_comment_dev = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_pk=11001)
        dkey_comment_issues = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_pk=2034)
        
        initial['prj_title'] = docinfo.doc_prj_fk.prj_title
        initial['prj_description'] = docinfo.doc_prj_fk.prj_description
        initial['doc_title'] = docinfo.doc_title
        initial['doc_description'] = docinfo.doc_description
        initial['doc_conname'] = docinfo.doc_conname
        initial['doc_conemail'] = docinfo.doc_conemail
        initial['doc_conphone'] = docinfo.doc_conphone
        initial['doc_conaddress1'] = docinfo.doc_conaddress1
        initial['doc_conaddress2'] = docinfo.doc_conaddress2
        initial['doc_concity'] = docinfo.doc_concity
        initial['doc_constate'] = docinfo.doc_constate
        initial['doc_conzip'] = docinfo.doc_conzip.strip
        initial['doc_location'] = docinfo.doc_location

        geominfo = Locations.objects.filter(document=self.request.GET.get('doc_pk'))
        if geominfo.exists():
            initial['geom'] = geominfo[0].geom

        if latlonginfo.exists():
            initial['doc_latitude'] = latlonginfo[0].doc_latitude
            initial['doc_longitude'] = latlonginfo[0].doc_longitude

        if docinfo.doc_statewide:
            initial['statewide'] = "yes"
        else:
            initial['statewide'] = "no"
        initial['counties'] = geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).filter(docgeowords__dgeo_doc_fk__doc_pk=self.request.GET.get('doc_pk'))
        initial['cities'] = geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).filter(docgeowords__dgeo_doc_fk__doc_pk=self.request.GET.get('doc_pk'))

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

        if latinfo.exists():
            initial['actions'] = latinfo

        for dev in devinfo:
            if dev.dkey_keyw_fk.keyw_pk > 4000:
                if dev.dkey_keyw_fk.keyw_pk < 5000:
                    initial['devtrans'] = True
                    initial['devtrans_id'] = dev.dkey_keyw_fk.keyw_pk
                    initial['devtrans_comment'] = dev.dkey_comment
            if dev.dkey_keyw_fk.keyw_pk > 3000:
                if dev.dkey_keyw_fk.keyw_pk < 4000:
                    initial['devpower'] = True
                    initial['devpower_id'] = dev.dkey_keyw_fk.keyw_pk
                    initial['devpower_comment'] = dev.dkey_comment
                    initial['devpower_val1'] = dev.dkey_value1
            if dev.dkey_keyw_fk.keyw_pk > 5000:
                if dev.dkey_keyw_fk.keyw_pk < 6000:
                    initial['devwaste'] = True
                    initial['devwaste_id'] = dev.dkey_keyw_fk.keyw_pk
                    initial['devwaste_comment'] = dev.dkey_comment
            if dev.dkey_keyw_fk.keyw_pk == 6001:
                initial['dev6001'] = True
                initial['dev6001_val1'] = dev.dkey_value1
                initial['dev6001_val2'] = dev.dkey_value2
            elif dev.dkey_keyw_fk.keyw_pk == 6002:
                initial['dev6002'] = True
                initial['dev6002_val1'] = dev.dkey_value1
                initial['dev6002_val2'] = dev.dkey_value2
                initial['dev6002_val3'] = dev.dkey_value3
            elif dev.dkey_keyw_fk.keyw_pk == 6003:
                initial['dev6003'] = True
                initial['dev6003_val1'] = dev.dkey_value1
                initial['dev6003_val2'] = dev.dkey_value2
                initial['dev6003_val3'] = dev.dkey_value3
            elif dev.dkey_keyw_fk.keyw_pk == 6004:
                initial['dev6004'] = True
                initial['dev6004_val1'] = dev.dkey_value1
                initial['dev6004_val2'] = dev.dkey_value2
                initial['dev6004_val3'] = dev.dkey_value3
            elif dev.dkey_keyw_fk.keyw_pk == 7001:
                initial['dev7001'] = True
                initial['dev7001_val1'] = dev.dkey_value1
            elif dev.dkey_keyw_fk.keyw_pk == 8001:
                initial['dev8001'] = True
                initial['dev8001_val1'] = dev.dkey_value1
            elif dev.dkey_keyw_fk.keyw_pk == 9001:
                initial['dev9001'] = True
                initial['dev9001_val1'] = dev.dkey_value1
                initial['dev9001_val2'] = dev.dkey_value2
            elif dev.dkey_keyw_fk.keyw_pk == 10001:
                initial['dev10001'] = True
                initial['dev10001_val1'] = dev.dkey_value1
            elif dev.dkey_keyw_fk.keyw_pk == 11001:
                initial['dev11001'] = True

        if issinfo.exists():
            initial['issues'] = issinfo

        if raginfo.exists():
            initial['ragencies'] = raginfo

        initial['doc_dept'] = docinfo.doc_dept
        initial['doc_clear'] = docinfo.doc_clear

        initial['doc_clerknotes'] = docinfo.doc_clerknotes

        return initial

    def get_context_data(self, **kwargs):
        context = super(docedit_nop, self).get_context_data(**kwargs)
        context['doc'] = documents.objects.get(doc_pk=self.request.GET.get('doc_pk'))
        context['lats'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1001)
        context['devs'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1010)
        context['isss'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1002)
        context['attachments'] = docattachments.objects.filter(datt_doc_fk=self.request.GET.get('doc_pk'))
        holidayslist = holidays.objects.filter(hday_date__gte=datetime.now())
        hlist = "["
        for h in holidayslist:
            hlist += "\"" + h.hday_date.strftime('%Y-%m-%d') + "\"" + ","

        hlist = hlist[:-1]
        hlist += "];"
        context['holidays'] = hlist

        return context

    def form_valid(self,form):
        data = form.cleaned_data
        doc = documents.objects.get(pk=self.request.POST.get('doc_pk'))
        prj = projects.objects.get(pk=doc.doc_prj_fk.prj_pk)

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

        doc.doc_title = data['doc_title']
        doc.doc_description = data['doc_description']
        doc.doc_conname = data['doc_conname']
        doc.doc_conemail = data['doc_conemail']
        doc.doc_conphone = data['doc_conphone']
        doc.doc_conaddress1 = data['doc_conaddress1']
        doc.doc_conaddress2 = doc_conaddress2
        doc.doc_concity = data['doc_concity']
        doc.doc_constate = data['doc_constate']
        doc.doc_conzip = data['doc_conzip']
        doc.doc_location = data['doc_location']

        doc_statewide = False

        if data['statewide'] == 'yes':
            doc_statewide = True

        doc.doc_statewide = doc_statewide

        doc_county = ""

        if data['statewide'] == 'no':
            for cnty in data['counties']:
                doc_county += cnty.geow_shortname + ","

            doc_county = doc_county[:-1]
            if len(doc_county) > 64:
                doc_county = doc_county[:64]

        doc_city = ""

        if data['statewide'] == 'no':
            for cty in data['cities']:
                doc_city += cty.geow_shortname + ","

            doc_city = doc_city[:-1]
            if len(doc_city) > 64:
                doc_city = doc_city[:64]

        doc.doc_county = doc_county
        doc.doc_city = doc_city
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
        doc.doc_dept = data['doc_dept']
        doc.doc_clear = data['doc_clear']
        doc.doc_clerknotes = data['doc_clerknotes']
        doc.save()
        prj.prj_title = data['prj_title']
        prj.prj_description = data['prj_description']
        prj.save()

        try:
            geometry = Locations.objects.get(document=doc.pk)
            geometry.geom = data['geom']
        except Locations.DoesNotExist:
            geometry = Locations(document=doc,geom=data['geom'])
        geometry.save()

        try:
            coords = latlongs.objects.get(pk=doc.pk)
            coords.doc_latitude = data['doc_latitude']
            coords.doc_longitude = data['doc_longitude']
        except latlongs.DoesNotExist:
            coords = latlongs(doc_pk=doc.pk,doc_prj_fk=prj,doc_doctype="NOP",doc_latitude=data['doc_latitude'],doc_longitude=data['doc_longitude'])
        coords.save()

        docgeowords.objects.filter(dgeo_doc_fk__doc_pk=doc.pk).delete()

        if data['statewide'] == 'no':
            for cnty in data['counties']:
                geowrds_cnty = docgeowords(dgeo_geow_fk=cnty,dgeo_doc_fk=doc,dgeo_rank=1)
                geowrds_cnty.save()

            for cty in data['cities']:
                geowrds_city = docgeowords(dgeo_geow_fk=cty,dgeo_doc_fk=doc,dgeo_rank=1)
                geowrds_city.save()

        dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc.pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1001).delete()

        for a in data['actions']:
            if a.keyw_pk == 1018:
                adockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=a,dkey_comment=data['dkey_comment_actions'],dkey_rank=0)
            else:
                adockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=a,dkey_rank=0)
            adockeyw.save()

        dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc.pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1010).delete()

        devtypes = keywords.objects.filter(keyw_keyl_fk__keyl_pk=1010).filter(keyw_pk__gte=6001).filter(keyw_pk__lte=11001)
        for d in devtypes:
            if self.request.POST.get('dev'+str(d.keyw_pk)):
                if d.keyw_pk == 11001:
                    ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=d,dkey_comment=self.request.POST.get('dkey_comment_dev'),dkey_value1=self.request.POST.get('dev'+str(d.keyw_pk)+'_val1'),dkey_value2=self.request.POST.get('dev'+str(d.keyw_pk)+'_val2'),dkey_value3=self.request.POST.get('dev'+str(d.keyw_pk)+'_val3'),dkey_rank=0)
                else:
                    ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=d,dkey_value1=self.request.POST.get('dev'+str(d.keyw_pk)+'_val1'),dkey_value2=self.request.POST.get('dev'+str(d.keyw_pk)+'_val2'),dkey_value3=self.request.POST.get('dev'+str(d.keyw_pk)+'_val3'),dkey_rank=0)
                ddockeyw.save()
        if data['devtrans']:
            ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=data['devtrans_id'],dkey_comment=data['devtrans_comment'],dkey_value1=None,dkey_value2=None,dkey_value3=None,dkey_rank=0)
            ddockeyw.save()
        if data['devpower']:
            ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=data['devpower_id'],dkey_comment=data['devpower_comment'],dkey_value1=data['devpower_val1'],dkey_value2=None,dkey_value3=None,dkey_rank=0)
            ddockeyw.save()
        if data['devwaste']:
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

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(docedit_nop, self).dispatch(*args, **kwargs)

class draftedit_noc(docedit_noc):    
    template_name="ceqanet/draftedit_noc.html"

    def get_success_url(self):
        success_url = reverse_lazy('draftsbylag')
        return success_url

class draftedit_nod(docedit_nod):    
    template_name="ceqanet/draftedit_nod.html"

    def get_success_url(self):
        success_url = reverse_lazy('draftsbylag')
        return success_url

class draftedit_noe(docedit_noe):    
    template_name="ceqanet/draftedit_noe.html"

    def get_success_url(self):
        success_url = reverse_lazy('draftsbylag')
        return success_url

class draftedit_nop(docedit_nop):    
    template_name="ceqanet/draftedit_nop.html"

    def get_success_url(self):
        success_url = reverse_lazy('draftsbylag')
        return success_url

class addleadagency(FormView):
    form_class = addleadagencyform
    template_name="ceqanet/addleadagency.html"

    def get_success_url(self):
        success_url = reverse_lazy('index')
        return success_url

    def form_valid(self,form):
        data = form.cleaned_data

        gw = geowords.objects.get(pk=0)

        newleadagency = leadagencies(lag_geow_fk=gw,lag_name=data['lag_name'],lag_title=data['lag_title'],lag_address1=data['lag_address1'],lag_address2=data['lag_address2'],lag_county=data['lag_county'].geow_shortname,lag_city=data['lag_city'].geow_shortname,lag_state=data['lag_state'],lag_zip=data['lag_zip'],lag_phone=data['lag_phone'],lag_fax=data['lag_fax'])
        newleadagency.save()

        return super(addleadagency,self).form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(addleadagency, self).dispatch(*args, **kwargs)

class addreviewingagency(FormView):
    form_class = addreviewingagencyform
    template_name="ceqanet/addreviewingagency.html"

    def get_success_url(self):
        success_url = reverse_lazy('index')
        return success_url

    def form_valid(self,form):
        data = form.cleaned_data

        newreviewingagency = reviewingagencies(rag_name=data['rag_name'],rag_title=data['rag_title'],rag_address1=data['rag_address1'],rag_address2=data['rag_address2'],rag_county=data['rag_county'].geow_shortname,rag_city=data['rag_city'].geow_shortname,rag_state=data['rag_state'],rag_zip=data['rag_zip'],rag_phone=data['rag_phone'])
        newreviewingagency.save()

        return super(addreviewingagency,self).form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(addreviewingagency, self).dispatch(*args, **kwargs)

class addholiday(FormView):
    form_class = addholidayform
    template_name="ceqanet/addholiday.html"

    def get_success_url(self):
        success_url = reverse_lazy('index')
        return success_url

    def get_context_data(self, **kwargs):
        context = super(addholiday, self).get_context_data(**kwargs)
        holidayslist = holidays.objects.filter(hday_date__gte=datetime.now())
        hlist = "["
        for h in holidayslist:
            hlist += "\"" + h.hday_date.strftime('%Y-%m-%d') + "\"" + ","

        hlist = hlist[:-1]
        hlist += "];"
        context['holidays'] = hlist

        return context

    def form_valid(self,form):
        data = form.cleaned_data

        gw = geowords.objects.get(pk=0)

        newholiday = holidays(hday_name=data['hday_name'],hday_date=data['hday_date'],hday_dow=data['hday_date'].strftime('%A'),hday_note=data['hday_note'])
        newholiday.save()

        return super(addholiday,self).form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(addholiday, self).dispatch(*args, **kwargs)

class manageusers(FormView):
    template_name="ceqanet/manageusers.html"
    form_class = manageusersform

    def get_initial(self):
        initial = super(manageusers, self).get_initial()

        if self.request.GET.get('userfilter') != None:
            initial['userfilter'] = self.request.GET.get('userfilter')
        
        return initial

    def get_context_data(self, **kwargs):
        context = super(manageusers, self).get_context_data(**kwargs)

        if self.request.GET.get('userfilter') != None:
            usrflt = self.request.GET.get('userfilter')
        else:
            usrflt = ''

        context['users'] = User.objects.filter(is_superuser=False).filter(pk__gt=0).filter(username__icontains=usrflt).order_by('pk')

        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(manageusers, self).dispatch(*args, **kwargs)

class manageuser(FormView):
    form_class = manageuserform
    template_name="ceqanet/manageuser.html"

    def get_success_url(self):
        success_url = "%s?user_id=%s" % (reverse_lazy('manageuser'),self.request.POST.get('user_id'))
        return success_url

    def get_initial(self):
        initial = super(manageuser, self).get_initial()

        usr = User.objects.get(pk=self.request.GET.get('user_id'))
        grp = usr.groups.all()
        if grp.exists():
            initial['usr_grp'] = grp[0]
        
        if usr.get_profile().set_lag_fk != None:
            initial['set_lag_fk'] = leadagencies.objects.get(pk=usr.get_profile().set_lag_fk.lag_pk)
        
        if usr.get_profile().set_rag_fk != None:
            initial['set_rag_fk'] = reviewingagencies.objects.get(pk=usr.get_profile().set_rag_fk.rag_pk)

        return initial

    def get_context_data(self, **kwargs):
        context = super(manageuser, self).get_context_data(**kwargs)

        context['usr'] = User.objects.get(pk=self.request.GET.get('user_id'))

        return context

    def form_valid(self,form):
        data = form.cleaned_data

        usr = User.objects.get(pk=self.request.POST.get('user_id'))

        if self.request.POST.get('mode') == "assign":
            usr.groups.clear()
            if data['usr_grp'] != None:
                usr.groups.add(data['usr_grp'])
            usrprof = UserProfile.objects.get(user_id=self.request.POST.get('user_id'))
            if data['usr_grp'] == None:
                usrprof.set_lag_fk = None
                usrprof.set_rag_fk = None
            elif data['usr_grp'].name == 'leads':
                usrprof.set_lag_fk = data['set_lag_fk']
                usrprof.set_rag_fk = None
            elif data['usr_grp'].name == 'reviewers':
                usrprof.set_lag_fk = None
                usrprof.set_rag_fk = data['set_rag_fk']
            elif data['usr_grp'].name == 'planners':
                usrprof.set_lag_fk = data['set_lag_fk']
                usrprof.set_rag_fk = data['set_rag_fk']
            usrprof.save()

        elif self.request.POST.get('mode') == "deactivate":
            usr.is_active = False
            usr.save()
        elif self.request.POST.get('mode') == "activate":
            usr.is_active = True
            usr.save()

        return super(manageuser,self).form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(manageuser, self).dispatch(*args, **kwargs)

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

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(pending, self).dispatch(*args, **kwargs)

def PendingListQuery(request):
    queryset = documents.objects.filter(doc_pending=True).order_by('-doc_received','-doc_pk')
    return queryset

class latest(ListView):
    template_name="ceqanet/latest.html"
    context_object_name = "latests"
    paginate_by = 25

    def get_queryset(self):
        queryset = LatestListQuery(self.request)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(latest, self).get_context_data(**kwargs)

        qsminuspage = self.request.GET.copy()
        
        if "page" in qsminuspage:
            qsminuspage.pop('page')

        context['restofqs'] = qsminuspage.urlencode()

        return context

def LatestListQuery(request):
    queryset = documents.objects.exclude(doc_received__isnull=True).filter(doc_visible=True).order_by('-doc_received','-doc_pk')
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
        latinfo = keywords.objects.filter(dockeywords__dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(keyw_keyl_fk__keyl_pk=1001)
        devinfo = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1010)
        issinfo= keywords.objects.filter(dockeywords__dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(keyw_keyl_fk__keyl_pk=1002)
        raginfo = reviewingagencies.objects.filter(docreviews__drag_doc_fk__doc_pk=self.request.GET.get('doc_pk'))
        dkey_comment_actions = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_pk=1018)
        dkey_comment_dev = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_pk=11001)
        dkey_comment_issues = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_pk=2034)

        initial['prj_title'] = docinfo.doc_prj_fk.prj_title
        initial['prj_description'] = docinfo.doc_prj_fk.prj_description
        initial['doc_title'] = docinfo.doc_title
        initial['doc_description'] = docinfo.doc_description
        initial['doc_conname'] = docinfo.doc_conname
        initial['doc_conemail'] = docinfo.doc_conemail
        initial['doc_conphone'] = docinfo.doc_conphone
        initial['doc_conaddress1'] = docinfo.doc_conaddress1
        initial['doc_conaddress2'] = docinfo.doc_conaddress2
        initial['doc_concity'] = docinfo.doc_concity
        initial['doc_constate'] = docinfo.doc_constate
        initial['doc_conzip'] = docinfo.doc_conzip.strip
        initial['doc_location'] = docinfo.doc_location

        geominfo = Locations.objects.filter(document=self.request.GET.get('doc_pk'))
        if geominfo.exists():
            initial['geom'] = geominfo[0].geom

        if latlonginfo.exists():
            initial['doc_latitude'] = latlonginfo[0].doc_latitude
            initial['doc_longitude'] = latlonginfo[0].doc_longitude

        if docinfo.doc_statewide:
            initial['statewide'] = "yes"
        else:
            initial['statewide'] = "no"
        initial['counties'] = geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).filter(docgeowords__dgeo_doc_fk__doc_pk=self.request.GET.get('doc_pk'))
        initial['cities'] = geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).filter(docgeowords__dgeo_doc_fk__doc_pk=self.request.GET.get('doc_pk'))

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
                    initial['devtrans'] = True
                    initial['devtrans_id'] = dev.dkey_keyw_fk.keyw_pk
                    initial['devtrans_comment'] = dev.dkey_comment
            if dev.dkey_keyw_fk.keyw_pk > 3000:
                if dev.dkey_keyw_fk.keyw_pk < 4000:
                    initial['devpower'] = True
                    initial['devpower_id'] = dev.dkey_keyw_fk.keyw_pk
                    initial['devpower_comment'] = dev.dkey_comment
                    initial['devpower_val1'] = dev.dkey_value1
            if dev.dkey_keyw_fk.keyw_pk > 5000:
                if dev.dkey_keyw_fk.keyw_pk < 6000:
                    initial['devwaste'] = True
                    initial['devwaste_id'] = dev.dkey_keyw_fk.keyw_pk
                    initial['devwaste_comment'] = dev.dkey_comment
            if dev.dkey_keyw_fk.keyw_pk == 6001:
                initial['dev6001'] = True
                initial['dev6001_val1'] = dev.dkey_value1
                initial['dev6001_val2'] = dev.dkey_value2
            elif dev.dkey_keyw_fk.keyw_pk == 6002:
                initial['dev6002'] = True
                initial['dev6002_val1'] = dev.dkey_value1
                initial['dev6002_val2'] = dev.dkey_value2
                initial['dev6002_val3'] = dev.dkey_value3
            elif dev.dkey_keyw_fk.keyw_pk == 6003:
                initial['dev6003'] = True
                initial['dev6003_val1'] = dev.dkey_value1
                initial['dev6003_val2'] = dev.dkey_value2
                initial['dev6003_val3'] = dev.dkey_value3
            elif dev.dkey_keyw_fk.keyw_pk == 6004:
                initial['dev6004'] = True
                initial['dev6004_val1'] = dev.dkey_value1
                initial['dev6004_val2'] = dev.dkey_value2
                initial['dev6004_val3'] = dev.dkey_value3
            elif dev.dkey_keyw_fk.keyw_pk == 7001:
                initial['dev7001'] = True
                initial['dev7001_val1'] = dev.dkey_value1
            elif dev.dkey_keyw_fk.keyw_pk == 8001:
                initial['dev8001'] = True
                initial['dev8001_val1'] = dev.dkey_value1
            elif dev.dkey_keyw_fk.keyw_pk == 9001:
                initial['dev9001'] = True
                initial['dev9001_val1'] = dev.dkey_value1
                initial['dev9001_val2'] = dev.dkey_value2
            elif dev.dkey_keyw_fk.keyw_pk == 10001:
                initial['dev10001'] = True
                initial['dev10001_val1'] = dev.dkey_value1
            elif dev.dkey_keyw_fk.keyw_pk == 11001:
                initial['dev11001'] = True
                
        if issinfo.exists():
            initial['issues'] = issinfo

        if raginfo.exists():
            initial['ragencies'] = raginfo

        return initial

    def get_context_data(self, **kwargs):
        context = super(pendingdetail_noc, self).get_context_data(**kwargs)
        context['docinfo'] = documents.objects.get(pk=self.request.GET.get('doc_pk'))
        context['lats'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1001)
        context['devs'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1010)
        context['isss'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1002)
        context['attachments'] = docattachments.objects.filter(datt_doc_fk=self.request.GET.get('doc_pk'))
        holidayslist = holidays.objects.filter(hday_date__gte=datetime.now())
        hlist = "["
        for h in holidayslist:
            hlist += "\"" + h.hday_date.strftime('%Y-%m-%d') + "\"" + ","

        hlist = hlist[:-1]
        hlist += "];"
        context['holidays'] = hlist

        return context

    def form_valid(self,form):
        data = form.cleaned_data
        doc = documents.objects.get(pk=self.request.POST.get('doc_pk'))
        prj = projects.objects.get(pk=doc.doc_prj_fk.prj_pk)

        if self.request.POST.get('mode') == 'assign':
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

            doc.doc_title = data['doc_title']
            doc.doc_description = data['doc_description']
            doc.doc_conname = data['doc_conname']
            doc.doc_conemail = data['doc_conemail']
            doc.doc_conphone = data['doc_conphone']
            doc.doc_conaddress1 = data['doc_conaddress1']
            doc.doc_conaddress2 = doc_conaddress2
            doc.doc_concity = data['doc_concity']
            doc.doc_constate = data['doc_constate']
            doc.doc_conzip = data['doc_conzip']
            doc.doc_location = data['doc_location']
            doc_county = ""

            for cnty in data['counties']:
                doc_county += cnty.geow_shortname + ","

            doc_county = doc_county[:-1]
            if len(doc_county) > 64:
                doc_county = doc_county[:64]

            doc_city = ""

            for cty in data['cities']:
                doc_city += cty.geow_shortname + ","

            doc_city = doc_city[:-1]
            if len(doc_city) > 64:
                doc_city = doc_city[:64]
            doc.doc_county = doc_county
            doc.doc_city = doc_city
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
            doc.doc_plannerregion = data['doc_plannerregion']
            doc.doc_dept = data['doc_dept']
            doc.doc_clear = data['doc_clear']
            doc.doc_clerknotes = data['doc_clerknotes']
            doc.doc_bia = data['doc_bia']
            doc.save()

            prj.prj_title = data['prj_title']
            prj.prj_description = data['prj_description']
            if prj.prj_pending:
                prj.prj_pending = False
                prj.prj_plannerreview = True
            prj.save()

            try:
                geometry = Locations.objects.get(document=doc.pk)
                geometry.geom = data['geom']
            except Locations.DoesNotExist:
                geometry = Locations(document=doc,geom=data['geom'])
            geometry.save()

            try:
                coords = latlongs.objects.get(pk=doc.pk)
                coords.doc_latitude = data['doc_latitude']
                coords.doc_longitude = data['doc_longitude']
            except latlongs.DoesNotExist:
                coords = latlongs(doc_pk=doc.pk,doc_prj_fk=prj,doc_doctype="NOC",doc_latitude=data['doc_latitude'],doc_longitude=data['doc_longitude'])
            coords.save()

            docgeowords.objects.filter(dgeo_doc_fk__doc_pk=doc.pk).delete()

            if data['statewide'] == 'no':
                for cnty in data['counties']:
                    geowrds_cnty = docgeowords(dgeo_geow_fk=cnty,dgeo_doc_fk=doc,dgeo_rank=1)
                    geowrds_cnty.save()

                for cty in data['cities']:
                    geowrds_city = docgeowords(dgeo_geow_fk=cty,dgeo_doc_fk=doc,dgeo_rank=1)
                    geowrds_city.save()

            dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc.pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1001).delete()

            for a in data['actions']:
                if a.keyw_pk == 1018:
                    adockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=a,dkey_comment=data['dkey_comment_actions'],dkey_rank=0)
                else:
                    adockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=a,dkey_rank=0)
                adockeyw.save()
            
            dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc.pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1010).delete()

            devtypes = keywords.objects.filter(keyw_keyl_fk__keyl_pk=1010).filter(keyw_pk__gte=6001).filter(keyw_pk__lte=11001)
            for d in devtypes:
                if self.request.POST.get('dev'+str(d.keyw_pk)):
                    if d.keyw_pk == 11001:
                        ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=d,dkey_comment=self.request.POST.get('dkey_comment_dev'),dkey_value1=self.request.POST.get('dev'+str(d.keyw_pk)+'_val1'),dkey_value2=self.request.POST.get('dev'+str(d.keyw_pk)+'_val2'),dkey_value3=self.request.POST.get('dev'+str(d.keyw_pk)+'_val3'),dkey_rank=0)
                    else:
                        ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=d,dkey_value1=self.request.POST.get('dev'+str(d.keyw_pk)+'_val1'),dkey_value2=self.request.POST.get('dev'+str(d.keyw_pk)+'_val2'),dkey_value3=self.request.POST.get('dev'+str(d.keyw_pk)+'_val3'),dkey_rank=0)
                    ddockeyw.save()
            if data['devtrans']:
                ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=data['devtrans_id'],dkey_comment=data['devtrans_comment'],dkey_value1=None,dkey_value2=None,dkey_value3=None,dkey_rank=0)
                ddockeyw.save()
            if data['devpower']:
                ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=data['devpower_id'],dkey_comment=data['devpower_comment'],dkey_value1=data['devpower_val1'],dkey_value2=None,dkey_value3=None,dkey_rank=0)
                ddockeyw.save()
            if data['devwaste']:
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

            if settings.SENDEMAIL:
                email_assigned(self,doc)

        if self.request.POST.get('mode') == 'reject':
            if settings.SENDEMAIL:
                email_demotiontodraft(self,doc)
            doc.doc_draft = True
            doc.doc_pending = False
            doc.save()

        return super(pendingdetail_noc,self).form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(pendingdetail_noc, self).dispatch(*args, **kwargs)

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
        initial['prj_applicant'] = docinfo.doc_prj_fk.prj_applicant
        initial['prj_description'] = docinfo.doc_prj_fk.prj_description
        initial['doc_title'] = docinfo.doc_title
        initial['doc_description'] = docinfo.doc_description
        initial['doc_conname'] = docinfo.doc_conname
        initial['doc_conemail'] = docinfo.doc_conemail
        initial['doc_conphone'] = docinfo.doc_conphone
        initial['doc_conaddress1'] = docinfo.doc_conaddress1
        initial['doc_conaddress2'] = docinfo.doc_conaddress2
        initial['doc_concity'] = docinfo.doc_concity
        initial['doc_constate'] = docinfo.doc_constate
        initial['doc_conzip'] = docinfo.doc_conzip.strip
        initial['doc_location'] = docinfo.doc_location

        geominfo = Locations.objects.filter(document=self.request.GET.get('doc_pk'))
        if geominfo.exists():
            initial['geom'] = geominfo[0].geom

        if latlonginfo.exists():
            initial['doc_latitude'] = latlonginfo[0].doc_latitude
            initial['doc_longitude'] = latlonginfo[0].doc_longitude

        if docinfo.doc_statewide:
            initial['statewide'] = "yes"
        else:
            initial['statewide'] = "no"
        initial['counties'] = geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).filter(docgeowords__dgeo_doc_fk__doc_pk=self.request.GET.get('doc_pk'))
        initial['cities'] = geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).filter(docgeowords__dgeo_doc_fk__doc_pk=self.request.GET.get('doc_pk'))

        if docinfo.doc_nodbylead:            
            initial['leadorresp'] = 'lead'
        elif docinfo.doc_nodbyresp:
            initial['leadorresp'] = 'resp'

        nodlaginfo = leadagencies.objects.filter(lag_name__startswith=docinfo.doc_nodagency)

        if nodlaginfo.count() == 1:
            initial['doc_nodagency'] = nodlaginfo[0].lag_pk
        
        initial['doc_nod'] = docinfo.doc_nod
        if docinfo.doc_detsigeffect:
            initial['det1'] = 'True'
        elif docinfo.doc_detnotsigeffect:
            initial['det1'] = 'False'
        if docinfo.doc_deteir:
            initial['det2'] = 'True'
        elif docinfo.doc_detnegdec:
            initial['det2'] = 'False'
        if docinfo.doc_detmitigation:
            initial['det3'] = 'True'
        elif docinfo.doc_detnotmitigation:
            initial['det3'] = 'False'
        if docinfo.doc_detconsider:
            initial['det4'] = 'True'
        elif docinfo.doc_detnotconsider:
            initial['det4'] = 'False'
        if docinfo.doc_detfindings:
            initial['det5'] = 'True'
        elif docinfo.doc_detnotfindings:
            initial['det5'] = 'False'
        initial['doc_eiravailableat'] = docinfo.doc_eiravailableat
        if docinfo.doc_nodfeespaid:
            initial['doc_nodfeespaid'] = 'yes'
        else:
            initial['doc_nodfeespaid'] = 'no'


        return initial

    def get_context_data(self, **kwargs):
        context = super(pendingdetail_nod, self).get_context_data(**kwargs)

        context['docinfo'] = documents.objects.get(pk=self.request.GET.get('doc_pk'))
        context['attachments'] = docattachments.objects.filter(datt_doc_fk=self.request.GET.get('doc_pk'))

        return context

    def form_valid(self,form):
        data = form.cleaned_data
        doc = documents.objects.get(pk=self.request.POST.get('doc_pk'))
        prj = projects.objects.get(pk=doc.doc_prj_fk.prj_pk)

        if self.request.POST.get("mode") == 'accept':            
            doc.doc_title = data['doc_title']
            doc.doc_description = data['doc_description']
            doc.doc_conname = data['doc_conname']
            doc.doc_conemail = data['doc_conemail']
            doc.doc_conphone = data['doc_conphone']
            doc.doc_conaddress1 = data['doc_conaddress1']
            doc.doc_conaddress2 = data['doc_conaddress2']
            doc.doc_concity = data['doc_concity']
            doc.doc_constate = data['doc_constate']
            doc.doc_conzip = data['doc_conzip']
            doc.doc_location = data['doc_location']
            doc_county = ""

            for cnty in data['counties']:
                doc_county += cnty.geow_shortname + ","

            doc_county = doc_county[:-1]
            if len(doc_county) > 64:
                doc_county = doc_county[:64]

            doc_city = ""

            for cty in data['cities']:
                doc_city += cty.geow_shortname + ","

            doc_city = doc_city[:-1]
            if len(doc_city) > 64:
                doc_city = doc_city[:64]
            doc.doc_county = doc_county
            doc.doc_city = doc_city
            doc.doc_nodagency = data['doc_nodagency'].lag_name
            doc.doc_nod = data['doc_nod']
            if data['leadorresp']:
                if data['leadorresp'] == 'lead':
                    doc.doc_nodbylead = True
                    doc.doc_nodbyresp = False
                elif data['leadorresp'] == 'resp':
                    doc.doc_nodbylead = False
                    doc.doc_nodbyresp = True

            if data['det1']:
                if data['det1'] == 'True':
                    doc.doc_detsigeffect = True
                    doc.doc_detnotsigeffect = False
                elif data['det1'] == 'False':
                    doc.doc_detsigeffect = False
                    doc.doc_detnotsigeffect = True
            if data['det2']:
                if data['det2'] == 'True':
                    doc.doc_deteir = True
                    doc.doc_detnegdec = False
                elif data['det2'] == 'False':
                    doc.doc_deteir = False
                    doc.doc_detnegdec = True
            if data['det3']:
                if data['det3'] == 'True':
                    doc.doc_detmitigation = True
                    doc.doc_detnotmitigation = False
                elif data['det3'] == 'False':
                    doc.doc_detmitigation = False
                    doc.doc_detnotmitigation = True
            if data['det4']:
                if data['det4'] == 'True':
                    doc.doc_detconsider = True
                    doc.doc_detnotconsider = False
                elif data['det4'] == 'False':
                    doc.doc_detconsider = False
                    doc.doc_detnotconsider = True
            if data['det5']:
                if data['det5'] == 'True':
                    doc.doc_detfindings = True
                    doc.doc_detnotfindings = False
                elif data['det5'] == 'False':
                    doc.doc_detfindings = False
                    doc.doc_detnotfindings = True
            doc.doc_eiravailableat = data['doc_eiravailableat']
            doc.doc_nodfeespaid = data['doc_nodfeespaid']

            if prj.prj_schno:
                doc.doc_schno = prj.prj_schno
            else:
                doc.doc_schno = generate_schno(9)
            
            doc.doc_visible = True
            doc.doc_pending = False
            doc.doc_plannerreview = False
            doc.doc_plannerregion = 0
            doc.doc_clerknotes = data['doc_clerknotes']
            doc.save()
            prj.prj_title = data['prj_title']
            prj.prj_applicant = data['prj_applicant']
            prj.prj_description = data['prj_description']

            if not prj.prj_schno:
                prj.prj_schno = doc.doc_schno
            prj.prj_pending = False
            prj.prj_plannerreview = False
            prj.save()

            try:
                geometry = Locations.objects.get(document=doc.pk)
                geometry.geom = data['geom']
            except Locations.DoesNotExist:
                geometry = Locations(document=doc,geom=data['geom'])
            geometry.save()

            try:
                coords = latlongs.objects.get(pk=doc.pk)
                coords.doc_latitude = data['doc_latitude']
                coords.doc_longitude = data['doc_longitude']
            except latlongs.DoesNotExist:
                coords = latlongs(doc_pk=doc.pk,doc_prj_fk=prj,doc_doctype="NOD",doc_latitude=data['doc_latitude'],doc_longitude=data['doc_longitude'])
            coords.save()

            docgeowords.objects.filter(dgeo_doc_fk__doc_pk=doc.pk).delete()

            if data['statewide'] == 'no':
                for cnty in data['counties']:
                    geowrds_cnty = docgeowords(dgeo_geow_fk=cnty,dgeo_doc_fk=doc,dgeo_rank=1)
                    geowrds_cnty.save()

                for cty in data['cities']:
                    geowrds_city = docgeowords(dgeo_geow_fk=cty,dgeo_doc_fk=doc,dgeo_rank=1)
                    geowrds_city.save()

            if settings.SENDEMAIL:
                email_acceptance(self)

        elif self.request.POST.get('mode') == 'reject':
            if settings.SENDEMAIL:
                email_demotiontodraft(self,doc)
            doc.doc_draft = True
            doc.doc_pending = False
            doc.save()
            
        return super(pendingdetail_nod,self).form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(pendingdetail_nod, self).dispatch(*args, **kwargs)

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
        initial['doc_title'] = docinfo.doc_title
        initial['doc_description'] = docinfo.doc_description
        initial['doc_conname'] = docinfo.doc_conname
        initial['doc_conemail'] = docinfo.doc_conemail
        initial['doc_conphone'] = docinfo.doc_conphone
        initial['doc_conaddress1'] = docinfo.doc_conaddress1
        initial['doc_conaddress2'] = docinfo.doc_conaddress2
        initial['doc_concity'] = docinfo.doc_concity
        initial['doc_constate'] = docinfo.doc_constate
        initial['doc_conzip'] = docinfo.doc_conzip.strip
        initial['doc_location'] = docinfo.doc_location

        geominfo = Locations.objects.filter(document=self.request.GET.get('doc_pk'))
        if geominfo.exists():
            initial['geom'] = geominfo[0].geom

        if latlonginfo.exists():
            initial['doc_latitude'] = latlonginfo[0].doc_latitude
            initial['doc_longitude'] = latlonginfo[0].doc_longitude

        if docinfo.doc_statewide:
            initial['statewide'] = "yes"
        else:
            initial['statewide'] = "no"
        initial['counties'] = geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).filter(docgeowords__dgeo_doc_fk__doc_pk=self.request.GET.get('doc_pk'))
        initial['cities'] = geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).filter(docgeowords__dgeo_doc_fk__doc_pk=self.request.GET.get('doc_pk'))

        initial['doc_approve_noe'] = docinfo.doc_approve_noe
        initial['doc_carryout_noe'] = docinfo.doc_carryout_noe

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

        context['docinfo'] = documents.objects.get(pk=self.request.GET.get('doc_pk'))
        context['attachments'] = docattachments.objects.filter(datt_doc_fk=self.request.GET.get('doc_pk'))

        return context

    def form_valid(self,form):
        data = form.cleaned_data
        doc = documents.objects.get(pk=self.request.POST.get('doc_pk'))
        prj = projects.objects.get(pk=doc.doc_prj_fk.prj_pk)

        if self.request.POST.get("mode") == 'accept':
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

            doc.doc_title = data['doc_title']
            doc.doc_description = data['doc_description']
            doc.doc_conname = data['doc_conname']
            doc.doc_conemail = data['doc_conemail']
            doc.doc_conphone = data['doc_conphone']
            doc.doc_conaddress1 = data['doc_conaddress1']
            doc.doc_conaddress2 = data['doc_conaddress2']
            doc.doc_concity = data['doc_concity']
            doc.doc_constate = data['doc_constate']
            doc.doc_conzip = data['doc_conzip']
            doc.doc_location = data['doc_location']
            doc_county = ""

            for cnty in data['counties']:
                doc_county += cnty.geow_shortname + ","

            doc_county = doc_county[:-1]
            if len(doc_county) > 64:
                doc_county = doc_county[:64]

            doc_city = ""

            for cty in data['cities']:
                doc_city += cty.geow_shortname + ","

            doc_city = doc_city[:-1]
            if len(doc_city) > 64:
                doc_city = doc_city[:64]
            doc.doc_county = doc_county
            doc.doc_city = doc_city
            doc.doc_approve_noe = data['doc_approve_noe']
            doc.doc_carryout_noe = data['doc_carryout_noe']
            doc.doc_exministerial = doc_exministerial
            doc.doc_exdeclared = doc_exdeclared
            doc.doc_exemergency = doc_exemergency
            doc.doc_excategorical = doc_excategorical
            doc.doc_exstatutory = doc_exstatutory
            doc.doc_exnumber = doc_exnumber
            doc.doc_exreasons = data['doc_exreasons']

            if prj.prj_schno:
                doc.doc_schno = prj.prj_schno
            else:
                doc.doc_schno = generate_schno(8)

            doc.doc_visible = True
            doc.doc_pending = False
            doc.doc_plannerreview = False
            doc.doc_plannerregion = 0
            doc.doc_clerknotes = data['doc_clerknotes']
            doc.save()
            prj.prj_title = data['prj_title']
            prj.prj_description = data['prj_description']

            if not prj.prj_schno:
                prj.prj_schno = doc.doc_schno
            prj.prj_pending = False
            prj.prj_plannerreview = False
            prj.save()

            try:
                geometry = Locations.objects.get(document=doc.pk)
                geometry.geom = data['geom']
            except Locations.DoesNotExist:
                geometry = Locations(document=doc,geom=data['geom'])
            geometry.save()

            try:
                coords = latlongs.objects.get(pk=doc.pk)
                coords.doc_latitude = data['doc_latitude']
                coords.doc_longitude = data['doc_longitude']
            except latlongs.DoesNotExist:
                coords = latlongs(doc_pk=doc.pk,doc_prj_fk=prj,doc_doctype="NOE",doc_latitude=data['doc_latitude'],doc_longitude=data['doc_longitude'])
            coords.save()

            docgeowords.objects.filter(dgeo_doc_fk__doc_pk=doc.pk).delete()

            if data['statewide'] == 'no':
                for cnty in data['counties']:
                    geowrds_cnty = docgeowords(dgeo_geow_fk=cnty,dgeo_doc_fk=doc,dgeo_rank=1)
                    geowrds_cnty.save()

                for cty in data['cities']:
                    geowrds_city = docgeowords(dgeo_geow_fk=cty,dgeo_doc_fk=doc,dgeo_rank=1)
                    geowrds_city.save()

            if settings.SENDEMAIL:
                email_acceptance(self)

        elif self.request.POST.get('mode') == 'reject':
            if settings.SENDEMAIL:
                email_demotiontodraft(self,doc)
            doc.doc_draft = True
            doc.doc_pending = False
            doc.save()

        return super(pendingdetail_noe,self).form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(pendingdetail_noe, self).dispatch(*args, **kwargs)

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
        latinfo = keywords.objects.filter(dockeywords__dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(keyw_keyl_fk__keyl_pk=1001)
        devinfo = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1010)
        issinfo= keywords.objects.filter(dockeywords__dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(keyw_keyl_fk__keyl_pk=1002)
        raginfo = reviewingagencies.objects.filter(docreviews__drag_doc_fk__doc_pk=self.request.GET.get('doc_pk'))
        dkey_comment_actions = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_pk=1018)
        dkey_comment_dev = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_pk=11001)
        dkey_comment_issues = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_pk=2034)
        
        initial['prj_title'] = docinfo.doc_prj_fk.prj_title
        initial['prj_description'] = docinfo.doc_prj_fk.prj_description
        initial['doc_title'] = docinfo.doc_title
        initial['doc_description'] = docinfo.doc_description
        initial['doc_conname'] = docinfo.doc_conname
        initial['doc_conemail'] = docinfo.doc_conemail
        initial['doc_conphone'] = docinfo.doc_conphone
        initial['doc_conaddress1'] = docinfo.doc_conaddress1
        initial['doc_conaddress2'] = docinfo.doc_conaddress2
        initial['doc_concity'] = docinfo.doc_concity
        initial['doc_constate'] = docinfo.doc_constate
        initial['doc_conzip'] = docinfo.doc_conzip.strip
        initial['doc_location'] = docinfo.doc_location

        geominfo = Locations.objects.filter(document=self.request.GET.get('doc_pk'))
        if geominfo.exists():
            initial['geom'] = geominfo[0].geom

        if latlonginfo.exists():
            initial['doc_latitude'] = latlonginfo[0].doc_latitude
            initial['doc_longitude'] = latlonginfo[0].doc_longitude

        if docinfo.doc_statewide:
            initial['statewide'] = "yes"
        else:
            initial['statewide'] = "no"
        initial['counties'] = geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).filter(docgeowords__dgeo_doc_fk__doc_pk=self.request.GET.get('doc_pk'))
        initial['cities'] = geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).filter(docgeowords__dgeo_doc_fk__doc_pk=self.request.GET.get('doc_pk'))

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

        if latinfo.exists():
            initial['actions'] = latinfo

        for dev in devinfo:
            if dev.dkey_keyw_fk.keyw_pk > 4000:
                if dev.dkey_keyw_fk.keyw_pk < 5000:
                    initial['devtrans'] = True
                    initial['devtrans_id'] = dev.dkey_keyw_fk.keyw_pk
                    initial['devtrans_comment'] = dev.dkey_comment
            if dev.dkey_keyw_fk.keyw_pk > 3000:
                if dev.dkey_keyw_fk.keyw_pk < 4000:
                    initial['devpower'] = True
                    initial['devpower_id'] = dev.dkey_keyw_fk.keyw_pk
                    initial['devpower_comment'] = dev.dkey_comment
                    initial['devpower_val1'] = dev.dkey_value1
            if dev.dkey_keyw_fk.keyw_pk > 5000:
                if dev.dkey_keyw_fk.keyw_pk < 6000:
                    initial['devwaste'] = True
                    initial['devwaste_id'] = dev.dkey_keyw_fk.keyw_pk
                    initial['devwaste_comment'] = dev.dkey_comment
            if dev.dkey_keyw_fk.keyw_pk == 6001:
                initial['dev6001'] = True
                initial['dev6001_val1'] = dev.dkey_value1
                initial['dev6001_val2'] = dev.dkey_value2
            elif dev.dkey_keyw_fk.keyw_pk == 6002:
                initial['dev6002'] = True
                initial['dev6002_val1'] = dev.dkey_value1
                initial['dev6002_val2'] = dev.dkey_value2
                initial['dev6002_val3'] = dev.dkey_value3
            elif dev.dkey_keyw_fk.keyw_pk == 6003:
                initial['dev6003'] = True
                initial['dev6003_val1'] = dev.dkey_value1
                initial['dev6003_val2'] = dev.dkey_value2
                initial['dev6003_val3'] = dev.dkey_value3
            elif dev.dkey_keyw_fk.keyw_pk == 6004:
                initial['dev6004'] = True
                initial['dev6004_val1'] = dev.dkey_value1
                initial['dev6004_val2'] = dev.dkey_value2
                initial['dev6004_val3'] = dev.dkey_value3
            elif dev.dkey_keyw_fk.keyw_pk == 7001:
                initial['dev7001'] = True
                initial['dev7001_val1'] = dev.dkey_value1
            elif dev.dkey_keyw_fk.keyw_pk == 8001:
                initial['dev8001'] = True
                initial['dev8001_val1'] = dev.dkey_value1
            elif dev.dkey_keyw_fk.keyw_pk == 9001:
                initial['dev9001'] = True
                initial['dev9001_val1'] = dev.dkey_value1
                initial['dev9001_val2'] = dev.dkey_value2
            elif dev.dkey_keyw_fk.keyw_pk == 10001:
                initial['dev10001'] = True
                initial['dev10001_val1'] = dev.dkey_value1
            elif dev.dkey_keyw_fk.keyw_pk == 11001:
                initial['dev11001'] = True

        if issinfo.exists():
            initial['issues'] = issinfo

        if raginfo.exists():
            initial['ragencies'] = raginfo

        return initial

    def get_context_data(self, **kwargs):
        context = super(pendingdetail_nop, self).get_context_data(**kwargs)
        context['docinfo'] = documents.objects.get(pk=self.request.GET.get('doc_pk'))
        context['lats'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1001)
        context['devs'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1010)
        context['isss'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1002)
        context['attachments'] = docattachments.objects.filter(datt_doc_fk=self.request.GET.get('doc_pk'))
        holidayslist = holidays.objects.filter(hday_date__gte=datetime.now())
        hlist = "["
        for h in holidayslist:
            hlist += "\"" + h.hday_date.strftime('%Y-%m-%d') + "\"" + ","

        hlist = hlist[:-1]
        hlist += "];"
        context['holidays'] = hlist

        return context

    def form_valid(self,form):
        data = form.cleaned_data
        doc = documents.objects.get(pk=self.request.POST.get('doc_pk'))
        prj = projects.objects.get(pk=doc.doc_prj_fk.prj_pk)

        if self.request.POST.get('mode') == 'assign':
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

            doc.doc_title = data['doc_title']
            doc.doc_description = data['doc_description']
            doc.doc_conname = data['doc_conname']
            doc.doc_conemail = data['doc_conemail']
            doc.doc_conphone = data['doc_conphone']
            doc.doc_conaddress1 = data['doc_conaddress1']
            doc.doc_conaddress2 = doc_conaddress2
            doc.doc_concity = data['doc_concity']
            doc.doc_constate = data['doc_constate']
            doc.doc_conzip = data['doc_conzip']
            doc.doc_location = data['doc_location']

            doc_statewide = False

            if data['statewide'] == 'yes':
                doc_statewide = True

            doc.doc_statewide = doc_statewide

            doc_county = ""

            if data['statewide'] == 'no':
                for cnty in data['counties']:
                    doc_county += cnty.geow_shortname + ","

                doc_county = doc_county[:-1]
                if len(doc_county) > 64:
                    doc_county = doc_county[:64]

            doc_city = ""

            if data['statewide'] == 'no':
                for cty in data['cities']:
                    doc_city += cty.geow_shortname + ","

                doc_city = doc_city[:-1]
                if len(doc_city) > 64:
                    doc_city = doc_city[:64]

            doc.doc_county = doc_county
            doc.doc_city = doc_city
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
            doc.doc_dept = data['doc_dept']
            doc.doc_clear = data['doc_clear']
            doc.doc_clerknotes = data['doc_clerknotes']
            doc.doc_bia = data['doc_bia']
            doc.save()
            prj.prj_title = data['prj_title']
            prj.prj_description = data['prj_description']
            if prj.prj_pending:
                prj.prj_pending = False
                prj.prj_plannerreview = True
            prj.save()

            try:
                geometry = Locations.objects.get(document=doc.pk)
                geometry.geom = data['geom']
            except Locations.DoesNotExist:
                geometry = Locations(document=doc,geom=data['geom'])
            geometry.save()

            try:
                coords = latlongs.objects.get(pk=doc.pk)
                coords.doc_latitude = data['doc_latitude']
                coords.doc_longitude = data['doc_longitude']
            except latlongs.DoesNotExist:
                coords = latlongs(doc_pk=doc.pk,doc_prj_fk=prj,doc_doctype="NOP",doc_latitude=data['doc_latitude'],doc_longitude=data['doc_longitude'])
            coords.save()

            docgeowords.objects.filter(dgeo_doc_fk__doc_pk=doc.pk).delete()

            if data['statewide'] == 'no':
                for cnty in data['counties']:
                    geowrds_cnty = docgeowords(dgeo_geow_fk=cnty,dgeo_doc_fk=doc,dgeo_rank=1)
                    geowrds_cnty.save()

                for cty in data['cities']:
                    geowrds_city = docgeowords(dgeo_geow_fk=cty,dgeo_doc_fk=doc,dgeo_rank=1)
                    geowrds_city.save()

            dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc.pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1001).delete()

            for a in data['actions']:
                if a.keyw_pk == 1018:
                    adockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=a,dkey_comment=data['dkey_comment_actions'],dkey_rank=0)
                else:
                    adockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=a,dkey_rank=0)
                adockeyw.save()
            
            dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc.pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1010).delete()

            devtypes = keywords.objects.filter(keyw_keyl_fk__keyl_pk=1010).filter(keyw_pk__gte=6001).filter(keyw_pk__lte=11001)
            for d in devtypes:
                if self.request.POST.get('dev'+str(d.keyw_pk)):
                    if d.keyw_pk == 11001:
                        ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=d,dkey_comment=self.request.POST.get('dkey_comment_dev'),dkey_value1=self.request.POST.get('dev'+str(d.keyw_pk)+'_val1'),dkey_value2=self.request.POST.get('dev'+str(d.keyw_pk)+'_val2'),dkey_value3=self.request.POST.get('dev'+str(d.keyw_pk)+'_val3'),dkey_rank=0)
                    else:
                        ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=d,dkey_value1=self.request.POST.get('dev'+str(d.keyw_pk)+'_val1'),dkey_value2=self.request.POST.get('dev'+str(d.keyw_pk)+'_val2'),dkey_value3=self.request.POST.get('dev'+str(d.keyw_pk)+'_val3'),dkey_rank=0)
                    ddockeyw.save()
            if data['devtrans']:
                ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=data['devtrans_id'],dkey_comment=data['devtrans_comment'],dkey_value1=None,dkey_value2=None,dkey_value3=None,dkey_rank=0)
                ddockeyw.save()
            if data['devpower']:
                ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=data['devpower_id'],dkey_comment=data['devpower_comment'],dkey_value1=data['devpower_val1'],dkey_value2=None,dkey_value3=None,dkey_rank=0)
                ddockeyw.save()
            if data['devwaste']:
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

            if settings.SENDEMAIL:
                email_assigned(self,doc)

        if self.request.POST.get('mode') == 'reject':
            if settings.SENDEMAIL:
                email_demotiontodraft(self,doc)
            doc.doc_draft = True
            doc.doc_pending = False
            doc.save()

        return super(pendingdetail_nop,self).form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(pendingdetail_nop, self).dispatch(*args, **kwargs)

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

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(review, self).dispatch(*args, **kwargs)

def ReviewListQuery(request):
    queryset = documents.objects.filter(doc_plannerreview=True).order_by('-doc_received','-doc_pk')
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
        latinfo = keywords.objects.filter(dockeywords__dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(keyw_keyl_fk__keyl_pk=1001)
        devinfo = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1010)
        issinfo= keywords.objects.filter(dockeywords__dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(keyw_keyl_fk__keyl_pk=1002)
        raginfo = reviewingagencies.objects.filter(docreviews__drag_doc_fk__doc_pk=self.request.GET.get('doc_pk'))
        dkey_comment_actions = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_pk=1018)
        dkey_comment_dev = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_pk=11001)
        dkey_comment_issues = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_pk=2034)
        
        docinfo.doc_lastlooked_userid = self.request.user
        docinfo.save()

        initial['prj_title'] = docinfo.doc_prj_fk.prj_title
        initial['prj_description'] = docinfo.doc_prj_fk.prj_description
        initial['doc_title'] = docinfo.doc_title
        initial['doc_description'] = docinfo.doc_description
        initial['doc_conname'] = docinfo.doc_conname
        initial['doc_conemail'] = docinfo.doc_conemail
        initial['doc_conphone'] = docinfo.doc_conphone
        initial['doc_conaddress1'] = docinfo.doc_conaddress1
        initial['doc_conaddress2'] = docinfo.doc_conaddress2
        initial['doc_concity'] = docinfo.doc_concity
        initial['doc_constate'] = docinfo.doc_constate
        initial['doc_conzip'] = docinfo.doc_conzip.strip
        initial['doc_location'] = docinfo.doc_location

        geominfo = Locations.objects.filter(document=self.request.GET.get('doc_pk'))
        if geominfo.exists():
            initial['geom'] = geominfo[0].geom
        
        if latlonginfo.exists():
            initial['doc_latitude'] = latlonginfo[0].doc_latitude
            initial['doc_longitude'] = latlonginfo[0].doc_longitude

        if docinfo.doc_statewide:
            initial['statewide'] = "yes"
        else:
            initial['statewide'] = "no"
        initial['counties'] = geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).filter(docgeowords__dgeo_doc_fk__doc_pk=self.request.GET.get('doc_pk'))
        initial['cities'] = geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).filter(docgeowords__dgeo_doc_fk__doc_pk=self.request.GET.get('doc_pk'))

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
                    initial['devtrans'] = True
                    initial['devtrans_id'] = dev.dkey_keyw_fk.keyw_pk
                    initial['devtrans_comment'] = dev.dkey_comment
            if dev.dkey_keyw_fk.keyw_pk > 3000:
                if dev.dkey_keyw_fk.keyw_pk < 4000:
                    initial['devpower'] = True
                    initial['devpower_id'] = dev.dkey_keyw_fk.keyw_pk
                    initial['devpower_comment'] = dev.dkey_comment
                    initial['devpower_val1'] = dev.dkey_value1
            if dev.dkey_keyw_fk.keyw_pk > 5000:
                if dev.dkey_keyw_fk.keyw_pk < 6000:
                    initial['devwaste'] = True
                    initial['devwaste_id'] = dev.dkey_keyw_fk.keyw_pk
                    initial['devwaste_comment'] = dev.dkey_comment
            if dev.dkey_keyw_fk.keyw_pk == 6001:
                initial['dev6001'] = True
                initial['dev6001_val1'] = dev.dkey_value1
                initial['dev6001_val2'] = dev.dkey_value2
            elif dev.dkey_keyw_fk.keyw_pk == 6002:
                initial['dev6002'] = True
                initial['dev6002_val1'] = dev.dkey_value1
                initial['dev6002_val2'] = dev.dkey_value2
                initial['dev6002_val3'] = dev.dkey_value3
            elif dev.dkey_keyw_fk.keyw_pk == 6003:
                initial['dev6003'] = True
                initial['dev6003_val1'] = dev.dkey_value1
                initial['dev6003_val2'] = dev.dkey_value2
                initial['dev6003_val3'] = dev.dkey_value3
            elif dev.dkey_keyw_fk.keyw_pk == 6004:
                initial['dev6004'] = True
                initial['dev6004_val1'] = dev.dkey_value1
                initial['dev6004_val2'] = dev.dkey_value2
                initial['dev6004_val3'] = dev.dkey_value3
            elif dev.dkey_keyw_fk.keyw_pk == 7001:
                initial['dev7001'] = True
                initial['dev7001_val1'] = dev.dkey_value1
            elif dev.dkey_keyw_fk.keyw_pk == 8001:
                initial['dev8001'] = True
                initial['dev8001_val1'] = dev.dkey_value1
            elif dev.dkey_keyw_fk.keyw_pk == 9001:
                initial['dev9001'] = True
                initial['dev9001_val1'] = dev.dkey_value1
                initial['dev9001_val2'] = dev.dkey_value2
            elif dev.dkey_keyw_fk.keyw_pk == 10001:
                initial['dev10001'] = True
                initial['dev10001_val1'] = dev.dkey_value1
            elif dev.dkey_keyw_fk.keyw_pk == 11001:
                initial['dev11001'] = True

        if issinfo.exists():
            initial['issues'] = issinfo

        if raginfo.exists():
            initial['ragencies'] = raginfo

        initial['doc_dept'] = docinfo.doc_dept
        initial['doc_clear'] = docinfo.doc_clear

        initial['doc_clerknotes'] = docinfo.doc_clerknotes

        return initial

    def get_context_data(self, **kwargs):
        context = super(reviewdetail_noc, self).get_context_data(**kwargs)
        context['docinfo'] = documents.objects.get(pk=self.request.GET.get('doc_pk'))
        context['lats'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1001)
        context['devs'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1010)
        context['isss'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1002)
        context['attachments'] = docattachments.objects.filter(datt_doc_fk=self.request.GET.get('doc_pk'))
        holidayslist = holidays.objects.filter(hday_date__gte=datetime.now())
        hlist = "["
        for h in holidayslist:
            hlist += "\"" + h.hday_date.strftime('%Y-%m-%d') + "\"" + ","

        hlist = hlist[:-1]
        hlist += "];"
        context['holidays'] = hlist

        return context

    def form_valid(self,form):
        data = form.cleaned_data
        doc = documents.objects.get(pk=self.request.POST.get('doc_pk'))
        prj = projects.objects.get(pk=doc.doc_prj_fk.prj_pk)

        if self.request.POST.get('mode') == 'accept':
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

            doc.doc_title = data['doc_title']
            doc.doc_description = data['doc_description']
            doc.doc_conname = data['doc_conname']
            doc.doc_conemail = data['doc_conemail']
            doc.doc_conphone = data['doc_conphone']
            doc.doc_conaddress1 = data['doc_conaddress1']
            doc.doc_conaddress2 = doc_conaddress2
            doc.doc_concity = data['doc_concity']
            doc.doc_constate = data['doc_constate']
            doc.doc_conzip = data['doc_conzip']
            doc.doc_location = data['doc_location']

            doc_statewide = False

            if data['statewide'] == 'yes':
                doc_statewide = True

            doc.doc_statewide = doc_statewide

            doc_county = ""

            if data['statewide'] == 'no':
                for cnty in data['counties']:
                    doc_county += cnty.geow_shortname + ","

                doc_county = doc_county[:-1]
                if len(doc_county) > 64:
                    doc_county = doc_county[:64]

            doc_city = ""

            if data['statewide'] == 'no':
                for cty in data['cities']:
                    doc_city += cty.geow_shortname + ","

                doc_city = doc_city[:-1]
                if len(doc_city) > 64:
                    doc_city = doc_city[:64]

            doc.doc_county = doc_county
            doc.doc_city = doc_city
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

            if prj.prj_schno:
                doc.doc_schno = prj.prj_schno
            else:
                if doc.doc_bia:
                    doc.doc_schno = generate_biaschno()
                else:
                    doc.doc_schno = generate_schno(doc.doc_plannerregion)

            doc.doc_review = True
            doc.doc_plannerreview = False
            doc.doc_visible = True
            doc.doc_dept = data['doc_dept']
            doc.doc_clear = data['doc_clear']
            doc.doc_clerknotes = data['doc_clerknotes']
            doc.doc_assigned_userid = self.request.user
            doc.save()

            prj.prj_title = data['prj_title']
            prj.prj_description = data['prj_description']
            if not prj.prj_schno:
                prj.prj_schno = doc.doc_schno
            prj.prj_plannerreview = False
            prj.save()

            try:
                geometry = Locations.objects.get(document=doc.pk)
                geometry.geom = data['geom']
            except Locations.DoesNotExist:
                geometry = Locations(document=doc,geom=data['geom'])
            geometry.save()

            try:
                coords = latlongs.objects.get(pk=doc.pk)
                coords.doc_latitude = data['doc_latitude']
                coords.doc_longitude = data['doc_longitude']
            except latlongs.DoesNotExist:
                coords = latlongs(doc_pk=doc.pk,doc_prj_fk=prj,doc_doctype="NOC",doc_latitude=data['doc_latitude'],doc_longitude=data['doc_longitude'])
            coords.save()

            docgeowords.objects.filter(dgeo_doc_fk__doc_pk=doc.pk).delete()

            if data['statewide'] == 'no':
                for cnty in data['counties']:
                    geowrds_cnty = docgeowords(dgeo_geow_fk=cnty,dgeo_doc_fk=doc,dgeo_rank=1)
                    geowrds_cnty.save()

                for cty in data['cities']:
                    geowrds_city = docgeowords(dgeo_geow_fk=cty,dgeo_doc_fk=doc,dgeo_rank=1)
                    geowrds_city.save()

            dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc.pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1001).delete()

            for a in data['actions']:
                if a.keyw_pk == 1018:
                    adockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=a,dkey_comment=data['dkey_comment_actions'],dkey_rank=0)
                else:
                    adockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=a,dkey_rank=0)
                adockeyw.save()

            dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc.pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1010).delete()
            
            devtypes = keywords.objects.filter(keyw_keyl_fk__keyl_pk=1010).filter(keyw_pk__gte=6001).filter(keyw_pk__lte=11001)
            for d in devtypes:
                if self.request.POST.get('dev'+str(d.keyw_pk)):
                    if d.keyw_pk == 11001:
                        ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=d,dkey_comment=self.request.POST.get('dkey_comment_dev'),dkey_value1=self.request.POST.get('dev'+str(d.keyw_pk)+'_val1'),dkey_value2=self.request.POST.get('dev'+str(d.keyw_pk)+'_val2'),dkey_value3=self.request.POST.get('dev'+str(d.keyw_pk)+'_val3'),dkey_rank=0)
                    else:
                        ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=d,dkey_value1=self.request.POST.get('dev'+str(d.keyw_pk)+'_val1'),dkey_value2=self.request.POST.get('dev'+str(d.keyw_pk)+'_val2'),dkey_value3=self.request.POST.get('dev'+str(d.keyw_pk)+'_val3'),dkey_rank=0)
                    ddockeyw.save()
            if data['devtrans']:
                ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=data['devtrans_id'],dkey_comment=data['devtrans_comment'],dkey_value1=None,dkey_value2=None,dkey_value3=None,dkey_rank=0)
                ddockeyw.save()
            if data['devpower']:
                ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=data['devpower_id'],dkey_comment=data['devpower_comment'],dkey_value1=data['devpower_val1'],dkey_value2=None,dkey_value3=None,dkey_rank=0)
                ddockeyw.save()
            if data['devwaste']:
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

            if settings.SENDEMAIL:
                email_inreview(self,doc)

        elif self.request.POST.get('mode') == 'reject':
            if settings.SENDEMAIL:
                email_rejection(self)
            delete_clearinghouse_document(self)

        return super(reviewdetail_noc,self).form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(reviewdetail_noc, self).dispatch(*args, **kwargs)

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
        latinfo = keywords.objects.filter(dockeywords__dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(keyw_keyl_fk__keyl_pk=1001)
        devinfo = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1010)
        issinfo= keywords.objects.filter(dockeywords__dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(keyw_keyl_fk__keyl_pk=1002)
        raginfo = reviewingagencies.objects.filter(docreviews__drag_doc_fk__doc_pk=self.request.GET.get('doc_pk'))
        dkey_comment_actions = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_pk=1018)
        dkey_comment_dev = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_pk=11001)
        dkey_comment_issues = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_pk=2034)

        docinfo.doc_lastlooked_userid = self.request.user
        docinfo.save()
        
        initial['prj_title'] = docinfo.doc_prj_fk.prj_title
        initial['prj_description'] = docinfo.doc_prj_fk.prj_description
        initial['doc_title'] = docinfo.doc_title
        initial['doc_description'] = docinfo.doc_description
        initial['doc_conname'] = docinfo.doc_conname
        initial['doc_conemail'] = docinfo.doc_conemail
        initial['doc_conphone'] = docinfo.doc_conphone
        initial['doc_conaddress1'] = docinfo.doc_conaddress1
        initial['doc_conaddress2'] = docinfo.doc_conaddress2
        initial['doc_concity'] = docinfo.doc_concity
        initial['doc_constate'] = docinfo.doc_constate
        initial['doc_conzip'] = docinfo.doc_conzip.strip
        initial['doc_location'] = docinfo.doc_location

        geominfo = Locations.objects.filter(document=self.request.GET.get('doc_pk'))
        if geominfo.exists():
            initial['geom'] = geominfo[0].geom

        if latlonginfo.exists():
            initial['doc_latitude'] = latlonginfo[0].doc_latitude
            initial['doc_longitude'] = latlonginfo[0].doc_longitude

        if docinfo.doc_statewide:
            initial['statewide'] = "yes"
        else:
            initial['statewide'] = "no"
        initial['counties'] = geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).filter(docgeowords__dgeo_doc_fk__doc_pk=self.request.GET.get('doc_pk'))
        initial['cities'] = geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).filter(docgeowords__dgeo_doc_fk__doc_pk=self.request.GET.get('doc_pk'))

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

        if latinfo.exists():
            initial['actions'] = latinfo

        for dev in devinfo:
            if dev.dkey_keyw_fk.keyw_pk > 4000:
                if dev.dkey_keyw_fk.keyw_pk < 5000:
                    initial['devtrans'] = True
                    initial['devtrans_id'] = dev.dkey_keyw_fk.keyw_pk
                    initial['devtrans_comment'] = dev.dkey_comment
            if dev.dkey_keyw_fk.keyw_pk > 3000:
                if dev.dkey_keyw_fk.keyw_pk < 4000:
                    initial['devpower'] = True
                    initial['devpower_id'] = dev.dkey_keyw_fk.keyw_pk
                    initial['devpower_comment'] = dev.dkey_comment
                    initial['devpower_val1'] = dev.dkey_value1
            if dev.dkey_keyw_fk.keyw_pk > 5000:
                if dev.dkey_keyw_fk.keyw_pk < 6000:
                    initial['devwaste'] = True
                    initial['devwaste_id'] = dev.dkey_keyw_fk.keyw_pk
                    initial['devwaste_comment'] = dev.dkey_comment
            if dev.dkey_keyw_fk.keyw_pk == 6001:
                initial['dev6001'] = True
                initial['dev6001_val1'] = dev.dkey_value1
                initial['dev6001_val2'] = dev.dkey_value2
            elif dev.dkey_keyw_fk.keyw_pk == 6002:
                initial['dev6002'] = True
                initial['dev6002_val1'] = dev.dkey_value1
                initial['dev6002_val2'] = dev.dkey_value2
                initial['dev6002_val3'] = dev.dkey_value3
            elif dev.dkey_keyw_fk.keyw_pk == 6003:
                initial['dev6003'] = True
                initial['dev6003_val1'] = dev.dkey_value1
                initial['dev6003_val2'] = dev.dkey_value2
                initial['dev6003_val3'] = dev.dkey_value3
            elif dev.dkey_keyw_fk.keyw_pk == 6004:
                initial['dev6004'] = True
                initial['dev6004_val1'] = dev.dkey_value1
                initial['dev6004_val2'] = dev.dkey_value2
                initial['dev6004_val3'] = dev.dkey_value3
            elif dev.dkey_keyw_fk.keyw_pk == 7001:
                initial['dev7001'] = True
                initial['dev7001_val1'] = dev.dkey_value1
            elif dev.dkey_keyw_fk.keyw_pk == 8001:
                initial['dev8001'] = True
                initial['dev8001_val1'] = dev.dkey_value1
            elif dev.dkey_keyw_fk.keyw_pk == 9001:
                initial['dev9001'] = True
                initial['dev9001_val1'] = dev.dkey_value1
                initial['dev9001_val2'] = dev.dkey_value2
            elif dev.dkey_keyw_fk.keyw_pk == 10001:
                initial['dev10001'] = True
                initial['dev10001_val1'] = dev.dkey_value1
            elif dev.dkey_keyw_fk.keyw_pk == 11001:
                initial['dev11001'] = True

        if issinfo.exists():
            initial['issues'] = issinfo

        if raginfo.exists():
            initial['ragencies'] = raginfo

        initial['doc_dept'] = docinfo.doc_dept
        initial['doc_clear'] = docinfo.doc_clear

        initial['doc_clerknotes'] = docinfo.doc_clerknotes

        return initial

    def get_context_data(self, **kwargs):
        context = super(reviewdetail_nop, self).get_context_data(**kwargs)
        context['docinfo'] = documents.objects.get(pk=self.request.GET.get('doc_pk'))
        context['lats'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1001)
        context['devs'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1010)
        context['isss'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=self.request.GET.get('doc_pk')).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1002)
        context['attachments'] = docattachments.objects.filter(datt_doc_fk=self.request.GET.get('doc_pk'))
        holidayslist = holidays.objects.filter(hday_date__gte=datetime.now())
        hlist = "["
        for h in holidayslist:
            hlist += "\"" + h.hday_date.strftime('%Y-%m-%d') + "\"" + ","

        hlist = hlist[:-1]
        hlist += "];"
        context['holidays'] = hlist

        return context

    def form_valid(self,form):
        data = form.cleaned_data
        doc = documents.objects.get(pk=self.request.POST.get('doc_pk'))
        prj = projects.objects.get(pk=doc.doc_prj_fk.prj_pk)

        if self.request.POST.get('mode') == 'accept':
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

            doc.doc_title = data['doc_title']
            doc.doc_description = data['doc_description']
            doc.doc_conname = data['doc_conname']
            doc.doc_conemail = data['doc_conemail']
            doc.doc_conphone = data['doc_conphone']
            doc.doc_conaddress1 = data['doc_conaddress1']
            doc.doc_conaddress2 = doc_conaddress2
            doc.doc_concity = data['doc_concity']
            doc.doc_constate = data['doc_constate']
            doc.doc_conzip = data['doc_conzip']
            doc.doc_location = data['doc_location']

            doc_statewide = False

            if data['statewide'] == 'yes':
                doc_statewide = True

            doc.doc_statewide = doc_statewide

            doc_county = ""

            if data['statewide'] == 'no':
                for cnty in data['counties']:
                    doc_county += cnty.geow_shortname + ","

                doc_county = doc_county[:-1]
                if len(doc_county) > 64:
                    doc_county = doc_county[:64]

            doc_city = ""

            if data['statewide'] == 'no':
                for cty in data['cities']:
                    doc_city += cty.geow_shortname + ","

                doc_city = doc_city[:-1]
                if len(doc_city) > 64:
                    doc_city = doc_city[:64]

            doc.doc_county = doc_county
            doc.doc_city = doc_city
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

            if prj.prj_schno:
                doc.doc_schno = prj.prj_schno
            else:
                if doc.doc_bia:
                    doc.doc_schno = generate_biaschno()
                else:
                    doc.doc_schno = generate_schno(doc.doc_plannerregion)

            doc.doc_review = True
            doc.doc_plannerreview = False
            doc.doc_visible = True
            doc.doc_dept = data['doc_dept']
            doc.doc_clear = data['doc_clear']
            doc.doc_clerknotes = data['doc_clerknotes']
            doc.doc_assigned_userid = self.request.user
            doc.save()

            prj.prj_title = data['prj_title']
            prj.prj_description = data['prj_description']
            if not prj.prj_schno:
                prj.prj_schno = doc.doc_schno
            prj.prj_plannerreview = False
            prj.save()

            try:
                geometry = Locations.objects.get(document=doc.pk)
                geometry.geom = data['geom']
            except Locations.DoesNotExist:
                geometry = Locations(document=doc,geom=data['geom'])
            geometry.save()

            try:
                coords = latlongs.objects.get(pk=doc.pk)
                coords.doc_latitude = data['doc_latitude']
                coords.doc_longitude = data['doc_longitude']
            except latlongs.DoesNotExist:
                coords = latlongs(doc_pk=doc.pk,doc_prj_fk=prj,doc_doctype="NOP",doc_latitude=data['doc_latitude'],doc_longitude=data['doc_longitude'])
            coords.save()

            docgeowords.objects.filter(dgeo_doc_fk__doc_pk=doc.pk).delete()

            if data['statewide'] == 'no':
                for cnty in data['counties']:
                    geowrds_cnty = docgeowords(dgeo_geow_fk=cnty,dgeo_doc_fk=doc,dgeo_rank=1)
                    geowrds_cnty.save()

                for cty in data['cities']:
                    geowrds_city = docgeowords(dgeo_geow_fk=cty,dgeo_doc_fk=doc,dgeo_rank=1)
                    geowrds_city.save()

            dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc.pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1001).delete()

            for a in data['actions']:
                if a.keyw_pk == 1018:
                    adockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=a,dkey_comment=data['dkey_comment_actions'],dkey_rank=0)
                else:
                    adockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=a,dkey_rank=0)
                adockeyw.save()

            dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc.pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1010).delete()

            devtypes = keywords.objects.filter(keyw_keyl_fk__keyl_pk=1010).filter(keyw_pk__gte=6001).filter(keyw_pk__lte=11001)
            for d in devtypes:
                if self.request.POST.get('dev'+str(d.keyw_pk)):
                    if d.keyw_pk == 11001:
                        ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=d,dkey_comment=self.request.POST.get('dkey_comment_dev'),dkey_value1=self.request.POST.get('dev'+str(d.keyw_pk)+'_val1'),dkey_value2=self.request.POST.get('dev'+str(d.keyw_pk)+'_val2'),dkey_value3=self.request.POST.get('dev'+str(d.keyw_pk)+'_val3'),dkey_rank=0)
                    else:
                        ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=d,dkey_value1=self.request.POST.get('dev'+str(d.keyw_pk)+'_val1'),dkey_value2=self.request.POST.get('dev'+str(d.keyw_pk)+'_val2'),dkey_value3=self.request.POST.get('dev'+str(d.keyw_pk)+'_val3'),dkey_rank=0)
                    ddockeyw.save()
            if data['devtrans']:
                ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=data['devtrans_id'],dkey_comment=data['devtrans_comment'],dkey_value1=None,dkey_value2=None,dkey_value3=None,dkey_rank=0)
                ddockeyw.save()
            if data['devpower']:
                ddockeyw = dockeywords(dkey_doc_fk=doc,dkey_keyw_fk=data['devpower_id'],dkey_comment=data['devpower_comment'],dkey_value1=data['devpower_val1'],dkey_value2=None,dkey_value3=None,dkey_rank=0)
                ddockeyw.save()
            if data['devwaste']:
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

            if settings.SENDEMAIL:
                email_inreview(self,doc)

        elif self.request.POST.get('mode') == 'reject':
            if settings.SENDEMAIL:
                email_rejection(self)
            delete_clearinghouse_document(self)

        return super(reviewdetail_nop,self).form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(reviewdetail_nop, self).dispatch(*args, **kwargs)

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

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(comment, self).dispatch(*args, **kwargs)

def CommentListQuery(request):
    set_rag_fk = request.user.get_profile().set_rag_fk.rag_pk
    queryset = docreviews.objects.filter(drag_rag_fk__rag_pk=set_rag_fk).filter(drag_doc_fk__doc_review=True).order_by('-drag_doc_fk__doc_received','-drag_doc_fk__doc_pk')
    return queryset

class commentdetail(ListView):
    template_name="ceqanet/commentdetail.html"
    context_object_name = "comments"

    def get_queryset(self):
        queryset = CommentDetailListQuery(self.request)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(commentdetail, self).get_context_data(**kwargs)

        doc_pk = self.request.GET.get('doc_pk')
        context['detail'] = documents.objects.get(doc_pk__exact=doc_pk)
        context['latlongs'] = latlongs.objects.filter(doc_pk=doc_pk)
        context['dev'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc_pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1010)
        context['actions'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc_pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1001)
        context['issues'] = dockeywords.objects.filter(dkey_doc_fk__doc_pk=doc_pk).filter(dkey_keyw_fk__keyw_keyl_fk__keyl_pk=1002)
        context['reviews'] = docreviews.objects.filter(drag_doc_fk__doc_pk=doc_pk)
        context['attachments'] = docattachments.objects.filter(datt_doc_fk=doc_pk)
        context['counties'] = geowords.objects.filter(geow_geol_fk=1001).filter(inlookup=True).filter(docgeowords__dgeo_doc_fk__doc_pk=doc_pk)
        context['cities'] = geowords.objects.filter(geow_geol_fk=1002).filter(inlookup=True).filter(docgeowords__dgeo_doc_fk__doc_pk=doc_pk)
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(commentdetail, self).dispatch(*args, **kwargs)

def CommentDetailListQuery(request):
    drag_pk = docreviews.objects.filter(drag_doc_fk=request.GET.get('doc_pk')).filter(drag_rag_fk=request.user.get_profile().set_rag_fk)
    queryset = doccomments.objects.filter(dcom_drag_fk=drag_pk).order_by('dcom_pk')
    return queryset

class commentadd(FormView):
    form_class = commentaddform
    template_name="ceqanet/commentadd.html"
 
    def get_success_url(self):
        success_url = "%s?doc_pk=%s" % (reverse_lazy('commentdetail'),self.request.GET.get('doc_pk'))
        return success_url

    def get_context_data(self, **kwargs):
        context = super(commentadd, self).get_context_data(**kwargs)

        context['doc_pk'] = self.request.GET.get('doc_pk')
        return context

    def form_valid(self,form):
        data = form.cleaned_data
        today = datetime.now()

        docreview = docreviews.objects.get(drag_doc_fk__doc_pk=self.request.GET.get('doc_pk'),drag_rag_fk__rag_pk=self.request.user.get_profile().set_rag_fk.rag_pk)

        if docreview.drag_numcomments:
            docreview.drag_numcomments = docreview.drag_numcomments + 1
        else:
            docreview.drag_numcomments = 1
        docreview.save()

        if data['commenttype'] == 'text':
            if data['dcom_textcomment']:
                doccomment = doccomments(dcom_drag_fk=docreview,dcom_doc_fk=docreview.drag_doc_fk,dcom_commentdate=today,dcom_textcomment=data['dcom_textcomment'],dcom_reviewer_userid=self.request.user)
                doccomment.save()
        elif data['commenttype'] == 'file':
            if data['dcom_filecomment']:
                doccomment = doccomments(dcom_drag_fk=docreview,dcom_doc_fk=docreview.drag_doc_fk,dcom_commentdate=today,dcom_filecomment=self.request.FILES['dcom_filecomment'],dcom_reviewer_userid=self.request.user)
                doccomment.save()

        if settings.SENDEMAIL:
            email_commentacceptance(self)

        return super(commentadd,self).form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(commentadd, self).dispatch(*args, **kwargs)

class showcomment(DetailView):
    model = doccomments
    template_name="ceqanet/showcomment.html"
    context_object_name = "doccomment"

def commentaccept(request):
    t = loader.get_template("ceqanet/commentaccept.html")
    c = RequestContext(request,{})
    return HttpResponse(t.render(c))

def accept(request):
    t = loader.get_template("ceqanet/accept.html")
    c = RequestContext(request,{})
    return HttpResponse(t.render(c))

class manageaccount(FormView):
    form_class = manageaccountform
    template_name = "ceqanet/manageaccount.html"

    def get_success_url(self):
        success_url = "%s" % (reverse_lazy('index'))
        return success_url

    def get_initial(self):
        initial = super(manageaccount, self).get_initial()

        try:
            us_query = self.request.user.get_profile()
            initial['confirstname'] = self.request.user.first_name
            initial['conlastname'] = self.request.user.last_name
            initial['conemail'] = self.request.user.email
            initial['conphone'] = us_query.conphone
        except UserProfile.DoesNotExist:
            pass
        return initial

    def form_valid(self,form):
        data = form.cleaned_data

        confirstname = data['confirstname']
        conlastname = data['conlastname']
        conemail = data['conemail']
        usr = self.request.user
        usr.first_name = confirstname
        usr.last_name = conlastname
        usr.email = conemail
        usr.save()

        conphone = data['conphone']

        us = self.request.user.get_profile()
        us.conphone = conphone
        us.save()

        return super(manageaccount,self).form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(manageaccount, self).dispatch(*args, **kwargs)

class requestupgrd(FormView):
    form_class = requestupgrdform
    template_name = "ceqanet/requestupgrd.html"

    def get_success_url(self):
        success_url = "%s" % (reverse_lazy('index'))
        return success_url

    def get_context_data(self, **kwargs):
        context = super(requestupgrd, self).get_context_data(**kwargs)
        
        isrequested = False

        if requestupgrade.objects.filter(user_id=self.request.user.pk).count() > 0:
            isrequested = True

        context['isrequested'] = isrequested

        return context

    def form_valid(self,form):
        data = form.cleaned_data

        rqst = requestupgrade(user_id=self.request.user,rqst_pending=True,rqst_type=data['rqst_type'],rqst_lag_fk=data['rqst_lag_fk'],rqst_rag_fk=data['rqst_rag_fk'],rqst_reason=data['rqst_reason'])
        rqst.save()

        if settings.SENDEMAIL:
            email_requestforupgrade(self,data)

        return super(requestupgrd,self).form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(requestupgrd, self).dispatch(*args, **kwargs)

class manageupgrades(ListView):
    template_name = "ceqanet/manageupgrades.html"
    context_object_name = "upgrades"

    def get_queryset(self):
        queryset = ManageUpgradesListQuery(self.request)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(manageupgrades, self).get_context_data(**kwargs)

        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(manageupgrades, self).dispatch(*args, **kwargs)

def ManageUpgradesListQuery(request):
    queryset = requestupgrade.objects.filter(rqst_pending=True)
    return queryset

class manageupgrade(FormView):
    form_class = manageupgradeform
    template_name = "ceqanet/manageupgrade.html"

    def get_success_url(self):
        success_url = "%s" % (reverse_lazy('manageupgrades'))
        return success_url

    def get_context_data(self, **kwargs):
        context = super(manageupgrade, self).get_context_data(**kwargs)
        
        context['rqstupgrd'] = requestupgrade.objects.get(user_id=self.request.GET.get('user_id'))

        return context

    def form_valid(self,form):
        data = form.cleaned_data

        rqstupgrd = requestupgrade.objects.get(user_id=self.request.POST.get('user_id'))

        if data['allowupgrade'] == 'yes':
            usr = User.objects.get(pk=self.request.POST.get('user_id'))
            usrprof = UserProfile.objects.get(user_id=self.request.POST.get('user_id'))
            if rqstupgrd.rqst_type == 'lead':
                grp = Group.objects.get(name="leads")
                usrprof.set_lag_fk = rqstupgrd.rqst_lag_fk
            else:
                grp = Group.objects.get(name="reviewers")
                usrprof.set_rag_fk = rqstupgrd.rqst_rag_fk
            usr.groups.add(grp)
            usr.save()
            usrprof.save()

            if settings.SENDEMAIL:
                email_upgradeacceptance(self)
        else:
            if settings.SENDEMAIL:
                email_upgraderejection(self)

        rqstupgrd.delete()

        return super(manageupgrade,self).form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(manageupgrade, self).dispatch(*args, **kwargs)

class usersettings(FormView):
    form_class = usersettingsform
    template_name="ceqanet/usersettings.html"

    def get_success_url(self):
        success_url = "%s" % (reverse_lazy('index'))
        return success_url

    def get_initial(self):
        initial = super(usersettings, self).get_initial()

        us_query = self.request.user.get_profile()
        if us_query.set_lag_fk:
            initial['set_lag_fk'] = us_query.set_lag_fk.lag_pk
        if us_query.set_rag_fk:
            initial['set_rag_fk'] = us_query.set_rag_fk.rag_pk
        return initial

    def get_context_data(self, **kwargs):
        context = super(usersettings, self).get_context_data(**kwargs)

        islead = False
        isplanner = False
        isclearinghouse = False

        for g in self.request.user.groups.all():
            if g.name == 'leads':
                islead = True
            if g.name == 'planners':
                isplanner = True
            if g.name == 'clearinghouse':
                isclearinghouse = True
        context['islead'] = islead
        context['isplanner'] = isplanner
        context['isclearinghouse'] = isclearinghouse

        return context

    def form_valid(self,form):
        data = form.cleaned_data

        set_lag_fk = data['set_lag_fk']
        if set_lag_fk == None:
            set_lag_fk = leadagencies.objects.get(pk=0)

        set_rag_fk = data['set_rag_fk']
        if set_rag_fk == None:
            set_rag_fk = reviewingagencies.objects.get(pk=0)

        us = self.request.user.get_profile()
        us.set_lag_fk = set_lag_fk
        us.set_rag_fk = set_rag_fk
        us.save()

        return super(usersettings,self).form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(usersettings, self).dispatch(*args, **kwargs)

def citiesforcounty_json(request, county):
    current_county = geowords.objects.get(geow_pk=county)
    cities = geowords.objects.all().filter(geow_parent_fk=current_county)
    json_cities = serializers.serialize("json", cities, fields=('geow_pk','geow_shortname'))
    return HttpResponse(json_cities, mimetype="application/javascript")
        
def locations_geojson(request,limit):
    locations_qs = Locations.objects.all()[:limit]
    #locations_qs = list(Locations.objects.values('pk','id','geom','document__doc_title')[:10])
    #djf = Django.Django(geodjango="geom", properties=['documents__doc_title'])
    djf = Django.Django(geodjango="geom")
    geoj = GeoJSON.GeoJSON()
    string = geoj.encode(djf.decode(locations_qs))
    #string = locations_qs
    return HttpResponse(string)

def doc_json(request,doc_id):
    ''' returns document metadata based on PK '''
    data = serializers.serialize('json', documents.objects.filter(pk=doc_id), fields=('doc_pk','doc_schno','doc_prj_fk','doc_docname','doc_received'),use_natural_keys=True)
    #data = serializers.serialize('json', documents.objects.filter(pk=doc_id))
    return HttpResponse(data)

def doc_location(request,doc_id):
    ''' returns the document location information from the API '''
    locations_qs = Locations.objects.filter(document=doc_id).centroid().geojson()
    #djf = Django.Django(geodjango="geom")
    #geoj = GeoJSON.GeoJSON()
    #string = geoj.encode(djf.decode(locations_qs))
    string1 = locations_qs[0].geojson
    #string = locations_qs[0].centroid
    #string1 = OGRGeometry(string).json
    return HttpResponse(string1)


def map(request):
    #form = basicqueryform()
    form = geocode()
    t = loader.get_template("ceqanet/map.html")
    c = RequestContext(request,{'form':form})
    return HttpResponse(t.render(c))
    
class locationEdit(UpdateView):
    model = Locations
    form_class = locationEditForm
    template_name="ceqanet/mapform.html"
    slug_field = "document"
    
    def get_queryset(self):
        slug = self.kwargs['slug']
        queryset = Locations.objects.filter(document=slug)
        return queryset

