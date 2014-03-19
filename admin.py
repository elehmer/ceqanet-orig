from django.contrib.gis import admin
from ceqanet.models import Locations
from ceqanet.models import projects,documents,geowords,leadagencies,reviewingagencies,doctypes,dockeywords,docreviews,latlongs,counties,UserProfile,clearinghouse,keywords,docattachments

from olwidget.admin import GeoModelAdmin

class CaliforniaAdmin(GeoModelAdmin):
    options ={
        'layers':['osm.mapnik'], 
        'default_lon': -13449176,
        'default_lat': 4546224,    
        'default_zoom': 6,
        'zoom_to_data_extent': True,
        }


admin.site.register(projects)
admin.site.register(documents)
admin.site.register(geowords)
admin.site.register(leadagencies)
admin.site.register(reviewingagencies)
admin.site.register(doctypes)
admin.site.register(dockeywords)
admin.site.register(docreviews)
admin.site.register(latlongs)
admin.site.register(counties)
admin.site.register(UserProfile)
admin.site.register(clearinghouse)
admin.site.register(keywords)
admin.site.register(docattachments)
admin.site.register(Locations, CaliforniaAdmin)
