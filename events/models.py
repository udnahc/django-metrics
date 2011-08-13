from django.db import models
from django.contrib import admin
from datetime import datetime, timedelta


class EventTrackerManager(models.Manager):
    def create_event(self,event_tracker = None,**params):
        try:
            if not event_tracker:
                event_tracker = EventTracker()

            for param in params:
                setattr(event_tracker,param,params[param])
            event_tracker.save()
            return event_tracker
        except Exception,e:
            pass
        return None

class EventTracker(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(blank=True, null=True)
    category = models.TextField(blank=True,null=True)
    action = models.TextField(blank=True,null=True)
    label = models.TextField(blank=True,null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    objects = EventTrackerManager()

class EventTrackerAdmin(admin.ModelAdmin):
    list_display = ('category','action', 'label','created_on')
    list_filter = ('category','action','created_on')
    search_fields = ['email']

admin.site.register(EventTracker, EventTrackerAdmin)                                                                                                       

