from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.conf import settings
from csvimport.tests.views import index
admin.autodiscover()

# URL patterns for test django-csvimport install

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^index.html', index)
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
   )
