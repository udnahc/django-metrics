from django.db import models
from django.contrib import admin

# Create your models here.
class ReportingToolManager(models.Manager):
    def get_results_and_headers(self, request):
        from reportingtool import report_utils
        from reportingtool.report_utils import ReportChangeList
        from reportingtool.report_utils import _request_param_get

        report_id = _request_param_get(request,'id')
        filter = _request_param_get(request,'filter')
        rt = self.get(id=report_id)
        path = getattr(report_utils, rt.default_method)
        if callable(path):
            results =  path(filter)
        result_headers = rt.report_headers.split(",")

        # Process the results and send it back to the view                   

        rcl = ReportChangeList(results,request)
        rcl.get_results(result_headers)
        base_url = rcl.base_url

        return (rt,rcl,base_url)


class ReportingTool(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50,blank=False,null=False)
    report_headers = models.TextField(blank=False, null=False)

    default_method = models.CharField(max_length=200,blank=False, null=False)
    graph_headers = models.TextField(blank=False, null=False)

    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    objects = ReportingToolManager()

    def view_report(self):
        return ('<a href=/t_report/?id='+ str(self.id) +'>Report</a>')
    view_report.allow_tags = True

class ReportingToolAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_on', 'view_report')
    ordering = ('-created_on',)
admin.site.register(ReportingTool,ReportingToolAdmin)                                                                                                       
