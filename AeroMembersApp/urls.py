from django.conf.urls import url,include
from django.contrib.auth import views as auth_views


from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^signup/', views.signup, name='signup'),
    url(r'^signin/$', views.signin, name='signin'),
    url(r'^oauth/', include('social_django.urls', namespace='social')),
    url(r'^accountsettings/$', views.accountSettings, name='accountsettings'),
    url(r'^accountsettings/password/$', views.password, name='password'),
    url(r'^signout/', views.signout, name='signout'),
]