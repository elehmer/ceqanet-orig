import os
from ceqanet.models import documents,projects,latlongs,dockeywords,docgeowords,docreviews,docattachments,clearinghouse,Locations,doccomments
from django.contrib.auth.models import User,Group
from django.core.mail import send_mail
from datetime import datetime

opr_email_address = "opr@ceqanet.ca.gov"

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
    emaillist = doc.doc_conemail
    if doc.doc_conemail != doc.doc_added_userid.email:
        emaillist += "," + doc.doc_added_userid.email

    strFrom = opr_email_address
    ToList = [emaillist]
    strSubject = "CEQANet: Acceptance of Submittal - " + doc.doc_doctype
    strBody = "The " + doc.doc_docname + " document submitted to the State Clearinghouse on " + doc.doc_received.strftime('%m/%d/%Y') + " was accepted.\n \n"
    strBody += "\n \n" + "Please reply to this email if you have any questions regarding this acceptance."
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

    try:
        send_mail(strSubject,strBody,strFrom,ToList,fail_silently=False)
    except Exception as detail:
        print "Not Able to Send Email:", detail

def email_rejection(self):
    doc = documents.objects.get(pk=self.request.POST.get('doc_pk'))
    emaillist = doc.doc_conemail
    if doc.doc_conemail != doc.doc_added_userid.email:
        emaillist += "," + doc.doc_added_userid.email

    strFrom = opr_email_address
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
    strBody += "Primary Contact:  " + "\n"
    strBody += "    Name: " + doc.doc_conname + "\n"
    strBody += "    Phone: " + doc.doc_conphone + "\n"
    strBody += "    E-mail: " + doc.doc_conemail + "\n"
    strBody += "DATE: " + doc.doc_received.strftime('%m/%d/%Y') + "\n"

    try:
        send_mail(strSubject,strBody,strFrom,ToList,fail_silently=False)
    except Exception as detail:
        print "Not Able to Send Email:", detail

def email_demotiontodraft(self,doc):
    emaillist = doc.doc_conemail
    if doc.doc_conemail != doc.doc_added_userid.email:
        emaillist += "," + doc.doc_added_userid.email

    strFrom = opr_email_address
    ToList = [emaillist]
    strSubject = "CEQANet: Rejection of Submittal - " + doc.doc_doctype
    strBody = "The " + doc.doc_docname + " document submitted to the State Clearinghouse on " + doc.doc_received.strftime('%m/%d/%Y') + " was rejected for the following reason:  \n \n"
    strBody += self.request.POST.get('rejectreason')
    strBody += "The document has been returned to draft mode and you may attempt to submit it again later." + "\n"
    strBody += "\n \n" + "Please reply to this email if you have any questions regarding this rejection." + "\n"
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

    try:
        send_mail(strSubject,strBody,strFrom,ToList,fail_silently=False)
    except Exception as detail:
        print "Not Able to Send Email:", detail

def email_submission(self,doc):
    emaillist = doc.doc_conemail
    if doc.doc_conemail != doc.doc_added_userid.email:
        emaillist += "," + doc.doc_added_userid.email
        emaillist += "," + opr_email_address

    strFrom = opr_email_address
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
    strBody += "Primary Contact:  " + "\n"
    strBody += "    Name: " + doc.doc_conname + "\n"
    strBody += "    Phone: " + doc.doc_conphone + "\n"
    strBody += "    E-mail: " + doc.doc_conemail + "\n"
    strBody += "DATE: " + doc.doc_received.strftime('%m/%d/%Y') + "\n"

    try:
        send_mail(strSubject,strBody,strFrom,ToList,fail_silently=False)
    except Exception as detail:
        print "Not Able to Send Email:", detail

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

    try:
        send_mail(strSubject,strBody,strFrom,ToList,fail_silently=False)
    except Exception as detail:
        print "Not Able to Send Email:", detail

def email_inreview(self,doc):
    emaillist = doc.doc_conemail
    if doc.doc_conemail != doc.doc_added_userid.email:
        emaillist += "," + doc.doc_added_userid.email

    grp = Group.objects.get(name='reviewers')
    usrs =grp.user_set.all()
    for u in usrs:
        for ra in self.request.POST.get('ragencies'):
            if u.get_profile().set_rag_fk == ra:
                emaillist += "," + u.email

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

    try:
        send_mail(strSubject,strBody,strFrom,ToList,fail_silently=False)
    except Exception as detail:
        print "Not Able to Send Email:", detail

def email_requestforupgrade():
    strFrom = opr_email_address
    ToList = opr_email_address
    strSubject = "CEQANet: Upgrade Request"
    strBody = "There is a new request for account upgrade. Please check website." + "\n"

    try:
        send_mail(strSubject,strBody,strFrom,ToList,fail_silently=False)
    except Exception as detail:
        print "Not Able to Send Email:", detail

def email_upgradeacceptance(self):
    emaillist = User.objects.get(pk=self.request.POST.get('user_id')).email
    
    strFrom = opr_email_address
    ToList = [emaillist]
    strSubject = "CEQANet: Acceptance of Account Upgrade Request"
    strBody = "Your request to have your CEQANet account upgraded has been accepted." + "\n"
    strBody += "\n \n" + "Please reply to this email if you have any questions regarding this rejection."

    try:
        send_mail(strSubject,strBody,strFrom,ToList,fail_silently=False)
    except Exception as detail:
        print "Not Able to Send Email:", detail

def email_upgraderejection(self):
    emaillist = User.objects.get(pk=self.request.POST.get('user_id')).email
    
    strFrom = opr_email_address
    ToList = [emaillist]
    strSubject = "CEQANet: Rejection of Account Upgrade Request"
    strBody = "Your request to have your CEQANet account upgraded has been rejected. Reason for rejection follows:" + "\n"
    strBody += self.request.POST.get('rejectreason')
    strBody += "\n \n" + "Please reply to this email if you have any questions regarding this rejection."

    try:
        send_mail(strSubject,strBody,strFrom,ToList,fail_silently=False)
    except Exception as detail:
        print "Not Able to Send Email:", detail

def email_commentacceptance(self):
    doc = documents.objects.get(pk=self.request.POST.get('doc_pk'))

    usrprof = self.request.user.get_profile()
    usr_rag_pk = usrprof.set_rag_fk
    
    emaillist = doc.doc_conemail

    grp = Group.objects.get(name='reviewers')
    usrs =grp.user_set.all()
    for u in usrs:
        if u.get_profile().set_rag_fk == usr_rag_pk:
            emaillist += "," + u.email
    
    strFrom = opr_email_address
    ToList = [emaillist]
    strSubject = "CEQANet: Comment Added to Document by Reveiwing Agency"
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

    try:
        send_mail(strSubject,strBody,strFrom,ToList,fail_silently=False)
    except Exception as detail:
        print "Not Able to Send Email:", detail
