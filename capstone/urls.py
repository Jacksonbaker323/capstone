from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'timeclock.views.index'),
    url(r'^redir', 'timeclock.views.index'),
    url(r'^semester/(?P<semester_name>\d+)/$', 'timeclock.views.project'),
    url(r'^project/(?P<project_name>\d+)/$', 'timeclock.views.student'),
    url(r'^student/(?P<student_id>\d+)/$', 'timeclock.views.entertime'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^submittime/$', 'timeclock.views.submittime'),
	url(r'^edittime/$', 'timeclock.views.edittime'),
    url(r'^reporting/$', 'timeclock.views.reporting'),
	url(r'^reporting/(?P<semester_name>\d+)/$', 'timeclock.views.reporting'),
	url(r'^editshift/(?P<shift_id>\d+)/$', 'timeclock.views.editshift'),
    url(r'^report/$', 'timeclock.views.reportingindex'),
	url(r'^clearsemester/', 'timeclock.views.deleteSemesterCookie'),
	url(r'^pmo_report/(?P<semester_name>\d+)/$', 'timeclock.views.pmo_report'),
	url(r'^pmo_report_select/$', 'timeclock.views.pmo_reportindex'),
	url(r'^pm_report/(?P<project_name>\d+)/$', 'timeclock.views.pm_report'),
	url(r'^pm_report_select/$', 'timeclock.views.pm_reportindex'), #This url is in here twice to allow for either pattern to be matched
	url(r'^pm_report_select/(?P<semester_name>\d+)/$', 'timeclock.views.pm_reportindex'),
)


