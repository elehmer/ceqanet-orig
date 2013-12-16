from django.contrib.gis import admin
from ceqanet.models import documents, Locations
from olwidget.admin import GeoModelAdmin

class CaliforniaAdmin(GeoModelAdmin):
    options ={
        'layers':['osm.mapnik'], 
        'default_lon': -13449176,
        'default_lat': 4546224,    
        'default_zoom': 6,
        'zoom_to_data_extent': True,
        }


admin.site.register(documents)
admin.site.register(Locations, CaliforniaAdmin)
