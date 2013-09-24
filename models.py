#from django.db import models
from django.contrib.gis.db import models
from django.contrib.auth.models import User

# Create your models here.
class counties(models.Model):
    geow_pk = models.AutoField(primary_key=True)
    geow_shortname = models.CharField(max_length=32)
    geow_longname = models.CharField(max_length=64)

class doctypes(models.Model):
    keyw_pk = models.AutoField(primary_key=True)
    keyw_shortname = models.CharField(max_length=32)
    keyw_longname = models.CharField(max_length=64)
    inlookup = models.BooleanField(default=True)

class docgeowords(models.Model):
    dgeo_pk = models.AutoField(primary_key=True)
    dgeo_geow_fk = models.ForeignKey("geowords",db_column="dgeo_geow_fk")
    dgeo_doc_fk = models.ForeignKey("documents",db_column="dgeo_doc_fk")
    dgeo_rank = models.IntegerField()
    dgeo_comment = models.CharField(max_length=64)
class dockeywords(models.Model):
    dkey_pk = models.AutoField(primary_key=True)
    dkey_doc_fk = models.ForeignKey("documents",db_column="dkey_doc_fk")
    dkey_keyw_fk = models.ForeignKey("keywords",db_column="dkey_keyw_fk")
    dkey_comment = models.CharField(null=True,blank=True,max_length=64)
    dkey_value1 = models.CharField(null=True,blank=True,max_length=16)
    dkey_value2 = models.CharField(null=True,blank=True,max_length=16)
    dkey_value3 = models.CharField(null=True,blank=True,max_length=16)
    dkey_rank = models.IntegerField()
class docreviews(models.Model):
    drag_pk = models.AutoField(primary_key=True)
    drag_doc_fk = models.ForeignKey("documents",db_column="drag_doc_fk")
    drag_rag_fk = models.ForeignKey("reviewingagencies",db_column="drag_rag_fk")
    drag_comment = models.CharField(max_length=64)
    drag_received = models.DateField()
    drag_sentbysch = models.BooleanField()
    drag_sentbylag = models.BooleanField()
    drag_late = models.BooleanField()
    drag_rank = models.IntegerField()
    drag_copies = models.IntegerField()
    sentbycode = models.CharField(max_length=1)
    dsnum = models.CharField(max_length=10)
    dscode = models.CharField(max_length=5)
    dsloc = models.CharField(max_length=30)
    drag_lateletter = models.DateField()
    drag_ragcomment = models.TextField(null=True,blank=True)

class documents(models.Model):
    doc_pk = models.AutoField(primary_key=True)
    doc_prj_fk = models.ForeignKey("projects",null=True,blank=True,db_column="doc_prj_fk")
    doc_cnty_fk = models.ForeignKey("counties",null=True,blank=True,db_column="doc_cnty_fk")
    doc_schno = models.CharField(null=True,blank=True,max_length=12,db_index=True)
    doc_doct_fk = models.ForeignKey("doctypes",null=True,blank=True,db_column="doc_doct_fk")
    doc_doctype = models.CharField(null=True,blank=True,max_length=3)
    doc_docname = models.CharField(null=True,blank=True,max_length=64)
    doc_title = models.TextField(null=True,blank=True)
    doc_description = models.TextField(null=True,blank=True)
    doc_comments = models.CharField(null=True,blank=True,max_length=64)
    doc_conname = models.CharField('Contact Name:',null=True,blank=True,max_length=64)
    doc_conagency = models.CharField(null=True,blank=True,max_length=64)
    doc_conphone = models.CharField(null=True,blank=True,max_length=32)
    doc_conemail = models.EmailField(null=True,blank=True,max_length=64)
    doc_confax = models.CharField(null=True,blank=True,max_length=32)
    doc_conaddress1 = models.CharField(null=True,blank=True,max_length=64)
    doc_conaddress2 = models.CharField(null=True,blank=True,max_length=64)
    doc_concity = models.CharField(null=True,blank=True,max_length=32)
    doc_constate = models.CharField(null=True,blank=True,max_length=2)
    doc_conzip = models.CharField(null=True,blank=True,max_length=10)
    doc_county = models.CharField('County:',null=True,blank=True,max_length=64)
    doc_city = models.CharField('CityL',null=True,blank=True,max_length=64)
    doc_region = models.TextField('Region:',null=True,blank=True)
    doc_location = models.TextField('Other Location Info:',null=True,blank=True)
    doc_notes = models.TextField(null=True,blank=True)
    doc_jobs = models.IntegerField(null=True,blank=True)
    doc_xstreets = models.CharField('Cross Streets:',null=True,blank=True,max_length=96)
    doc_zipcode = models.CharField(null=True,blank=True,max_length=10)
    doc_acres = models.CharField(null=True,blank=True,max_length=16)
    doc_parcelno = models.CharField('Parcel No:',null=True,blank=True,max_length=96)
    doc_township = models.CharField('Township:',null=True,blank=True,max_length=6)
    doc_range = models.CharField('Range:',null=True,blank=True,max_length=6)
    doc_section = models.CharField('Section:',null=True,blank=True,max_length=6)
    doc_base = models.CharField('Base:',null=True,blank=True,max_length=8)
    doc_highways = models.CharField(null=True,blank=True,max_length=32)
    doc_airports = models.CharField(null=True,blank=True,max_length=32)
    doc_railways = models.CharField(null=True,blank=True,max_length=32)
    doc_waterways = models.CharField(null=True,blank=True,max_length=96)
    doc_schools = models.CharField(null=True,blank=True,max_length=64)
    doc_doctypenotes = models.CharField(null=True,blank=True,max_length=32)
    doc_actionnotes = models.CharField(null=True,blank=True,max_length=32)
    doc_devnotes = models.CharField(null=True,blank=True,max_length=32)
    doc_issuesnotes = models.CharField(null=True,blank=True,max_length=32)
    doc_landuse = models.TextField(null=True,blank=True)
    doc_analyst = models.CharField(null=True,blank=True,max_length=5)
    doc_received = models.DateField(null=True,blank=True)
    doc_dept = models.DateField(null=True,blank=True)
    doc_agency = models.DateField(null=True,blank=True)
    doc_signed = models.DateField(null=True,blank=True)
    doc_clear = models.DateField(null=True,blank=True)
    doc_final = models.DateField(null=True,blank=True)
    doc_nod = models.DateField(null=True,blank=True)
    doc_detsigeffect = models.BooleanField(blank=True)
    doc_detnotsigeffect = models.BooleanField(blank=True)
    doc_deteir = models.BooleanField(blank=True)
    doc_detnegdec = models.BooleanField(blank=True)
    doc_detmitigation = models.BooleanField(blank=True)
    doc_detnotmitigation = models.BooleanField(blank=True)
    doc_detconsider = models.BooleanField(blank=True)
    doc_detnotconsider = models.BooleanField(blank=True)
    doc_detfindings = models.BooleanField(blank=True)
    doc_detnotfindings = models.BooleanField(blank=True)
    doc_eiravailableat = models.TextField(null=True,blank=True)
    doc_exministerial = models.BooleanField(blank=True)
    doc_exdeclared = models.BooleanField(blank=True)
    doc_exemergency = models.BooleanField(blank=True)
    doc_excategorical = models.BooleanField(blank=True)
    doc_exstatutory = models.BooleanField(blank=True)
    doc_exnumber = models.CharField(null=True,blank=True,max_length=32)
    doc_exreasons = models.TextField('Reasons why project is exempt:',null=True,blank=True)
    doc_srrreasons = models.TextField(null=True,blank=True)
    doc_ssragencies = models.TextField(null=True,blank=True)
    doc_ssrdays = models.IntegerField(null=True,blank=True)
    doc_ssrapproved = models.DateField(null=True,blank=True)
    doc_prncomment = models.DateField(null=True,blank=True)
    doc_prnnocomment = models.DateField(null=True,blank=True)
    doc_prnlatecomment = models.DateField(null=True,blank=True)
    doc_prnearlyconsult = models.DateField(null=True,blank=True)
    doc_prnnopletter = models.DateField(null=True,blank=True)
    doc_prnacknowledgement = models.DateField(null=True,blank=True)
    doc_letternote = models.TextField(null=True,blank=True)
    doc_updated = models.TextField(null=True,blank=True)
    doc_nodbylead = models.BooleanField(blank=True)
    doc_nodbyresp = models.BooleanField(blank=True)
    doc_nodagency = models.CharField(null=True,blank=True,max_length=64)
    doc_tribeinfo = models.CharField(null=True,blank=True,max_length=64)
    doc_lat_deg = models.CharField(null=True,blank=True,max_length=12)
    doc_lat_min = models.CharField(null=True,blank=True,max_length=10)
    doc_lat_sec = models.CharField(null=True,blank=True,max_length=10)
    doc_long_deg = models.CharField(null=True,blank=True,max_length=12)
    doc_long_min = models.CharField(null=True,blank=True,max_length=10)
    doc_long_sec = models.CharField(null=True,blank=True,max_length=10)
    doc_pending = models.BooleanField()
    doc_visible = models.BooleanField()
    doc_review = models.BooleanField()
    doc_plannerregion = models.IntegerField(null=True,blank=True)
    doc_plannerreview = models.BooleanField()

    class Meta:
        #ordering = ['name']
        verbose_name = "Document"
        verbose_name_plural = "Documents"

    def __unicode__(self):
        return self.doc_pk

class geowordlists(models.Model):
    geol_pk = models.AutoField(primary_key=True)
    geol_shortname = models.CharField(null=True,blank=True,max_length=32)
    geol_longname = models.CharField(null=True,blank=True,max_length=64)
    geol_description = models.TextField(null=True,blank=True)
    geol_listsource = models.CharField(null=True,blank=True,max_length=10)

class geowords(models.Model):
    geow_pk = models.AutoField(primary_key=True)
    geow_geol_fk = models.ForeignKey("geowordlists",db_column="geow_geol_fk")
    geow_shortname = models.CharField(max_length=32,db_index=True)
    geow_longname = models.CharField(max_length=64)
    geow_description = models.TextField()
    geow_originalcontrolid = models.CharField(max_length=10)
    geow_recordsource = models.CharField(max_length=10)
    inlookup = models.BooleanField(default=True)

    def __unicode__(self):
        return self.geow_shortname        

class holidays(models.Model):

    hday_pk = models.AutoField(primary_key=True)
    hday_name = models.CharField(max_length=40)
    hday_date = models.DateField()
    hday_dow = models.CharField(max_length=10)
    hday_note = models.TextField()

class keywordlists(models.Model):
    keyl_pk = models.AutoField(primary_key=True)
    keyl_shortname = models.CharField(max_length=32)
    keyl_longname = models.CharField(max_length=64)
    keyl_description = models.TextField()
    keyl_listsource = models.CharField(max_length=10)

class keywords(models.Model):
    keyw_pk = models.AutoField(primary_key=True)
    keyw_keyl_fk = models.ForeignKey("keywordlists",db_column="keyw_keyl_fk")
    keyw_shortname = models.CharField(max_length=32)
    keyw_longname = models.CharField(max_length=64)
    keyw_description = models.TextField()
    keyw_caption1 = models.CharField(max_length=10)
    keyw_caption2 = models.CharField(max_length=10)
    keyw_caption3 = models.CharField(max_length=10)
    keyw_originalcontrolid = models.CharField(max_length=10)
    keyw_recordsource = models.CharField(max_length=10)

class latlongs(models.Model):
    doc_pk = models.AutoField(primary_key=True)
    doc_prj_fk = models.ForeignKey("projects",db_column="doc_prj_fk")
    doc_schno = models.CharField(null=True,blank=True,max_length=12)
    doc_doctype = models.CharField(max_length=3)
    doc_lat_deg = models.CharField(null=True,blank=True,max_length=12)
    doc_lat_min = models.CharField(null=True,blank=True,max_length=10)
    doc_lat_sec = models.CharField(null=True,blank=True,max_length=10)
    doc_long_deg = models.CharField(null=True,blank=True,max_length=12)
    doc_long_min = models.CharField(null=True,blank=True,max_length=10)
    doc_long_sec = models.CharField(null=True,blank=True,max_length=10)
    doc_latitude = models.CharField(max_length=30)
    doc_longitude = models.CharField(max_length=30)
    doc_map_link = models.CharField(null=True,blank=True,max_length=240)

class leadagencies(models.Model):
    lag_pk = models.AutoField(primary_key=True)
    lag_geow_fk = models.ForeignKey("geowords",db_column="lag_geow_fk")
    lag_domain = models.CharField(max_length=20)
    lag_name = models.CharField(max_length=90,db_index=True)
    lag_title = models.CharField(max_length=90)
    lag_address1 = models.CharField(max_length=50)
    lag_address2 = models.CharField(max_length=50)
    lag_city = models.CharField(max_length=30)
    lag_county = models.CharField(max_length=20)
    lag_state = models.CharField(max_length=2)
    lag_zip = models.CharField(max_length=10)
    lag_phone = models.CharField(max_length=30)
    lag_fax = models.CharField(max_length=30)
    lag_sch_no = models.CharField(max_length=10)
    lag_updated = models.DateField()
    lag_acronym = models.CharField(max_length=10)
    lag_disable = models.BooleanField()
    lag_prjcnt = models.IntegerField()
    lag_note = models.CharField(max_length=60)
    inlookup = models.BooleanField(default=True)

    def __unicode__(self):
        return self.lag_name

class prinfo(models.Model):
    info_prjdate = models.DateField()
    info_docdate = models.DateField()

class projects(models.Model):
    prj_pk = models.AutoField(primary_key=True)
    prj_lag_fk = models.ForeignKey("leadagencies",db_column="prj_lag_fk")
    prj_schno = models.CharField(null=True,blank=True,max_length=12)
    prj_title = models.CharField(null=True,blank=True,max_length=160)
    prj_comments = models.TextField(null=True,blank=True)
    prj_doc_fk = models.ForeignKey("documents",db_column="prj_doc_fk")
    prj_status = models.CharField(null=True,blank=True,max_length=3)
    prj_description = models.TextField(null=True,blank=True)
    prj_datefirst = models.DateField(null=True,blank=True)
    prj_datelast = models.DateField(null=True,blank=True)
    prj_analyst = models.CharField(null=True,blank=True,max_length=5)
    prj_leadagency = models.CharField(null=True,blank=True,max_length=90)
    prj_otheragency = models.CharField(null=True,blank=True,max_length=90)
    prj_otheraddress1 = models.CharField(null=True,blank=True,max_length=90)
    prj_otheraddress2 = models.CharField(null=True,blank=True,max_length=90)
    prj_othercity = models.CharField(null=True,blank=True,max_length=30)
    prj_othercounty = models.CharField(null=True,blank=True,max_length=20)
    prj_otherstate = models.CharField(null=True,blank=True,max_length=2)
    prj_otherzip = models.CharField(null=True,blank=True,max_length=10)
    prj_otherphone = models.CharField(null=True,blank=True,max_length=20)
    prj_updated = models.DateField(null=True,blank=True)
    prj_pending = models.BooleanField()
    prj_visible = models.BooleanField()
    prj_plannerreview = models.BooleanField()

class reviewingagencies(models.Model):
    rag_pk = models.AutoField(primary_key=True)
    rag_name = models.CharField(max_length=90,db_index=True)
    rag_title = models.CharField(max_length=90,blank=True)
    rag_subtitle = models.CharField(max_length=50,blank=True)
    rag_address1 = models.CharField(max_length=50,blank=True)
    rag_address2 = models.CharField(max_length=50,blank=True)
    rag_city = models.CharField(max_length=25,blank=True)
    rag_county = models.CharField(max_length=16,blank=True)
    rag_state = models.CharField(max_length=2,blank=True)
    rag_zip = models.CharField(max_length=10,blank=True)
    rag_phone = models.CharField(max_length=30,blank=True)
    rag_copies = models.IntegerField()
    rag_rank = models.IntegerField()
    rag_default = models.BooleanField()
    rag_acronym = models.CharField(max_length=10)
    rag_disable = models.BooleanField()
    inlookup = models.BooleanField(default=True)

    def __unicode__(self):
        return self.rag_title

class UserProfile(models.Model):
    user = models.ForeignKey(User,unique=True)
    region = models.IntegerField(blank=True)
    set_lag_fk = models.ForeignKey("leadagencies",blank=True,null=True,db_column="set_lag_fk")
    set_rag_fk = models.ForeignKey("reviewingagencies",blank=True,null=True,db_column="set_rag_fk")

class clearinghouse(models.Model):
    schnoprefix = models.CharField(max_length=6)
    currentid = models.IntegerField()

class Locations(models.Model):
    '''Spatial model to store locations associations with Documents'''
    document = models.ForeignKey("documents",db_column="doc_pk")
    geom = models.GeometryCollectionField()
    objects = models.GeoManager()

    class Meta:
        verbose_name = "Location"
        verbose_name_plural = "Locations"


