from django.conf.urls import include
from django.urls import path


from . import views

urlpatterns = [
    path('', views.index,name='index'),
    path('signup/', views.signup),
    path('completesignup/', views.completeSignup,name='completeSignup'),
    path('companyregistration/', views.companyRegistration),
    path('editcompany/<int:companyId>/', views.editCompany),
    path('viewcompany/<int:companyId>', views.viewCompany, name='viewcompany'),
    path('setcompany/<int:companyId>', views.setCompany),
    path('setcompany/', views.setCompany),
    path('viewuser/<int:userId>', views.viewUser),
    path('editprofile/', views.editProfile),
    path('completesignup/<str:backend>/<str:username>/', views.completeSignup),
    path('signin/', views.signin,name='signin'),
    path('oauth/', include('social_django.urls', namespace='social')),
    path('accountsettings/', views.accountSettings),
    path('accountsettings/password/', views.password, name='password'),
    path('signout/', views.signout),
    path('termsofservice/', views.termsOfService),
    path('privacy/', views.privacy),
    path('forum/', views.forum),
    path('thread/<int:threadId>/',views.thread,name='thread'),
    path('createthread/', views.createThread),
    path('editthread/', views.editThread),
    path('upvotecomment/', views.upvoteComment),
    path('commenttemplate/', views.commentTemplate),
    path('thread/<int:threadId>/comments/',views.comments),
    path('thread/<int:threadId>/postcomment/',views.postComment),
    path('thread/<int:threadId>/editcomment/',views.editComment),
    path('thread/<int:threadId>/deletepost/<int:postId>',views.deletePost),
    path('clienttoken/', views.clientToken),
    path('checkout/', views.checkout),   
    path('addorderline/', views.addOrderLine),
    path('getorder/', views.getOrder),
    path('addpaymentmethod/', views.addPaymentMethod),
    path('manageplan/', views.managePlan),
    path('managecompanyplan/',views.manageCompanyPlan, name='managecompanyplan'),
    path('applydiscount/', views.applyDiscount),
    path('cancelorderline/', views.cancelOrderLine),
    path('createsubscription/',views.createSubscription),
    path('subscriptioncheckout/',views.subscriptionCheckout),
    path('getinactivesubscription/',views.getInactiveSubscription)
]