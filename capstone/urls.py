from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'timeclock.views.index'),
    url(r'^semester_(?P<semester_name>\w+)/?$', 'timeclock.views.project'),
    url(r'^admin/', include(admin.site.urls)),
)

