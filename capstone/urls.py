from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'timeclock.views.index'),
    url(r'^semester/(?P<semester_name>\d+)/$', 'timeclock.views.project'),
    url(r'^project/(?P<project_name>\d+)/$', 'timeclock.views.student'),
    url(r'^student/(?P<student_id>\d+)/$', 'timeclock.views.entertime'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^submittime/$', 'timeclock.views.submittime'),
)

