from django.conf.urls import *
from django.contrib import admin
from django.conf import settings
from csvimport.tests.views import index
admin.autodiscover()

# URL patterns for test django-csvimport install
try:
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
except:
    urlpatterns = [
        (r'^admin/', include(admin.site.urls)),
        (r'^index.html', index)
    ]
    if settings.DEBUG:
        urlpatterns += [
            url(r'^(?P<path>.*)$', 'django.views.static.serve', {
                'document_root': settings.MEDIA_ROOT,
            }),
       ]
    
