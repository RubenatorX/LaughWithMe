from django.conf.urls import patterns, url

from mainsite import views

urlpatterns = patterns('',
    url(r'^$', views.WelcomeView, name='WelcomeView'),
)