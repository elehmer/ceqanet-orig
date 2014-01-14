import os
from ceqanet.models import documents,projects,latlongs,dockeywords,docreviews,docattachments,clearinghouse
from django.core.mail import send_mail

def generate_schno(region):
    ch = clearinghouse.objects.get(pk=1)
    currentidnum = str(ch.currentid)
    if len(currentidnum) == 1:
        currentidnum = "00"+currentidnum
    elif len(currentidnum) == 2:
        currentidnum = "0"+currentidnum
    schno = ch.schnoprefix + str(region) + currentidnum
    ch.currentid = ch.currentid+1
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
    dockeywords.objects.filter(dkey_doc_fk=doc.doc_pk).delete()
    docreviews.objects.filter(drag_doc_fk=doc.doc_pk).delete()

    docatts = docattachments.objects.filter(datt_doc_fk=doc.doc_pk)
    for att in docatts:
        os.remove(os.path.join(settings.MEDIA_ROOT, att.datt_file.name))
    docatts.delete()
    doc.delete()

def email_rejection(self):
    doc = documents.objects.get(pk=self.request.POST.get('doc_pk'))
    emaillist = doc.doc_conemail
    if doc.doc_conemail != self.request.user.email:
        emaillist += "," + self.request.user.email

    strFrom = "ceqanet@opr.ca.gov"
    ToList = [emaillist]
    strSubject = "CEQANet: Rejection of Submittal - " + doc.doc_doctype
    strBody = "The " + doc.doc_docname + " document submitted to the State Clearinghouse on " + doc.doc_received.strftime('%m/%d/%Y') + " was rejected for the following reason:  \n \n"
    strBody += self.request.POST.get('rejectreason')
    strBody += "\n \n" + "Please reply to this email if you have any questions regarding this rejection."
    strBody += "\n \n" + "--- Information Submitted ---" + "\n"
    strBody += "Document Type: " + doc.doc_doctype + "\n"        
    strBody += "Project Title: " + doc.doc_prj_fk.prj_title + "\n"
    strBody += "Project Location: " + doc.doc_location + "\n"
    strBody += "    City: " + doc.doc_city + "\n"
    strBody += "    County: " + doc.doc_county + "\n"
    strBody += "Project Description: " + doc.doc_prj_fk.prj_description + "\n"
    strBody += "Agency Approving Project: " + doc.doc_prj_fk.prj_leadagency + "\n"
    strBody += "Primary Contact:  " + "\n"
    strBody += "    Name: " + doc.doc_conname + "\n"
    strBody += "    Phone: " + doc.doc_conphone + "\n"
    strBody += "    E-mail: " + doc.doc_conemail + "\n"
    strBody += "DATE: " + doc.doc_received.strftime('%m/%d/%Y') + "\n"

    try:
        send_mail(strSubject,strBody,strFrom,ToList,fail_silently=False)
    except Exception as detail:
        print "Not Able to Send Email:", detail

def email_demotiontodraft(self):
    doc = documents.objects.get(pk=self.request.POST.get('doc_pk'))
    emaillist = doc.doc_conemail
    if doc.doc_conemail != self.request.user.email:
        emaillist += "," + self.request.user.email

    strFrom = "ceqanet@opr.ca.gov"
    ToList = [emaillist]
    strSubject = "CEQANet: Rejection of Submittal - " + doc.doc_doctype
    strBody = "The " + doc.doc_docname + " document submitted to the State Clearinghouse on " + doc.doc_received.strftime('%m/%d/%Y') + " was rejected for the following reason:  \n \n"
    strBody += self.request.POST.get('rejectreason')
    strBody += "The document has been returned to draft mode and you may attempt to submit it again later."
    strBody += "\n \n" + "Please reply to this email if you have any questions regarding this rejection."
    strBody += "\n \n" + "--- Information Submitted ---" + "\n"
    strBody += "Document Type: " + doc.doc_doctype + "\n"        
    strBody += "Project Title: " + doc.doc_prj_fk.prj_title + "\n"
    strBody += "Project Location: " + doc.doc_location + "\n"
    strBody += "    City: " + doc.doc_city + "\n"
    strBody += "    County: " + doc.doc_county + "\n"
    strBody += "Project Description: " + doc.doc_prj_fk.prj_description + "\n"
    strBody += "Agency Approving Project: " + doc.doc_prj_fk.prj_leadagency + "\n"
    strBody += "Primary Contact:  " + "\n"
    strBody += "    Name: " + doc.doc_conname + "\n"
    strBody += "    Phone: " + doc.doc_conphone + "\n"
    strBody += "    E-mail: " + doc.doc_conemail + "\n"
    strBody += "DATE: " + doc.doc_received.strftime('%m/%d/%Y') + "\n"

    try:
        send_mail(strSubject,strBody,strFrom,ToList,fail_silently=False)
    except Exception as detail:
        print "Not Able to Send Email:", detail

def email_submission(self):
    doc = documents.objects.get(pk=self.request.POST.get('doc_pk'))
    emaillist = doc.doc_conemail
    if doc.doc_conemail != self.request.user.email:
        emaillist += "," + self.request.user.email

    strFrom = "ceqanet@opr.ca.gov"
    ToList = [emaillist]
    strSubject = "Confirmation of Submittal - " + doc.doc_doctype
    strBody = "This confirms receipt of your electronic " + doc.doc_docname + " form submission on " + doc.doc_received.strftime('%m/%d/%Y') + ".  \n \n"
    strBody += "The State Clearinghouse will review your submittal and provide a State Clearinghouse Number and filing date within one business day. \n \n"
    strBody += "If you have questions about the form submittal process, please reply to this email.  Thank you for using CEQAnet. \n"
    strBody += "\n \n" + "--- Information Submitted ---" + "\n"
    strBody += "Document Type: " + doc.doc_doctype + "\n"        
    strBody += "Project Title: " + doc.doc_prj_fk.prj_title + "\n"
    strBody += "Project Location: " + doc.doc_location + "\n"
    strBody += "    City: " + doc.doc_city + "\n"
    strBody += "    County: " + doc.doc_county + "\n"
    strBody += "Project Description: " + doc.doc_prj_fk.prj_description + "\n"
    strBody += "Agency Approving Project: " + doc.doc_prj_fk.prj_leadagency + "\n"
    strBody += "Primary Contact:  " + "\n"
    strBody += "    Name: " + doc.doc_conname + "\n"
    strBody += "    Phone: " + doc.doc_conphone + "\n"
    strBody += "    E-mail: " + doc.doc_conemail + "\n"
    strBody += "DATE: " + doc.doc_received.strftime('%m/%d/%Y') + "\n"

    try:
        send_mail(strSubject,strBody,strFrom,ToList,fail_silently=False)
    except Exception as detail:
        print "Not Able to Send Email:", detail
