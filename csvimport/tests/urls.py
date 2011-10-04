from django.conf.urls.defaults import patterns, include
from django.contrib import admin

admin.autodiscover()

# URL patterns for test django-csvimport install

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
)
