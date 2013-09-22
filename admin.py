from django.contrib.gis import admin
from ceqanet.models import documents, Locations

class CaliforniaAdmin(admin.OSMGeoAdmin):
    default_lon= -13449176
    default_lat= 4546224    
    default_zoom= 6


admin.site.register(documents)
admin.site.register(Locations, CaliforniaAdmin)
