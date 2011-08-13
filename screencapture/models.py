from django.db import models
from django.contrib import admin
from datetime import datetime, timedelta

class MovementManager(models.Manager):
    def create_tale(self,movement = None,**params):
        try:
            if not movement:
                movement = Movement()

            for param in params:
                setattr(movement,param,params[param])
            movement = movement.save()
            return clicktale
        except Exception,e:
            pass
        return None

class Movement(models.Model):
    id = models.AutoField(primary_key=True)
    project = models.IntegerField(blank=True)
    ip = models.TextField(blank=True)
    full_url = models.TextField(blank=True)
    total_time = models.IntegerField(blank=True)
    user_email = models.TextField(blank=True)
    tale = models.TextField(blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    objects = MovementManager()

    def show_video_url(self):
        return ('<a href="%s%s%s">%s%s%s</a>') % (self.full_url,'?show_video=',self.id,self.full_url,'?show_video=',self.id)
    show_video_url.short_description = 'Link to replay video '
    show_video_url.allow_tags = True
    def __unicode__(self):
        return 'User - %s , URL - %s, Accessed On - %s ' % (self.user_email, self.full_url, self.created_on)

class MovementAdmin(admin.ModelAdmin):
    list_display = ('ip','show_video_url','user_email', 'created_on')
    list_filter = ('full_url','created_on')
    search_fields = ['user_email']

admin.site.register(Movement, MovementAdmin)                               

