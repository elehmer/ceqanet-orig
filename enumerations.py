DOCUMENT_TYPES = (
    ('108','Notice of Determination (NOD)'),
    ('109','Notice of Exemption (NOE)'),
    ('107','Negative Declaration (NEG)'),
    ('500008','Mitigated Negative Declaration (MND)'),
    ('106','Draft EIR (EIR)'),
    ('110','Supplemental EIR (SIR)'),
    ('124','Subsequent EIR (SBE)'),
    ('114','Final Document (FIN)'),
    ('102','Notice of Preperation (NOP)'),
    ('None','Other Notice of Completion (NOC)')
)

PRJ_SORT_FIELDS = (
    ('-prj_schno','Clearinghouse Number (Descending)'),
    ('prj_schno','Clearinghouse Number (Ascending)'),
    ('prj_title','Project Title'),
    ('prj_description','Project Description'),
    ('prj_leadagency','Lead Agency'),
    ('prj_status','Document Type'),
    ('-prj_datefirst','Date First Document Received (Descending)'),
    ('prj_datefirst','Date First Document Received (Ascending)'),
    ('-prj_datelast','Date Latest Document Received (Descending)'),
    ('prj_datelast','Date Latest Document Received (Ascending)')
)

DOC_SORT_FIELDS = (
    ('-doc_prj_fk__prj_schno','Clearinghouse Number (Descending)'),
    ('doc_prj_fk__prj_schno','Clearinghouse Number (Ascending)'),
    ('doc_prj_fk__prj_title','Project Title'),
    ('doc_prj_fk__prj_description','Project Description'),
    ('doc_leadagency','Lead Agency'),
    ('doc_doctype','Document Type'),
    ('-doc_received','Date Received (Descending)'),
    ('doc_received','Date Received (Ascending)'),
)

COMMENT_CHOICES = (
    ('text', 'Submit Text Comment'),
    ('file', 'Submit PDF Comment')
)

COLATION_CHOICES = (
    ('project', 'Project'),
    ('document', 'Document')
)

UPGRADE_CHOICES = (
    ('lead', 'Request to Become Part of Lead Agencies Group:'),
    ('review', 'Request to Become Part of Reviewing Agencies Group:')
)

NODAGENCY_CHOICES = (
    ('lead','Lead Agency'),
    ('resp','Responsible Agency')
)

DETERMINATION_CHOICES = (
    ('True',''),
    ('False','')
)

RDODATE_CHOICES = (
    ('all', 'All'),
    ('range', 'Range')
)

RDOPLACE_CHOICES = (
    ('all', 'All'),
    ('city', 'City'),
    ('county', 'County')
)

RDOLAG_CHOICES = (
    ('all', 'All'),
    ('agency', 'Agency')
)

RDORAG_CHOICES = (
    ('all', 'All'),
    ('agency', 'Agency')
)

RDODOCTYPE_CHOICES = (
    ('all', 'All'),
    ('type', 'Type')
)

RDOLAT_CHOICES = (
    ('all', 'All'),
    ('type', 'Type')
)

RDODEVTYPE_CHOICES = (
    ('all', 'All'),
    ('type', 'Type')
)

RDOISSUE_CHOICES = (
    ('all', 'All'),
    ('issue', 'Issue')
)

RDOTITLE_CHOICES = (
    ('all', 'All'),
    ('title', 'Title Contains')
)

RDODESCRIPTION_CHOICES = (
    ('all', 'All'),
    ('description', 'Description Contains')
)

PROJECT_EXISTS = (
    ('yes','Yes'),
    ('no','No')
)

EXEMPT_STATUS_CHOICES = (
    (1,'Ministerial (Sec.21080(b)(1); 15268);'),
    (2,'Declared Emergency (Sec. 21080(b)(3);15269(a));'),
    (3,'Emergency Project (Sec. 21080(b)(4); 15269(b)(c));'),
    (4,'Categorical Exemption. State type and section number:'),
    (5,'Statutory Exemptions. State code number:')
)

PLANNERREGION_CHOICES = (
    (1,'1 (South)'),
    (2,'2 (North)'),
    (4,'4 (Federal)')
)

NODFEESPAID_CHOICES = (
    ('yes','Yes'),
    ('no','No')
)
