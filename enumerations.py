DOCUMENT_TYPES = (
    ('NOC','NOC'),
    ('NOD','NOD'),
    ('NOE','NOE'),
    ('NOP','NOP')
)

SORT_FIELDS = (
    ('-doc_prj_fk__prj_schno','Clearinghouse Number (Descending)'),
    ('doc_prj_fk__prj_schno','Clearinghouse Number (Ascending)'),
    ('doc_prj_fk__prj_leadagency','Lead Agency'),
    ('doc_prj_fk__prj_title','Project Title'),
    ('doc_description','Project Description'),
    ('doc_docname','Document Type'),
    ('-doc_received','Date Received (Descending)'),
    ('doc_received','Date Received (Ascending)')
)

COLATION_CHOICES = (
    ('project', 'Project'),
    ('document', 'Document')
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
    (0,'0'),
    (1,'1'),
    (2,'2'),
    (3,'3'),
    (4,'4'),
    (5,'5'),
    (6,'6'),
    (7,'7'),
    (8,'8'),
    (9,'9')
)
