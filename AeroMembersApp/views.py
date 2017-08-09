from django.http import HttpResponse
from django.contrib.auth import login, authenticate, update_session_auth_hash, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AdminPasswordChangeForm, PasswordChangeForm
from django.contrib import messages
from forms import SignUpForm
from social_django.models import UserSocialAuth

from pprint import pprint

def signin(request):
    return render(request, 'registration/login.html')

def index(request):
    return render(request, 'index.html');

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.profile.birth_date = form.cleaned_data.get('birth_date')
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

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

def signout(request):
    logout(request)
    return render(request, 'index.html');
