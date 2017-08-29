from django.http import HttpResponse
from django.contrib.auth import login, authenticate, update_session_auth_hash, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AdminPasswordChangeForm, PasswordChangeForm
from django.contrib import messages
from forms import *
from social_django.models import UserSocialAuth
from django.forms.formsets import formset_factory
from django.contrib.auth.backends import ModelBackend
#from AeroMembersApp.forms import *

from pprint import pprint

def signin(request):
    return render(request, 'registration/login.html')

def index(request):
    return render(request, 'index.html');

def signup(request):
    #CompanyFormset = formset_factory(CompanyForm, extra = )
    if request.method == 'POST':
        userForm = UserForm(request.POST)
        profileForm = ProfileForm(request.POST)
        contactForm = ContactForm(request.POST)
        if userForm.is_valid() and profileForm.is_valid() and contactForm.is_valid():
            user = User.objects.create_user(userForm.cleaned_data.get('username'),userForm.cleaned_data.get('email'),userForm.cleaned_data.get('password'))
            user.first_name=userForm.cleaned_data.get('first_name')
            user.last_name=userForm.cleaned_data.get('last_name')
            user.save()
            profile = profileForm.save(commit=False)
            profile.user = user
            profile.save()
            contact = contactForm.save(commit=False)
            contact.user = user
            contact.save()
            #user.refresh_from_db()  # load the profile instance created by the signal
            #user.profile.birth_date = userForm.cleaned_data.get('birth_date')
            #user.save()
            user = authenticate(username=user.username, password=userForm.cleaned_data.get('password'))
            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                print "not authed!!\n\n\n\n"

    else:
        userForm = UserForm()
        profileForm = ProfileForm()
        contactForm = ContactForm()

    return render(request, 'registration/signup.html', {'userForm': userForm,
                                                        'profileForm':profileForm,
                                                        'contactForm':contactForm})

@login_required
def accountSettings(request):
    user = request.user

    try:
        linkedin_login = user.social_auth.get(provider='linkedin-oauth2')
        #pprint(linkedin_login.get_username())
        #pprint(linkedin_login.social_details)
    except UserSocialAuth.DoesNotExist:
        linkedin_login = None

    try:
        facebook_login = user.social_auth.get(provider='facebook')
        pprint(facebook_login.extra_data)
    except UserSocialAuth.DoesNotExist:
        facebook_login = None

    return render(request, 'registration/accountSettings.html', {
    	'linkedin_login': linkedin_login,
        'facebook_login': facebook_login,
    })

@login_required
def password(request):
    fbTest = request.user.social_auth.get(provider='facebook')
    print 'social_details:'
    pprint(fbTest.social_details)
    print 'get_username:'
    pprint(fbTest.get_username())
    print 'extra_data:'
    pprint(fbTest.extra_data)
    print 'user_details:'
    pprint(fbTest.user_details)
    if request.user.has_usable_password():
        PasswordForm = PasswordChangeForm
    else:
        PasswordForm = AdminPasswordChangeForm

    if request.method == 'POST':
        form = PasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('index')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordForm(request.user)
    return render(request, 'registration/password.html', {'form': form})

def termsOfService(request):
    return render(request, 'termsOfService.html');

def privacy(request):
    return render(request, 'privacy.html');

def signout(request):
    logout(request)
    return render(request, 'index.html');
