from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'metrics.views.home', name='home'),
    # url(r'^metrics/', include('metrics.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/home/cs/Projects/django/anyadmin/metrics/site_media/'}),
)

urlpatterns += patterns('screencapture.views',
  (r'^record_movement/$','view_record_movement',{},'record_movement'),
)

urlpatterns += patterns('events.views',
  (r'^record_event/$','view_record_event',{},'record_event'),
)

urlpatterns += patterns('testurls.views',
  (r'^home_page/$','home_page',{'home_page_template':'testurls/home.html'},'home_page'),
  (r'^register_page/$','register_page',{'register_page_template':'testurls/register.html'},'register_page'),
)

urlpatterns += patterns('reportingtool.views',
  (r'^t_report/$','view_bi_report', {'bi_report_template':'reportingtool/bi_report.html'},'bi-report'),
  (r'^show_graph/$', 'view_chart_data', {'show_graph_template':'reportingtool/show_chart.html'},'show-chart'),
  (r'^return_csv/$', 'return_csv', {}),
)
