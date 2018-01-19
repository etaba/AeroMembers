from django.conf.urls import url,include
from django.contrib.auth import views as auth_views


from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^signup/', views.signup, name='signup'),
    url(r'^completesignup/', views.completeSignup, name='completesignup'),
    url(r'^companyregistration/', views.companyRegistration, name='companyregistration'),
    url(r'^editcompany/(?P<companyId>[0-9]+)/$', views.editCompany, name='editcompany'),
    url(r'^viewcompany/(?P<companyId>[0-9]+)/$', views.viewCompany, name='viewcompany'),
    url(r'^viewuser/(?P<username>[0-9a-zA-Z+]+)/$', views.viewUser, name='viewuser'),
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
    url(r'^thread/(?P<threadId>[0-9]+)/$',views.thread,name='thread'),
    url(r'^createthread/$', views.createThread, name='createthread'),
    url(r'^editthread/$', views.editThread, name='editthread'),
    url(r'^upvotecomment/$', views.upvoteComment, name='upvotecomment'),
    url(r'^commenttemplate/$', views.commentTemplate, name='commenttemplate'),
    url(r'^thread/(?P<threadId>[0-9]+)/comments/$',views.comments,name='comments'),
    url(r'^thread/(?P<threadId>[0-9]+)/postcomment/$',views.postComment,name='postcomment'),
    url(r'^thread/(?P<threadId>[0-9]+)/editcomment/$',views.editComment,name='editcomment'),
    url(r'^thread/(?P<threadId>[0-9]+)/deletepost/(?P<postId>[0-9]+)$',views.deletePost,name='deletepost'),
]