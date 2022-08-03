from django.contrib import admin

from event_map.models import AirtableSync, Event, EventMap, ActionNetworkECSync

# Register your models here.
admin.site.register(AirtableSync)
admin.site.register(Event)
admin.site.register(EventMap)
admin.site.register(ActionNetworkECSync)
