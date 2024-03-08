"""
This file contains all the urls used for roster pulse project
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("EbszxOwABPM0qn/superuser/", admin.site.urls),
    path("users/", include("users.urls")),
    path("rosters/", include("rosters.urls")),
    path("attendance/", include("attendance.urls")),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
