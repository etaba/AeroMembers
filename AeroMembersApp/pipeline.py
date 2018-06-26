from social_core.pipeline.partial import partial
from django.contrib.sessions.backends.db import SessionStore
from django.forms.models import model_to_dict
from AeroMembersApp.models import *

@partial
def complete_profile(strategy, backend, user, request, details, *args, **kwargs):
    if (user.username and user.email and user.first_name and user.last_name):
        #user is all set to go, complete social pipeline
        return
    else:
        #try to get needed data from social api
        username = strategy.request_data().get('username')
        email = strategy.request_data().get('email')
        first_name = strategy.request_data().get('first_name')
        last_name = strategy.request_data().get('last_name')
        if username:
            details['username']=username
        if email:
            details['email']=email
        if first_name:
            details['first_name']=first_name
        if last_name:
            details['last_name']=last_name
        if (username and email and first_name and last_name):
            #all needed fields filled with social API
            return
        else:
            #must prompt user for missing fields
            current_partial = kwargs.get('current_partial')
            return strategy.redirect('/completesignup?username={0}&backend={1}'.format(user.username,current_partial.backend))

def set_session(user,request, *args, **kwargs):
    request.session['companies'] = list(CompanyUser.objects.filter(user=user).values('company'))
    if len(request.session['companies']) == 1:
        request.session['currCompany'] = model_to_dict(request.session['companies'][0])
    activeUserPlan = Subscription.objects.filter(user=user,status="Active",plan__type="USER")
    if activeUserPlan.exists():
        request.session['userPlan'] = model_to_dict(activeUserPlan.get().plan)
    return