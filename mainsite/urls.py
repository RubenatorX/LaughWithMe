from django.conf.urls import patterns, url

from mainsite import views

urlpatterns = patterns('',
    url(r'^$', views.WelcomeView, name='WelcomeView'),
    url(r'^about(/|$)', views.AboutView, name='AboutView'),
    url(r'^register(/|$)', views.RegistrationView, name='RegistrationView'),
)