from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^polls/', include('polls.urls', namespace="polls")),
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('mainsite.urls', namespace="mainsite")),
    #url(r'^[a-zA-Z_0-9-]*(/|$)', include('mainsite.urls', namespace="mainsite")),
)

    # Examples:
    # url(r'^$', 'lolTrueStory.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

