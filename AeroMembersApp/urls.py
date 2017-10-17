from django.conf.urls import url,include
from django.contrib.auth import views as auth_views


from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^signup/', views.signup, name='signup'),
    url(r'^completesignup/', views.completeSignup, name='completesignup'),
    url(r'^companyregistration/', views.companyRegistration, name='companyregistration'),
    url(r'^editprofile/', views.editProfile, name='editprofile'),
    #url(r'^completesignup/(?P<backend>)/(?P<username>)/', views.completeSignup, name='completesignup'),
    url(r'^signin/$', views.signin, name='signin'),
    url(r'^oauth/', include('social_django.urls', namespace='social')),
    url(r'^accountsettings/$', views.accountSettings, name='accountsettings'),
    url(r'^accountsettings/password/$', views.password, name='password'),
    url(r'^signout/', views.signout, name='signout'),
    url(r'^termsofservice/$', views.termsOfService, name='termsofservice'),
    url(r'^privacy/$', views.privacy, name='privacy'),
    url(r'^forum/$', views.forum, name='forum'),
    url(r'^thread/(?P<thread_id>[0-9]+)/$',views.thread,name='thread'),
    url(r'^createthread/$', views.createThread, name='createthread'),
    url(r'^postreply/$', views.postReply, name='postreply'),
    url(r'^upvotepost/$', views.upvotePost, name='upvotepost'),
    url(r'^ffl/(?P<leagueId>[0-9]+)/(?P<victimTeamId>[0-9]+)/(?P<victimPlayerId>[0-9]+)/(?P<victimPlayerRosterPosition>[0-9]+)/(?P<sourceTeamId>[0-9]+)/(?P<sourcePlayerId>[0-9]+)/(?P<sourcePlayerRosterPosition>[0-9]+)/$',views.ffl,name='ffl'),

]