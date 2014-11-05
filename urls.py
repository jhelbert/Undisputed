from django.conf.urls.defaults import patterns, include, url
from django.conf.urls.defaults import *
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    # Uncomment the next line to enable the admin:
    url(r'^udadmin/', include(admin.site.urls)),
    url(r'player/','main.views.player'),
    url(r'incoming_text','main.views.incoming_text'),
    url(r'^$','main.views.home')
)
