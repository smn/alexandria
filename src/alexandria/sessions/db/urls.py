from django.conf.urls.defaults import *
from django.conf import settings
from alexandria.sessions.db import views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^dashboards/', include('dashboards.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    
    (r'^stats/static/(.*)$', 'django.views.static.serve', \
                            {'document_root': settings.MEDIA_ROOT}, "static"),
    
    
    # Uncomment the next line to enable the admin:
    (r'^stats/admin/', include(admin.site.urls)),
    (r'^stats/data.js', views.json),
    (r'^stats/$', views.home)
)
