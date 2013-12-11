from django.conf.urls import patterns, url
from mainsite import views
from axes.decorators import watch_login

urlpatterns = patterns('',
    url(r'^$', views.WelcomeView, name='WelcomeView'),
    url(r'^about(/|$)', views.AboutView, name='AboutView'),
    url(r'^register(/|$)', views.RegistrationView, name='RegistrationView'),
    url(r'^login(/|$)', watch_login(views.LoginView), name='LoginView'),
    url(r'^logout(/|$)', views.LogoutView, name='LogoutView'),
    url(r'^newPost(/|$)', views.NewPostView, name='NewPostView'),
    url(r'^myposts(/|$)', views.MyPostsView, name='MyPostsView'),
)
