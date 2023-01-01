from django.contrib import admin
from django.conf import settings
from csvimport.tests.views import index

admin.autodiscover()

# URL patterns for test django-csvimport install
try:
    # 4 or later
    from django.urls import re_path

    urlpatterns = [re_path(r"^admin/", admin.site.urls), re_path(r"^.*", index)]
except:
    from django.conf.urls import url, include

    try:
        # 1.9 or later
        urlpatterns = [url(r"^admin/", admin.site.urls), url(r"^.*", index)]
    except:
        # 1.8 or earlier
        urlpatterns = patterns(
            "", (r"^admin/", include(admin.site.urls)), (r"^.*", index)
        )
        if settings.DEBUG:
            urlpatterns += patterns(
                "",
                url(
                    r"^(?P<path>.*)$",
                    "django.views.static.serve",
                    {
                        "document_root": settings.MEDIA_ROOT,
                    },
                ),
            )
