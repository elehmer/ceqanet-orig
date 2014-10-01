import os
from django.core.urlresolvers import reverse
from ceqanet.models import documents,projects,latlongs,dockeywords,docgeowords,docreviews,docattachments,clearinghouse,Locations,doccomments,requestupgrade
from django.contrib.auth.models import User,Group
from django.core.mail import send_mail,EmailMultiAlternatives
from datetime import datetime
from django.templatetags.static import static

opr_email_address = "opr@ceqa.ice.ucdavis.edu"
opr_email_recipients = "opr@ceqa.ice.ucdavis.edu,Christine.Asiata@OPR.CA.GOV,elehmer@ucdavis.edu"

def generate_schno(region):
    ch = clearinghouse.objects.get(pk=1)

    prefix = ch.schnoprefix
    yearmonthnow = datetime.now().strftime("%Y%m")
    if yearmonthnow != prefix:
        ch.schnoprefix = yearmonthnow
        ch.currentid = 1
        ch.save()

    currentidnum = str(ch.currentid)
    if len(currentidnum) == 1:
        currentidnum = "00"+currentidnum
    elif len(currentidnum) == 2:
        currentidnum = "0"+currentidnum
    schno = ch.schnoprefix + str(region) + currentidnum
    ch.currentid = ch.currentid+1
    ch.save()
    return schno

def generate_biaschno():
    ch = clearinghouse.objects.get(pk=1)

    biayear = ch.biayear
    yearnow = datetime.now().strftime("%Y")
    if yearnow != biayear:
        ch.biayear = yearnow
        ch.biaid = 1
        ch.save()

    schno = ch.biayear + "-" + str(ch.biaid)
    ch.biaid = ch.biaid+1
    ch.save()
    return schno

def delete_clearinghouse_document(self):
    doc = documents.objects.get(pk=self.request.POST.get('doc_pk'))
    doc_prj_fk = doc.doc_prj_fk
    otherdocs = documents.objects.filter(doc_prj_fk=doc_prj_fk).exclude(pk=doc.doc_pk).order_by('-doc_received')
    if otherdocs.count() > 0:
        prj = projects.objects.get(pk=doc_prj_fk.prj_pk)
        prj.prj_doc_fk = otherdocs[0]
        prj.save()
    else:
        prj = projects.objects.get(pk=0)
        doc.doc_prj_fk = prj
        doc.save()
        try:
            coords = latlongs.objects.get(doc_pk=doc.doc_pk)
        except latlongs.DoesNotExist:
            coords = None
        if coords:
            coords.doc_prj_fk = prj
            coords.save()
        projects.objects.filter(pk=doc_prj_fk.prj_pk).delete()

    latlongs.objects.filter(doc_pk=doc.doc_pk).delete()
    Locations.objects.filter(document=doc.doc_pk).delete()
    docgeowords.objects.filter(dgeo_doc_fk=doc.doc_pk).delete()
    dockeywords.objects.filter(dkey_doc_fk=doc.doc_pk).delete()
    doccomments.objects.filter(dcom_doc_fk=doc.doc_pk).delete()
    docreviews.objects.filter(drag_doc_fk=doc.doc_pk).delete()

    docatts = docattachments.objects.filter(datt_doc_fk=doc.doc_pk)
    for att in docatts:
        os.remove(os.path.join(settings.MEDIA_ROOT, att.datt_file.name))
    docatts.delete()
    doc.delete()

def email_acceptance(self):
    doc = documents.objects.get(pk=self.request.POST.get('doc_pk'))

    if doc.doc_doct_fk.keyw_pk == 109:
        docurl = reverse('docdesp_noe', args=[self.request.POST.get('doc_pk')])
    elif doc.doc_doct_fk.keyw_pk == 108:
        docurl = reverse('docdesp_nod', args=[self.request.POST.get('doc_pk')])
    elif doc.doc_doct_fk.keyw_pk == 102:
        docurl = reverse('docdesp_nop', args=[self.request.POST.get('doc_pk')])
    else:
        docurl = reverse('docdesp_noc', args=[self.request.POST.get('doc_pk')])

    emaillist = doc.doc_conemail
    if doc.doc_conemail != doc.doc_added_userid.email:
        emaillist += "," + doc.doc_added_userid.email

    strFrom = opr_email_address
    ToList = [emaillist]
    strSubject = "CEQANet: Acceptance of Submittal - " + doc.doc_doctype
    strBody = "Dear CEQANet User,\n"
    strBody += "Thank you for submitting a CEQA document on the State Clearinghouse CEQANet System.\n" 
    strBody += "The following document has been accepted and posted by the State Clearinghouse:\n"
    strBody += "Project Title: " + doc.doc_prj_fk.prj_title + "\n"
    strBody += "Lead Agency: " + doc.doc_prj_fk.prj_leadagency + "\n"
    strBody += "Type of CEQA Document: " + doc.doc_doctype + "\n"
    strBody += "State Clearinghouse Number (SCH#), if existing: "
    if doc.doc_schno != None:
        strBody += doc.doc_schno + "\n"
    else:
        strBody += "Not Assigned Yet\n"
    strBody += "Posted: " + doc.doc_received.strftime('%m/%d/%Y') + "\n"
    strBody += "If you have any questions or need to correct your submittal, feel free to call the State Clearinghouse at (916)445-0613.\n"
    strBody += "Thank you.\n"

    html_content = "<!DOCTYPE html>"
    html_content += "<html class=\"no-js\" lang=\"en\"><HEAD><meta charset=\"utf-8\"><title>OPR CEQANet Email Communication</title>"
    html_content += "<link rel=\"stylesheet\" href=\"http://" + self.request.get_host() + static("ceqanet/CA_template/css/style.css") + "\">"
    html_content += "<link rel=\"stylesheet\" href=\"http://" + self.request.get_host() + static("ceqanet/CA_template/css/colorscheme_oceanside.css") + "\">"
    html_content += "</HEAD><body class=\"clearfix\">"
    html_content += "<div id=\"main_content\" class=\"clearfix\">"
    html_content += "<div class=\"add_maincontent_padding\">"
    html_content += "<h1 class=\"add_icon_blue_arrow_right\">OPR CEQANet Communication: Acceptance of Submittal</h1>"
    html_content += "<P>Dear CEQANet User,<BR>"
    html_content += "Thank you for submitting a CEQA document on the State Clearinghouse CEQANet System. The following document has been accepted and posted by the State Clearinghouse:</P>"
    html_content += "<ul><li>Project Title: <a href=\"http://" + self.request.get_host() + docurl + "\">" + doc.doc_prj_fk.prj_title + "</a>"
    html_content += "<li>Lead Agency: " + doc.doc_prj_fk.prj_leadagency
    html_content += "<li>Type of CEQA Document: " + doc.doc_doctype
    html_content += "<li>State Clearinghouse Number (SCH#), if existing: "
    if doc.doc_schno != None:
        html_content += doc.doc_schno
    else:
        html_content += "Not Assigned Yet"
    html_content += "<li>Posted: " + doc.doc_received.strftime('%m/%d/%Y') + "</ul>"
    html_content += "<p>If you have any questions or need to correct your submittal, feel free to call the State Clearinghouse at (916) 445-0613.</p>"
    html_content += "Thank you."
    html_content += "</div></div>"
    html_content += "</BODY></HTML>"

    msg = EmailMultiAlternatives(strSubject, strBody, strFrom, ToList)
    msg.attach_alternative(html_content, "text/html")
    msg.send()

def email_rejection(self):
    doc = documents.objects.get(pk=self.request.POST.get('doc_pk'))

    emaillist = doc.doc_conemail
    if doc.doc_conemail != doc.doc_added_userid.email:
        emaillist += "," + doc.doc_added_userid.email

    strFrom = opr_email_address
    ToList = [emaillist]
    strSubject = "CEQANet: Rejection of Submittal - " + doc.doc_doctype
    strBody = "Dear CEQANet User,\n"
    strBody += "Thank you for submitting a CEQA document on the State Clearinghouse CEQANet System.\n" 
    strBody += "The following document has been rejected by the State Clearinghouse:\n"
    strBody += "Project Title: " + doc.doc_prj_fk.prj_title + "\n"
    strBody += "Lead Agency: " + doc.doc_prj_fk.prj_leadagency + "\n"
    strBody += "Type of CEQA Document: " + doc.doc_doctype + "\n"
    strBody += "The document has been deleted and will need to be resubmitted.\n"
    strBody += "Please contact the State Clearinghouse at (916)445-0613 to discuss your document submittal.\n"
    strBody += "Thank you.\n"

    html_content = "<!DOCTYPE html>"
    html_content += "<html class=\"no-js\" lang=\"en\"><HEAD><meta charset=\"utf-8\"><title>OPR CEQANet Email Communication</title>"
    html_content += "<link rel=\"stylesheet\" href=\"http://" + self.request.get_host() + static("ceqanet/CA_template/css/style.css") + "\">"
    html_content += "<link rel=\"stylesheet\" href=\"http://" + self.request.get_host() + static("ceqanet/CA_template/css/colorscheme_oceanside.css") + "\">"
    html_content += "</HEAD><body class=\"clearfix\">"
    html_content += "<div id=\"main_content\" class=\"clearfix\">"
    html_content += "<div class=\"add_maincontent_padding\">"
    html_content += "<h1 class=\"add_icon_blue_arrow_right\">OPR CEQANet Communication: Rejection of Submittal</h1>"
    html_content += "<P>Dear CEQANet User,<BR>"
    html_content += "Thank you for submitting a CEQA document on the State Clearinghouse CEQANet System. The following document has been rejected by the State Clearinghouse:</P>"
    html_content += "<ul><li>Project Title: " + doc.doc_prj_fk.prj_title 
    html_content += "<li>Lead Agency: " + doc.doc_prj_fk.prj_leadagency
    html_content += "<li>Type of CEQA Document: " + doc.doc_doctype
    html_content += "<p>The document has been deleted and will need to be resubmitted.</p>"
    html_content += "<p>Please contact the State Clearinghouse at (916)445-0613 to discuss your document submittal.</p>"
    html_content += "Thank you."
    html_content += "</div></div>"
    html_content += "</BODY></HTML>"

    msg = EmailMultiAlternatives(strSubject, strBody, strFrom, ToList)
    msg.attach_alternative(html_content, "text/html")
    msg.send()

def email_demotiontodraft(self,doc):
    if doc.doc_doct_fk.keyw_pk == 109:
        docurl = "%s?doc_pk=%s" % (reverse('draftedit_noe'),doc.doc_pk)
    elif doc.doc_doct_fk.keyw_pk == 108:
        docurl = "%s?doc_pk=%s" % (reverse('draftedit_nod'),doc.doc_pk)
    elif doc.doc_doct_fk.keyw_pk == 102:
        docurl = "%s?doc_pk=%s" % (reverse('draftedit_nop'),doc.doc_pk)
    else:
        docurl = "%s?doc_pk=%s" % (reverse('draftedit_noc'),doc.doc_pk)

    emaillist = doc.doc_conemail
    if doc.doc_conemail != doc.doc_added_userid.email:
        emaillist += "," + doc.doc_added_userid.email

    strFrom = opr_email_address
    ToList = [emaillist]
    strSubject = "CEQANet: Rejection of Submittal - " + doc.doc_doctype
    strBody = "Dear CEQANet User,\n"
    strBody += "Thank you for submitting a CEQA document on the State Clearinghouse CEQANet System.\n" 
    strBody += "The following document has been rejected by the State Clearinghouse:\n"
    strBody += "Project Title: " + doc.doc_prj_fk.prj_title + "\n"
    strBody += "Lead Agency: " + doc.doc_prj_fk.prj_leadagency + "\n"
    strBody += "Type of CEQA Document: " + doc.doc_doctype + "\n"
    strBody += "The document has been returned to the Draft Documents list on your account and will need to be corrected before being submitted again.\n"
    strBody += "Please contact the State Clearinghouse at (916)445-0613 to discuss your document submittal.\n"
    strBody += "Thank you.\n"

    html_content = "<!DOCTYPE html>"
    html_content += "<html class=\"no-js\" lang=\"en\"><HEAD><meta charset=\"utf-8\"><title>OPR CEQANet Email Communication</title>"
    html_content += "<link rel=\"stylesheet\" href=\"http://" + self.request.get_host() + static("ceqanet/CA_template/css/style.css") + "\">"
    html_content += "<link rel=\"stylesheet\" href=\"http://" + self.request.get_host() + static("ceqanet/CA_template/css/colorscheme_oceanside.css") + "\">"
    html_content += "</HEAD><body class=\"clearfix\">"
    html_content += "<div id=\"main_content\" class=\"clearfix\">"
    html_content += "<div class=\"add_maincontent_padding\">"
    html_content += "<h1 class=\"add_icon_blue_arrow_right\">OPR CEQANet Communication: Rejection of Submittal</h1>"
    html_content += "<P>Dear CEQANet User,<BR>"
    html_content += "Thank you for submitting a CEQA document on the State Clearinghouse CEQANet System. The following document has been rejected by the State Clearinghouse:</P>"
    html_content += "<ul><li>Project Title: <a href=\"http://" + self.request.get_host() + docurl + "\">" + doc.doc_prj_fk.prj_title + "</a>"
    html_content += "<li>Lead Agency: " + doc.doc_prj_fk.prj_leadagency
    html_content += "<li>Type of CEQA Document: " + doc.doc_doctype
    html_content += "<p>The document has been returned to the Draft Documents list on your account and will need to be corrected before being submitted again.</p>"
    html_content += "<p>Please contact the State Clearinghouse at (916)445-0613 to discuss your document submittal.</p>"
    html_content += "Thank you."
    html_content += "Link: <a href=\"" + self.request.get_host() + docurl + "\">" + self.request.get_host() + docurl + "</a>"
    html_content += "</div></div>"
    html_content += "</BODY></HTML>"

    msg = EmailMultiAlternatives(strSubject, strBody, strFrom, ToList)
    msg.attach_alternative(html_content, "text/html")
    msg.send()

def email_submission(self,doc):
    if doc.doc_doct_fk.keyw_pk == 109:
        docurl = reverse('docdesp_noe', args=[doc.doc_pk])
    elif doc.doc_doct_fk.keyw_pk == 108:
        docurl = reverse('docdesp_nod', args=[doc.doc_pk])
    elif doc.doc_doct_fk.keyw_pk == 102:
        docurl = reverse('docdesp_nop', args=[doc.doc_pk])
    else:
        docurl = reverse('docdesp_noc', args=[doc.doc_pk])

    emaillist = doc.doc_conemail
    if doc.doc_conemail != doc.doc_added_userid.email:
        emaillist += "," + doc.doc_added_userid.email
        emaillist += "," + opr_email_address

    strFrom = opr_email_address
    ToList = [emaillist]
    strSubject = "Confirmation of Submittal - " + doc.doc_doctype
    strBody = "Dear CEQANet User,\n"
    strBody += "Thank you for submitting a CEQA document on the State Clearinghouse CEQANet System. Please review the following information to ensure it is correct:\n"
    strBody += "Project Title: " + doc.doc_prj_fk.prj_title + "\n"
    strBody += "Lead Agency: " + doc.doc_prj_fk.prj_leadagency + "\n"
    strBody += "Type of CEQA Document: " + doc.doc_doctype + "\n"
    strBody += "State Clearinghouse Number (SCH#), if existing: "
    if doc.doc_schno != None:
        strBody += doc.doc_schno + "\n"
    else:
        strBody += "Not Assigned Yet\n"
    strBody += "Lead Agency Contact Name: " + doc.doc_conname + "\n"
    strBody += "Lead Agency Contact Phone Number: " + doc.doc_conphone + "\n"
    strBody += "State Clearinghouse staff will review your submittal for completeness. If necessary, the State Clearinghouse staff will also assign the project a State Clearinghouse number, determine which state agencies will receive the document for review, and set the review period dates for your document.  Once these steps are complete, you will receive another confirmation email.\n"
    strBody += "If you have any questions or need to correct your submittal, feel free to call the State Clearinghouse at (916) 445-0613.\n"
    strBody += "Thank you."

    html_content = "<!DOCTYPE html>"
    html_content += "<html class=\"no-js\" lang=\"en\"><HEAD><meta charset=\"utf-8\"><title>OPR CEQANet Email Communication</title>"
    html_content += "<link rel=\"stylesheet\" href=\"http://" + self.request.get_host() + static("ceqanet/CA_template/css/style.css") + "\">"
    html_content += "<link rel=\"stylesheet\" href=\"http://" + self.request.get_host() + static("ceqanet/CA_template/css/colorscheme_oceanside.css") + "\">"
    html_content += "</HEAD><body class=\"clearfix\">"
    html_content += "<div id=\"main_content\" class=\"clearfix\">"
    html_content += "<div class=\"add_maincontent_padding\">"
    html_content += "<h1 class=\"add_icon_blue_arrow_right\">OPR CEQANet Communication: Comfirmation of Submittal</h1>"
    html_content += "<P>Dear CEQANet User,<BR>"
    html_content += "Thank you for submitting a CEQA document on the State Clearinghouse CEQANet System. Please review the following information to ensure it is correct:</P>"
    html_content += "<ul><li>Project Title: <a href=\"http://" + self.request.get_host() + docurl + "\">" + doc.doc_prj_fk.prj_title + "</a>"
    html_content += "<li>Lead Agency: " + doc.doc_prj_fk.prj_leadagency
    html_content += "<li>Type of CEQA Document: " + doc.doc_doctype
    html_content += "<li>State Clearinghouse Number (SCH#), if existing: "
    if doc.doc_schno != None:
        html_content += doc.doc_schno
    else:
        html_content += "Not Assigned Yet"
    html_content += "<li>Lead Agency Contact Name: " + doc.doc_conname
    html_content += "<li>Lead Agency Contact Phone Number: " + doc.doc_conphone
    html_content += "</ul><p>State Clearinghouse staff will review your submittal for completeness. If necessary, the State Clearinghouse staff will also assign the project a State Clearinghouse number, determine which state agencies will receive the document for review, and set the review period dates for your document.  Once these steps are complete, you will receive another confirmation email.</p>"
    html_content += "<p>If you have any questions or need to correct your submittal, feel free to call the State Clearinghouse at (916) 445-0613.</p>"
    html_content += "Thank you."
    html_content += "</div></div>"
    html_content += "</BODY></HTML>"

    msg = EmailMultiAlternatives(strSubject, strBody, strFrom, ToList)
    msg.attach_alternative(html_content, "text/html")
    msg.send()

    #try:
    #    send_mail(strSubject,strBody,strFrom,ToList,fail_silently=False,html_message=strBody)
    #except Exception as detail:
    #    print "Not Able to Send Email:", detail

def email_assigned(self,doc):
    emaillist = opr_email_address

    grp = Group.objects.get(name='planners')
    usrs =grp.user_set.all()
    for u in usrs:
        emaillist += "," + u.email

    strFrom = opr_email_address
    ToList = [emaillist]
    strSubject = "Document Assigned to Planners - " + doc.doc_doctype
    strBody = "The document of type: " + doc.doc_docname + " form submission on " + doc.doc_received.strftime('%m/%d/%Y') + " has been assigned to planners for review.  \n \n"
    strBody += "\n \n" + "--- Information Submitted ---" + "\n"
    strBody += "Document Type: " + doc.doc_doctype + "\ndoc.doc_pk"        
    strBody += "Project Title: " + doc.doc_prj_fk.prj_title + "\n"
    strBody += "Project Location: " + doc.doc_location + "\n"
    strBody += "    City: " + doc.doc_city + "\n"
    strBody += "    County: " + doc.doc_county + "\n"
    strBody += "Project Description: " + doc.doc_prj_fk.prj_description + "\n"
    strBody += "Primary Contact:  " + "\n"
    strBody += "    Name: " + doc.doc_conname + "\n"
    strBody += "    Phone: " + doc.doc_conphone + "\n"
    strBody += "    E-mail: " + doc.doc_conemail + "\n"
    strBody += "DATE: " + doc.doc_received.strftime('%m/%d/%Y') + "\n"

    try:
        send_mail(strSubject,strBody,strFrom,ToList,fail_silently=False)
    except Exception as detail:
        print "Not Able to Send Email:", detail

def email_inreview(self,doc):
    if doc.doc_doct_fk.keyw_pk == 109:
        docurl = reverse('docdesp_noe', args=[self.request.POST.get('doc_pk')])
    elif doc.doc_doct_fk.keyw_pk == 108:
        docurl = reverse('docdesp_nod', args=[self.request.POST.get('doc_pk')])
    elif doc.doc_doct_fk.keyw_pk == 102:
        docurl = reverse('docdesp_nop', args=[self.request.POST.get('doc_pk')])
    else:
        docurl = reverse('docdesp_noc', args=[self.request.POST.get('doc_pk')])

    emaillist = doc.doc_conemail
    if doc.doc_conemail != doc.doc_added_userid.email:
        emaillist += "," + doc.doc_added_userid.email

    grp = Group.objects.get(name='reviewers')
    usrs =grp.user_set.all()
    for u in usrs:
        for ra in self.request.POST.get('ragencies'):
            if u.get_profile().set_rag_fk == ra:
                emaillist += "," + u.email

    reviewers = docreviews.objects.filter(drag_doc_fk=doc.pk)

    strFrom = opr_email_address
    ToList = [emaillist]
    strSubject = "CEQANet: Beginning of Review Period - " + doc.doc_doctype
    strBody = "The " + doc.doc_docname + " document submitted to the State Clearinghouse on " + doc.doc_received.strftime('%m/%d/%Y') + " has entered a review period:  \n \n"
    strBody += "Review Start Date: " +  doc.doc_dept.strftime('%m/%d/%Y') + "\n"
    strBody += "Review End Date: " +  doc.doc_clear.strftime('%m/%d/%Y') + "\n"
    strBody += "\n \n" + "Please reply to this email if you have any questions regarding this document."
    strBody += "\n \n" + "--- Information Submitted ---" + "\n"
    strBody += "Document Type: " + doc.doc_doctype + "\n"        
    strBody += "Project Title: " + doc.doc_prj_fk.prj_title + "\n"
    strBody += "Project Location: " + doc.doc_location + "\n"
    strBody += "    City: " + doc.doc_city + "\n"
    strBody += "    County: " + doc.doc_county + "\n"
    strBody += "Project Description: " + doc.doc_prj_fk.prj_description + "\n"
    strBody += "Primary Contact:  " + "\n"
    strBody += "    Name: " + doc.doc_conname + "\n"
    strBody += "    Phone: " + doc.doc_conphone + "\n"
    strBody += "    E-mail: " + doc.doc_conemail + "\n"
    strBody += "Date Recieved: " + doc.doc_received.strftime('%m/%d/%Y') + "\n"

    html_content = "<!DOCTYPE html>"
    html_content += "<html class=\"no-js\" lang=\"en\"><HEAD><meta charset=\"utf-8\"><title>OPR CEQANet Email Communication</title>"
    html_content += "<link rel=\"stylesheet\" href=\"http://" + self.request.get_host() + static("ceqanet/CA_template/css/style.css") + "\">"
    html_content += "<link rel=\"stylesheet\" href=\"http://" + self.request.get_host() + static("ceqanet/CA_template/css/colorscheme_oceanside.css") + "\">"
    html_content += "</HEAD><body class=\"clearfix\">"
    html_content += "<div id=\"main_content\" class=\"clearfix\">"
    html_content += "<div class=\"add_maincontent_padding\">"
    html_content += "<h1 class=\"add_icon_blue_arrow_right\">OPR CEQANet Communication: Acceptance of Submittal</h1>"
    html_content += "<P>Dear CEQANet User,<BR>"
    html_content += "Thank you for submitting a CEQA document on the State Clearinghouse CEQANet System. The following document has been accepted and posted by the State Clearinghouse:</P>"
    html_content += "<ul><li>Project Title: <a href=\"http://" + self.request.get_host() + docurl + "\">" + doc.doc_prj_fk.prj_title + "</a>"
    html_content += "<li>Lead Agency: " + doc.doc_prj_fk.prj_leadagency
    html_content += "<li>Type of CEQA Document: " + doc.doc_doctype
    html_content += "<li>State Clearinghouse Number (SCH#), if existing: "
    if doc.doc_schno != None:
        html_content += doc.doc_schno
    else:
        html_content += "Not Assigned Yet"
    html_content += "<li>Posted: " + doc.doc_received.strftime('%m/%d/%Y') + "</ul>"
    html_content += "<p>The State Review period for your document will begin on " + doc.doc_dept.strftime('%m/%d/%Y') + " and conclude on " + doc.doc_clear.strftime('%m/%d/%Y') + ".</P>"
    html_content += "<P>The following state agencies have received your document for review:</P>"
    html_content += "<UL>"
    html_content += "</UL>"
    html_content += "<p>If you have any questions or need to correct your submittal, feel free to call the State Clearinghouse at (916) 445-0613.</p>"
    html_content += "Thank you."
    html_content += "</div></div>"
    html_content += "</BODY></HTML>"

    msg = EmailMultiAlternatives(strSubject, strBody, strFrom, ToList)
    msg.attach_alternative(html_content, "text/html")
    msg.send()

def email_requestforupgrade(self,data):
    strFrom = opr_email_address
    ToList = [opr_email_recipients]
    strSubject = "CEQANet: Upgrade Request"
    strBody = "There is a new request for account upgrade. Please check website." + "\n"

    docurl = "%s?user_id=%s" % (reverse('manageupgrade'),self.request.user.pk)

    html_content = "<!DOCTYPE html>"
    html_content += "<html class=\"no-js\" lang=\"en\"><HEAD><meta charset=\"utf-8\"><title>OPR CEQANet Email Communication</title>"
    html_content += "<link rel=\"stylesheet\" href=\"http://" + self.request.get_host() + static("ceqanet/CA_template/css/style.css") + "\">"
    html_content += "<link rel=\"stylesheet\" href=\"http://" + self.request.get_host() + static("ceqanet/CA_template/css/colorscheme_oceanside.css") + "\">"
    html_content += "</HEAD><body class=\"clearfix\">"
    html_content += "<div id=\"main_content\" class=\"clearfix\">"
    html_content += "<div class=\"add_maincontent_padding\">"
    html_content += "<h1 class=\"add_icon_blue_arrow_right\">OPR CEQANet Communication: Request for Account Upgrade</h1>"
    html_content += "<P>The following registered CEQANet System User has requested an upgraded status:</P>"
    html_content += "<ul><li>User Name: " + self.request.user.username
    html_content += "<li>Request Type: " + self.request.POST.get('rqst_type')
    if self.request.POST.get('rqst_type') == 'lead':
        html_content += "<li>Lead Agency: " + data['rqst_lag_fk'].lag_name
    else:
        html_content += "<li>Reviewing Agency: " + data['rqst_rag_fk'].rag_name
    html_content += "<li>Email: " + self.request.user.email
    if self.request.user.get_profile().conphone != None:
        html_content += "<li>Phone Number: " + self.request.user.get_profile().conphone
    html_content += "</ul>"
    html_content += "<a href=\"http://" + self.request.get_host() + docurl + "\">Click here to review the request.</a>"
    html_content += "</div></div>"
    html_content += "</BODY></HTML>"

    msg = EmailMultiAlternatives(strSubject, strBody, strFrom, ToList)
    msg.attach_alternative(html_content, "text/html")
    msg.send()

def email_upgradeacceptance(self):
    emaillist = User.objects.get(pk=self.request.POST.get('user_id')).email

    rqstupgrd = requestupgrade.objects.get(user_id=self.request.POST.get('user_id'))
    
    strFrom = opr_email_address
    ToList = [emaillist]
    strSubject = "CEQANet: Acceptance of Account Upgrade Request"
    strBody = "Your request to have your CEQANet account upgraded has been accepted."
    strBody += "\n \n" + "Please reply to this email if you have any questions regarding this rejection."

    html_content = "<!DOCTYPE html>"
    html_content += "<html class=\"no-js\" lang=\"en\"><HEAD><meta charset=\"utf-8\"><title>OPR CEQANet Email Communication</title>"
    html_content += "<link rel=\"stylesheet\" href=\"http://" + self.request.get_host() + static("ceqanet/CA_template/css/style.css") + "\">"
    html_content += "<link rel=\"stylesheet\" href=\"http://" + self.request.get_host() + static("ceqanet/CA_template/css/colorscheme_oceanside.css") + "\">"
    html_content += "</HEAD><body class=\"clearfix\">"
    html_content += "<div id=\"main_content\" class=\"clearfix\">"
    html_content += "<div class=\"add_maincontent_padding\">"
    html_content += "<h1 class=\"add_icon_blue_arrow_right\">OPR CEQANet Communication: Acceptance of Upgrade Request</h1>"
    html_content += "<P>Thank you for requesting an upgrade to your status on the State Clearinghouse CEQANet System.  Your request has been approved.</P>"
    if rqstupgrd.rqst_type == 'lead':
        html_content += "<P>You may now submit CEQA documents on the CEQANet System for review.</P>"
    else:
        html_content += "<P>You will now receive email notification for documents sent by the State Clearinghouse for your state agency's review.  You may also submit comment letters on these documents.</P>"
    html_content += "<a href=\"http://" + self.request.get_host() + "\">Click here to go to CEQANet</a>"
    html_content += "<p>If you have any questions, feel free to call the State Clearinghouse at (916) 445-0613.</p>"
    html_content += "Thank you."
    html_content += "</div></div>"
    html_content += "</BODY></HTML>"

    msg = EmailMultiAlternatives(strSubject, strBody, strFrom, ToList)
    msg.attach_alternative(html_content, "text/html")
    msg.send()

def email_upgraderejection(self):
    emaillist = User.objects.get(pk=self.request.POST.get('user_id')).email
    
    strFrom = opr_email_address
    ToList = [emaillist]
    strSubject = "CEQANet: Rejection of Account Upgrade Request"
    strBody = "Your request to have your CEQANet account upgraded has been rejected. Reason for rejection follows:" + "\n"
    strBody += self.request.POST.get('rejectreason')
    strBody += "\n \n" + "Please reply to this email if you have any questions regarding this rejection."

    html_content = "<!DOCTYPE html>"
    html_content += "<html class=\"no-js\" lang=\"en\"><HEAD><meta charset=\"utf-8\"><title>OPR CEQANet Email Communication</title>"
    html_content += "<link rel=\"stylesheet\" href=\"http://" + self.request.get_host() + static("ceqanet/CA_template/css/style.css") + "\">"
    html_content += "<link rel=\"stylesheet\" href=\"http://" + self.request.get_host() + static("ceqanet/CA_template/css/colorscheme_oceanside.css") + "\">"
    html_content += "</HEAD><body class=\"clearfix\">"
    html_content += "<div id=\"main_content\" class=\"clearfix\">"
    html_content += "<div class=\"add_maincontent_padding\">"
    html_content += "<h1 class=\"add_icon_blue_arrow_right\">OPR CEQANet Communication: Rejection of Upgrade Request</h1>"
    html_content += "<P>Thank you for requesting an upgrade to your status on the State Clearinghouse CEQANet System.  Your request has been rejected.  You will not be able to submit or review CEQA documents at this time.</P>"
    html_content += "<P>Reason: " + self.request.POST.get('rejectreason') + "</P>"
    html_content += "<p>Please contact the State Clearinghouse at (916)445-0613 to discuss your status.</p>"
    html_content += "Thank you."
    html_content += "</div></div>"
    html_content += "</BODY></HTML>"

    msg = EmailMultiAlternatives(strSubject, strBody, strFrom, ToList)
    msg.attach_alternative(html_content, "text/html")
    msg.send()

def email_commentacceptance(self):
    doc = documents.objects.get(pk=self.request.POST.get('doc_pk'))

    usrprof = self.request.user.get_profile()
    usr_rag_pk = usrprof.set_rag_fk

    docurl = "%s?doc_pk=%s" % (reverse('commentdetail'),doc.doc_pk)
    
    emaillist = doc.doc_conemail

    grp = Group.objects.get(name='reviewers')
    usrs =grp.user_set.all()
    for u in usrs:
        if u.get_profile().set_rag_fk == usr_rag_pk:
            emaillist += "," + u.email
    
    strFrom = opr_email_address
    ToList = [emaillist]
    strSubject = "CEQANet: Comment Added to Document by Reviewing Agency"
    strBody = "A new comment has been added to the following document:" + "\n"
    strBody += "\n \n" + "--- Information Submitted ---" + "\n"
    strBody += "Document Type: " + doc.doc_doctype + "\n"        
    strBody += "Project Title: " + doc.doc_prj_fk.prj_title + "\n"
    strBody += "Project Location: " + doc.doc_location + "\n"
    strBody += "    City: " + doc.doc_city + "\n"
    strBody += "    County: " + doc.doc_county + "\n"
    strBody += "Project Description: " + doc.doc_prj_fk.prj_description + "\n"
    strBody += "Primary Contact:  " + "\n"
    strBody += "    Name: " + doc.doc_conname + "\n"
    strBody += "    Phone: " + doc.doc_conphone + "\n"
    strBody += "    E-mail: " + doc.doc_conemail + "\n"
    strBody += "DATE: " + doc.doc_received.strftime('%m/%d/%Y') + "\n"
    strBody += "\n \n" + "Please reply to this email if you have any questions regarding this action."

    html_content = "<!DOCTYPE html>"
    html_content += "<html class=\"no-js\" lang=\"en\"><HEAD><meta charset=\"utf-8\"><title>OPR CEQANet Email Communication</title>"
    html_content += "<link rel=\"stylesheet\" href=\"http://" + self.request.get_host() + static("ceqanet/CA_template/css/style.css") + "\">"
    html_content += "<link rel=\"stylesheet\" href=\"http://" + self.request.get_host() + static("ceqanet/CA_template/css/colorscheme_oceanside.css") + "\">"
    html_content += "</HEAD><body class=\"clearfix\">"
    html_content += "<div id=\"main_content\" class=\"clearfix\">"
    html_content += "<div class=\"add_maincontent_padding\">"
    html_content += "<h1 class=\"add_icon_blue_arrow_right\">OPR CEQANet Communication: Comment Added to Document by Reviewing Agency</h1>"
    html_content += "<P>Dear CEQANet User,<BR>"
    html_content += usr_rag_pk.rag_name + " has submitted a comment letter on the following CEQA document:</P>"
    html_content += "<ul><li>Project Title: " + doc.doc_prj_fk.prj_title + "</a>"
    html_content += "<li>Lead Agency: " + doc.doc_prj_fk.prj_leadagency
    html_content += "<li>Type of CEQA Document: " + doc.doc_doctype
    html_content += "<li>State Clearinghouse Number (SCH#), if existing: "
    if doc.doc_schno != None:
        html_content += doc.doc_schno
    else:
        html_content += "Not Assigned Yet"
    html_content += "<p>The State Review period for your document began on " + doc.doc_dept.strftime('%m/%d/%Y') + " and concludes on " + doc.doc_clear.strftime('%m/%d/%Y') + ".</P>"
    html_content += "<p><a href=\"http://" + self.request.get_host() + docurl + "\">Click Here to View The Comment Letter</a></P>"
    html_content += "<p>If the comment letter was received after the close of the State Review period above, the comment is considered a late comment (CEQA Guidelines 15207).  The State Clearinghouse encourages lead agencies to incorporate these comments into your final environmental document and to consider them prior to taking final action on the proposed project.</P>"
    html_content += "<p>If you have any questions, feel free to call the State Clearinghouse at (916)445-0613.</P>"
    html_content += "Thank you."
    html_content += "</div></div>"
    html_content += "</BODY></HTML>"

    msg = EmailMultiAlternatives(strSubject, strBody, strFrom, ToList)
    msg.attach_alternative(html_content, "text/html")
    msg.send()