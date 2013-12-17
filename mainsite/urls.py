from django.conf.urls import patterns, url
from mainsite import views
from axes.decorators import watch_login

urlpatterns = patterns('',
    url(r'^$', views.WelcomeView, name='WelcomeView'),
    url(r'^about(/|$)', views.AboutView, name='AboutView'),
    url(r'^register(/|$)', views.RegistrationView, name='RegistrationView'),
    url(r'^login(/|$)', watch_login(views.LoginView), name='LoginView'),
    url(r'^logout(/|$)', views.LogoutView, name='LogoutView'),
    url(r'^newpost(/|$)', views.NewPostView, name='NewPostView'),
    url(r'^myposts(/|$)', views.MyPostsView, name='MyPostsView'),
    url(r'^user/(\w+)', views.PersonView, name='PersonView'),
    url(r'^post/(\d+)', views.PostView, name='PostView'),
    url(r'^settings(/|$)', views.SettingsView, name='SettingsView'),
    url(r'^favorites(/|$)', views.FavoritesView, name='FavoritesView'),
    url(r'^trending(/|$)', views.TrendingView, name='TrendingView')
    url(r'^myactivity(/|$)', views.MyActivityView, name='MyActivityView')
)
