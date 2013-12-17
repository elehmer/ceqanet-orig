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

from ceqanet.forms import QueryForm,basicqueryform,prjlistform,doclistform,advancedqueryform,submitform,usersettingsform,attachmentsform,chqueryform,findprojectform
from ceqanet.forms import nocform,nodform,noeform,nopform
from ceqanet.forms import editnocform,editnoeform,editnodform,editnopform
from ceqanet.forms import pendingdetailnocform,pendingdetailnodform,pendingdetailnoeform,pendingdetailnopform
from ceqanet.forms import reviewdetailnocform,reviewdetailnodform,reviewdetailnoeform,reviewdetailnopform
from ceqanet.forms import commentdetailform
from ceqanet.models import projects,documents,geowords,leadagencies,reviewingagencies,doctypes,dockeywords,docreviews,latlongs,counties,UserProfile,clearinghouse,keywords,docattachments
#split geo imports for simplicity
from ceqanet.models import Locations
from django.contrib.auth.models import User

from datetime import datetime
#vectorformats trick
from vectorformats.Formats import Django, GeoJSON, KML
#import simplejson
from django.utils import simplejson
from django.core import serializers

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
            success_url = "%s?doctype=%s" % (reverse_lazy('chquery'),doctype)
        elif prjtoggle == "no":
            success_url = "%s?doctype=%s&prj_pk=%s" % (reverse_lazy('docadd_'+doctype.lower()),doctype,None)
        return success_url

    def get_context_data(self, **kwargs):
        context = super(submit, self).get_context_data(**kwargs)

        context['laginfo'] = leadagencies.objects.get(pk=self.request.user.get_profile().set_lag_fk.lag_pk)
        context['drafts'] = documents.objects.filter(projects__prj_lag_fk__lag_pk=self.request.user.get_profile().set_lag_fk.lag_pk).filter(doc_draft=True)
        context['pending'] = documents.objects.filter(projects__prj_lag_fk__lag_pk=self.request.user.get_profile().set_lag_fk.lag_pk).filter(doc_pending=True)
        return context

class chquery(FormView):
    template_name="ceqanet/chquery.html"
    form_class = chqueryform

    def get_success_url(self):
        success_url = "%s?prj_schno=%s&doctype=%s" % (reverse_lazy('findproject'),self.prj_schno,self.doctype)
        return success_url

    def get_context_data(self, **kwargs):
        context = super(chquery, self).get_context_data(**kwargs)

        context['doctype'] = self.request.GET.get('doctype')

        return context

    def form_valid(self,form):
        data = form.cleaned_data
        self.prj_schno = data['prj_schno']
        self.doctype = self.request.POST.get('doctype')
        return super(chquery,self).form_valid(form)

class findproject(FormView):
    template_name="ceqanet/findproject.html"
    form_class = findprojectform

    def get_success_url(self):
        success_url = "%s?doctype=%s&prj_pk=%s" % (reverse_lazy('docadd_'+ self.doctype.lower()),self.doctype,self.prj_pk)
        return success_url

    def get_context_data(self, **kwargs):
        context = super(findproject, self).get_context_data(**kwargs)

        prj_schno = self.request.GET.get('prj_schno')
        context['schnos'] = projects.objects.filter(prj_visible=True).filter(prj_schno__startswith=prj_schno).order_by('-prj_schno')
        context['doctype'] = self.request.GET.get('doctype')

        return context

    def form_valid(self,form):
        self.prj_pk = self.request.POST.get('prj_pk')
        self.doctype = self.request.POST.get('doctype')
        return super(findproject,self).form_valid(form)

class attachments(FormView):
    template_name="ceqanet/attachments.html"
    form_class = attachmentsform    
    
    def get_success_url(self):
        if self.request.POST.get('mode') == 'attach':
            success_url = "%s?doc_pk=%s" % (reverse_lazy('attachments'),self.request.POST.get('doc_pk'))
        elif self.request.POST.get('mode') == 'delete':
            success_url = "%s" % reverse_lazy('submit')
        elif self.request.POST.get('mode') == 'remove':
            success_url = "%s?doc_pk=%s" % (reverse_lazy('attachments'),self.request.POST.get('doc_pk'))
        elif self.request.POST.get('mode') == 'draft':
            success_url = "%s" % reverse_lazy('submit')
        elif self.request.POST.get('mode') == 'submitch':
            success_url = "%s" % reverse_lazy('accept')
        return success_url

    def get_context_data(self, **kwargs):
        context = super(attachments , self).get_context_data(**kwargs)

        doc_pk = self.request.GET.get('doc_pk')
        context['doc_pk'] = doc_pk
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
            doc_prj_fk = doc.doc_prj_fk
            otherdocs = documents.objects.filter(doc_prj_fk=doc_prj_fk).exclude(pk=doc.doc_pk).order_by('-doc_received')
            if otherdocs.count() > 0:
                prj = projects.objects.get(pk=doc_prj_fk.prj_pk)
                prj.prj_doc_fk = otherdocs[0]
                prj.save()
            else:
                prj = projects.objects.get(pk=0)
                doc.doc_prj_fk = prj
                coords = latlongs.objects.get(doc_pk=doc.doc_pk)
                coords.doc_prj_fk = prj
                doc.save()
                coords.save()
                projects.objects.filter(pk=doc_prj_fk.prj_pk).delete()

            latlongs.objects.filter(doc_pk=doc.doc_pk).delete()
            dockeywords.objects.filter(dkey_doc_fk=doc.doc_pk).delete()
            docreviews.objects.filter(drag_doc_fk=doc.doc_pk).delete()
            
            docatts = docattachments.objects.filter(datt_doc_fk=doc.doc_pk)
            for att in docatts:
                os.remove(os.path.join(settings.MEDIA_ROOT, att.datt_file.name))
            docatts.delete()
            doc.delete()

        elif self.request.POST.get('mode') == 'submitch':
            doc.doc_draft = False
            doc.doc_pending = True
            doc.save()
    
            emaillist = doc.doc_conemail
            if doc.doc_conemail != self.request.user.email:
                emaillist += "," + self.request.user.email

            strFrom = "ceqanet@opr.ca.gov"
            ToList = [emaillist]
            strSubject = "Confirmation of Submittal - " + doc.doc_doctype
            strBody = "This confirms receipt of your electronic " + doc.doc_docname + " form submission on " + doc.doc_received.strftime('%m/%d/%Y') + ".  \n \n"
            strBody = strBody + "The State Clearinghouse will review your submittal and provide a State Clearinghouse Number and filing date within one business day. \n \n"
            strBody = strBody + "If you have questions about the form submittal process, please reply to this email.  Thank you for using CEQAnet. \n"
            strBody = strBody + "\n \n" + "--- Information Submitted ---" + "\n"
            strBody = strBody + "Document Type: " + doc.doc_doctype + "\n"        
            strBody = strBody + "Project Title: " + doc.doc_prj_fk.prj_title + "\n"
            strBody = strBody + "Project Location: " + doc.doc_location + "\n"
            strBody = strBody + "    City: " + doc.doc_city + "\n"
            strBody = strBody + "    County: " + doc.doc_county + "\n"
            #strBody = strBody + "    Latitude: " + data['doc_latitude'] + "\n"
            #strBody = strBody + "    Longitude: " + data['doc_longitude'] + "\n"
            strBody = strBody + "Project Description: " + doc.doc_prj_fk.prj_description + "\n"
            strBody = strBody + "Agency Approving Project: " + doc.doc_prj_fk.prj_leadagency + "\n"
            strBody = strBody + "Primary Contact:  " + "\n"
            strBody = strBody + "    Name: " + doc.doc_conname + "\n"
            strBody = strBody + "    Phone: " + doc.doc_conphone + "\n"
            strBody = strBody + "    E-mail: " + doc.doc_conemail + "\n"
            strBody = strBody + "DATE: " + doc.doc_received.strftime('%m/%d/%Y') + "\n"

            try:
                send_mail(strSubject,strBody,strFrom,ToList,fail_silently=False)
            except Exception as detail:
                print "Not Able to Send Email:", detail

        return super(attachments,self).form_valid(form)

class docadd_noc(FormView):
    template_name="ceqanet/docadd_noc.html"
    form_class = nocform

    def get_success_url(self):
        success_url = "%s?doc_pk=%s" % (reverse_lazy('attachments'),self.doc_pk)
        return success_url

    def get_initial(self):
        initial = super(docadd_noc, self).get_initial()

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

        if self.request.POST.get('prj_pk') == 'None':
            prj = projects(prj_lag_fk=lag,prj_doc_fk=doc,prj_status=data['doctypeid'].keyw_shortname,prj_title=data['prj_title'],prj_description=data['prj_description'],prj_leadagency=lag.lag_name,prj_datefirst=today,prj_datelast=today)
            prj.save()
        else:
            prj = projects.objects.get(pk=self.request.POST.get('prj_pk'))
            prj.prj_status = data['doctypeid'].keyw_shortname
            prj.prj_datelast = today

        adddoc = documents(doc_prj_fk=prj,doc_cnty_fk=cnty,doc_doct_fk=data['doctypeid'],doc_doctype=data['doctypeid'].keyw_shortname,doc_docname=data['doctypeid'].keyw_longname,doc_conname=data['doc_conname'],doc_conagency=lag.lag_name,doc_conemail=data['doc_conemail'],doc_conphone=data['doc_conphone'],doc_conaddress1=data['doc_conaddress1'],doc_conaddress2=doc_conaddress2,doc_concity=data['doc_concity'],doc_constate=data['doc_constate'],doc_conzip=data['doc_conzip'],doc_location=data['doc_location'],doc_city=doc_city,doc_county=doc_county,doc_draft=1,doc_pending=0,doc_received=doc_received,doc_added=today,doc_parcelno=doc_parcelno,doc_xstreets=doc_xstreets,doc_township=doc_township,doc_range=doc_range,doc_section=doc_section,doc_base=doc_base,doc_highways=doc_highways,doc_airports=doc_airports,doc_railways=doc_railways,doc_waterways=doc_waterways,doc_landuse=doc_landuse,doc_schools=doc_schools)
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

        self.doc_pk = adddoc.pk

        return super(docadd_noc,self).form_valid(form)

class docadd_nod(FormView):
    template_name="ceqanet/docadd_nod.html"
    form_class = nodform

    def get_success_url(self):
        success_url = "%s" % reverse_lazy('accept')
        return success_url

    def get_initial(self):
        initial = super(docadd_nod, self).get_initial()

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
        context = super(docadd_nod, self).get_context_data(**kwargs)

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
        cnty = counties.objects.get(pk=data['doc_county'].pk)
        doct = doctypes.objects.get(keyw_shortname__startswith=self.request.POST.get('doctype'))
        if data['doc_conaddress2'] == '':
            doc_conaddress2 = None
        else:
            doc_conaddress2 = data['doc_conaddress2']

        if self.request.POST.get('prj_pk') == 'None':
            prj = projects(prj_lag_fk=lag,prj_doc_fk=doc,prj_status=self.request.POST.get('doctype'),prj_title=data['prj_title'],prj_description=data['prj_description'],prj_leadagency=lag.lag_name,prj_datefirst=today,prj_datelast=today)
            prj.save()
        else:
            prj = projects.objects.get(pk=self.request.POST.get('prj_pk'))
            prj.prj_status = self.request.POST.get('doctype')
            prj.prj_datelast = today

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
        
        if data['leadorresp']:
            if data['leadorresp'] == 'lead':
                doc_nodbylead = True
                doc_nodbyresp = False
            elif data['leadorresp'] == 'resp':
                doc_nodbylead = False
                doc_nodbyresp = True

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

        adddoc = documents(doc_prj_fk=prj,doc_cnty_fk=cnty,doc_doct_fk=doct,doc_doctype=self.request.POST.get('doctype'),doc_docname=doct.keyw_longname,doc_conname=data['doc_conname'],doc_conagency=lag.lag_name,doc_conemail=data['doc_conemail'],doc_conphone=data['doc_conphone'],doc_conaddress1=data['doc_conaddress1'],doc_conaddress2=doc_conaddress2,doc_concity=data['doc_concity'],doc_constate=data['doc_constate'],doc_conzip=data['doc_conzip'],doc_location=data['doc_location'],doc_city=data['doc_city'].geow_shortname,doc_county=data['doc_county'].geow_shortname,doc_draft=0,doc_pending=1,doc_received=doc_received,doc_nodbylead=doc_nodbylead,doc_nodbyresp=doc_nodbyresp,doc_nodagency=data['doc_nodagency'].lag_name,doc_nod=data['doc_nod'],doc_detsigeffect=doc_detsigeffect,doc_detnotsigeffect=doc_detnotsigeffect,doc_deteir=doc_deteir,doc_detnegdec=doc_detnegdec,doc_detmitigation=doc_detmitigation,doc_detnotmitigation=doc_detnotmitigation,doc_detconsider=doc_detconsider,doc_detnotconsider=doc_detnotconsider,doc_detfindings=doc_detfindings,doc_detnotfindings=doc_detnotfindings,doc_eiravailableat=data['doc_eiravailableat'])
        adddoc.save()
        prj.prj_doc_fk=adddoc
        prj.save()

        coords = latlongs(doc_pk=adddoc.pk,doc_prj_fk=prj,doc_doctype=self.request.POST.get('doctype'),doc_latitude=data['doc_latitude'],doc_longitude=data['doc_longitude'])
        coords.save()

        self.doc_pk = adddoc.pk

        emaillist = adddoc.doc_conemail
        if adddoc.doc_conemail != self.request.user.email:
            emaillist += "," + self.request.user.email

        strFrom = "ceqanet@opr.ca.gov"
        ToList = [emaillist]
        strSubject = "Confirmation of Submittal - " + adddoc.doc_doctype
        strBody = "This confirms receipt of your electronic " + adddoc.doc_docname + " form submission on " + adddoc.doc_received.strftime('%m/%d/%Y') + ".  \n \n"
        strBody = strBody + "The State Clearinghouse will review your submittal and provide a State Clearinghouse Number and filing date within one business day. \n \n"
        strBody = strBody + "If you have questions about the form submittal process, please reply to this email.  Thank you for using CEQAnet. \n"
        strBody = strBody + "\n \n" + "--- Information Submitted ---" + "\n"
        strBody = strBody + "Document Type: " + adddoc.doc_doctype + "\n"        
        strBody = strBody + "Project Title: " + adddoc.doc_prj_fk.prj_title + "\n"
        strBody = strBody + "Project Location: " + adddoc.doc_location + "\n"
        strBody = strBody + "    City: " + adddoc.doc_city + "\n"
        strBody = strBody + "    County: " + adddoc.doc_county + "\n"
        strBody = strBody + "    Latitude: " + coords.doc_latitude + "\n"
        strBody = strBody + "    Longitude: " + coords.doc_longitude + "\n"
        strBody = strBody + "Project Description: " + adddoc.doc_prj_fk.prj_description + "\n"
        strBody = strBody + "Agency Approving Project: " + adddoc.doc_prj_fk.prj_leadagency + "\n"
        strBody = strBody + "Primary Contact:  " + "\n"
        strBody = strBody + "    Name: " + adddoc.doc_conname + "\n"
        strBody = strBody + "    Phone: " + adddoc.doc_conphone + "\n"
        strBody = strBody + "    E-mail: " + adddoc.doc_conemail + "\n"
        strBody = strBody + "DATE: " + adddoc.doc_received.strftime('%m/%d/%Y') + "\n"

        try:
            send_mail(strSubject,strBody,strFrom,ToList,fail_silently=False)
        except Exception as detail:
            print "Not Able to Send Email:", detail

        return super(docadd_nod,self).form_valid(form)

class docadd_noe(FormView):
    template_name="ceqanet/docadd_noe.html"
    form_class = noeform

    def get_success_url(self):
        success_url = "%s" % reverse_lazy('accept')
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

        if self.request.POST.get('prj_pk') == 'None':
            prj = projects(prj_lag_fk=lag,prj_doc_fk=doc,prj_status=self.request.POST.get('doctype'),prj_title=data['prj_title'],prj_description=data['prj_description'],prj_leadagency=lag.lag_name,prj_datefirst=today,prj_datelast=today)
            prj.save()
        else:
            prj = projects.objects.get(pk=self.request.POST.get('prj_pk'))
            prj.prj_status = self.request.POST.get('doctype')
            prj.prj_datelast = today

        adddoc = documents(doc_prj_fk=prj,doc_cnty_fk=cnty,doc_doct_fk=doct,doc_doctype=self.request.POST.get('doctype'),doc_docname=doct.keyw_longname,doc_conname=data['doc_conname'],doc_conagency=lag.lag_name,doc_conemail=data['doc_conemail'],doc_conphone=data['doc_conphone'],doc_conaddress1=data['doc_conaddress1'],doc_conaddress2=doc_conaddress2,doc_concity=data['doc_concity'],doc_constate=data['doc_constate'],doc_conzip=data['doc_conzip'],doc_location=data['doc_location'],doc_city=data['doc_city'].geow_shortname,doc_county=data['doc_county'].geow_shortname,doc_draft=0,doc_pending=1,doc_received=doc_received,doc_exministerial=doc_exministerial,doc_exdeclared=doc_exdeclared,doc_exemergency=doc_exemergency,doc_excategorical=doc_excategorical,doc_exstatutory=doc_exstatutory,doc_exnumber=doc_exnumber,doc_exreasons=data['doc_exreasons'])
        adddoc.save()
        prj.prj_doc_fk=adddoc
        prj.save()

        coords = latlongs(doc_pk=adddoc.pk,doc_prj_fk=prj,doc_doctype=self.request.POST.get('doctype'),doc_latitude=data['doc_latitude'],doc_longitude=data['doc_longitude'])
        coords.save()

        self.doc_pk = adddoc.pk

        emaillist = adddoc.doc_conemail
        if adddoc.doc_conemail != self.request.user.email:
            emaillist += "," + self.request.user.email

        strFrom = "ceqanet@opr.ca.gov"
        ToList = [emaillist]
        strSubject = "Confirmation of Submittal - " + adddoc.doc_doctype
        strBody = "This confirms receipt of your electronic " + adddoc.doc_docname + " form submission on " + adddoc.doc_received.strftime('%m/%d/%Y') + ".  \n \n"
        strBody = strBody + "The State Clearinghouse will review your submittal and provide a State Clearinghouse Number and filing date within one business day. \n \n"
        strBody = strBody + "If you have questions about the form submittal process, please reply to this email.  Thank you for using CEQAnet. \n"
        strBody = strBody + "\n \n" + "--- Information Submitted ---" + "\n"
        strBody = strBody + "Document Type: " + adddoc.doc_doctype + "\n"        
        strBody = strBody + "Project Title: " + adddoc.doc_prj_fk.prj_title + "\n"
        strBody = strBody + "Project Location: " + adddoc.doc_location + "\n"
        strBody = strBody + "    City: " + adddoc.doc_city + "\n"
        strBody = strBody + "    County: " + adddoc.doc_county + "\n"
        strBody = strBody + "    Latitude: " + coords.doc_latitude + "\n"
        strBody = strBody + "    Longitude: " + coords.doc_longitude + "\n"
        strBody = strBody + "Project Description: " + adddoc.doc_prj_fk.prj_description + "\n"
        strBody = strBody + "Agency Approving Project: " + adddoc.doc_prj_fk.prj_leadagency + "\n"
        strBody = strBody + "Primary Contact:  " + "\n"
        strBody = strBody + "    Name: " + adddoc.doc_conname + "\n"
        strBody = strBody + "    Phone: " + adddoc.doc_conphone + "\n"
        strBody = strBody + "    E-mail: " + adddoc.doc_conemail + "\n"
        strBody = strBody + "DATE: " + adddoc.doc_received.strftime('%m/%d/%Y') + "\n"

        try:
            send_mail(strSubject,strBody,strFrom,ToList,fail_silently=False)
        except Exception as detail:
            print "Not Able to Send Email:", detail

        return super(docadd_noe,self).form_valid(form)

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

        if self.request.POST.get('prj_pk') == 'None':
            prj = projects(prj_lag_fk=lag,prj_doc_fk=doc,prj_status=self.request.POST.get('doctype'),prj_title=data['prj_title'],prj_description=data['prj_description'],prj_leadagency=lag.lag_name,prj_datefirst=today,prj_datelast=today)
            prj.save()
        else:
            prj = projects.objects.get(pk=self.request.POST.get('prj_pk'))
            prj.prj_status = self.request.POST.get('doctype')
            prj.prj_datelast = today

        adddoc = documents(doc_prj_fk=prj,doc_cnty_fk=cnty,doc_doct_fk=doct,doc_doctype=doct.keyw_shortname,doc_docname=doct.keyw_longname,doc_conname=data['doc_conname'],doc_conagency=lag.lag_name,doc_conemail=data['doc_conemail'],doc_conphone=data['doc_conphone'],doc_conaddress1=data['doc_conaddress1'],doc_conaddress2=doc_conaddress2,doc_concity=data['doc_concity'],doc_constate=data['doc_constate'],doc_conzip=data['doc_conzip'],doc_location=data['doc_location'],doc_city=doc_city,doc_county=doc_county,doc_draft=1,doc_pending=0,doc_received=doc_received,doc_added=today,doc_parcelno=doc_parcelno,doc_xstreets=doc_xstreets,doc_township=doc_township,doc_range=doc_range,doc_section=doc_section,doc_base=doc_base,doc_highways=doc_highways,doc_airports=doc_airports,doc_railways=doc_railways,doc_waterways=doc_waterways,doc_landuse=doc_landuse,doc_schools=doc_schools)
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

        self.doc_pk = adddoc.pk

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
        context['attachments'] = docattachments.objects.filter(datt_doc_fk=self.request.GET.get('doc_pk'))

        return context

    def form_valid(self,form):
        data = form.cleaned_data
        doc = documents.objects.get(pk=self.request.POST.get('doc_pk'))
        prj = projects.objects.get(pk=doc.doc_prj_fk.prj_pk)

        if self.request.POST.get('mode') == 'assign':
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
        if self.request.POST.get('mode') == 'reject':
            doc_prj_fk = doc.doc_prj_fk
            otherdocs = documents.objects.filter(doc_prj_fk=doc_prj_fk).exclude(pk=doc.doc_pk).order_by('-doc_received')
            if otherdocs.count() > 0:
                prj = projects.objects.get(pk=doc_prj_fk.prj_pk)
                prj.prj_doc_fk = otherdocs[0]
                prj.save()
            else:
                prj = projects.objects.get(pk=0)
                doc.doc_prj_fk = prj
                coords = latlongs.objects.get(doc_pk=doc.doc_pk)
                coords.doc_prj_fk = prj
                doc.save()
                coords.save()
                projects.objects.filter(pk=doc_prj_fk.prj_pk).delete()

            latlongs.objects.filter(doc_pk=doc.doc_pk).delete()
            dockeywords.objects.filter(dkey_doc_fk=doc.doc_pk).delete()
            docreviews.objects.filter(drag_doc_fk=doc.doc_pk).delete()
            
            docatts = docattachments.objects.filter(datt_doc_fk=doc.doc_pk)
            for att in docatts:
                os.remove(os.path.join(settings.MEDIA_ROOT, att.datt_file.name))
            docatts.delete()
            doc.delete()

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

def account(request):
    t = loader.get_template("ceqanet/account.html")
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
        initial['confirstname'] = self.request.user.first_name
        initial['conlastname'] = self.request.user.last_name
        initial['conemail'] = self.request.user.email
        initial['conphone'] = us_query.conphone
        return initial

    def get_context_data(self, **kwargs):
        context = super(usersettings, self).get_context_data(**kwargs)

        islead = False
        isplanner = False
        isreview = False
        isclearinghouse = False

        for g in self.request.user.groups.all():
            if g.name == 'leads':
                islead = True
            if g.name == 'planners':
                isplanner = True
            if g.name == 'reviewers':
                isreview = True
            if g.name == 'clearinghouse':
                isclearinghouse = True
        context['islead'] = islead
        context['isplanner'] = isplanner
        context['isreview'] = isreview
        context['isclearinghouse'] = isclearinghouse

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
        us.region = region
        us.set_lag_fk = set_lag_fk
        us.set_rag_fk = set_rag_fk
        us.conphone = conphone
        us.save()

        return super(usersettings,self).form_valid(form)
        
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
    data = serializers.serialize('json', documents.objects.filter(pk=doc_id), fields=('doc_pk','doc_schno','doc_prj_fk','doc_docname','doc_received'),use_natural_keys=True)
    #data = serializers.serialize('json', documents.objects.filter(pk=doc_id))
    return HttpResponse(data)

def doc_location(request,doc_id):
    locations_qs = Locations.objects.filter(document=doc_id)
    djf = Django.Django(geodjango="geom")
    geoj = GeoJSON.GeoJSON()
    string = geoj.encode(djf.decode(locations_qs))
    return HttpResponse(string)


def map(request):
    t = loader.get_template("ceqanet/map.html")
    c = RequestContext(request,{})
    return HttpResponse(t.render(c))
