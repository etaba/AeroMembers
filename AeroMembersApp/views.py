from django.http import HttpResponse
from django.contrib.auth import login, authenticate, update_session_auth_hash, logout
from django.shortcuts import render, redirect, reverse, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AdminPasswordChangeForm, PasswordChangeForm
from django.contrib import messages
from forms import *
from social_django.models import UserSocialAuth
from django.forms.formsets import formset_factory
from django.contrib.auth.backends import ModelBackend
from django.template import RequestContext
from social_django.utils import psa, load_strategy
from pprint import pprint
import json

import pdb



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
def editProfile(request):
    try:
        profile = Profile.objects.get(user=request.user)
    except: 
        profile = Profile(user=request.user)
    try:
        contact = Contact.objects.get(user=request.user)
    except:
        contact = Contact(user=request.user)
    if request.method == 'POST':
        userForm = UserFormWithoutPassword(request.POST,instance=request.user)
        profileForm = ProfileForm(request.POST,instance=profile)
        contactForm = ContactForm(request.POST,instance=contact)
        if userForm.is_valid() and profileForm.is_valid() and contactForm.is_valid():
            userForm.save()
            profileForm.save()
            contactForm.save()
            return redirect('index')
        else:
            print userForm._errors
    else:
        userForm = UserFormWithoutPassword(instance=request.user)
        profileForm = ProfileForm(instance=profile)
        contactForm = ContactForm(instance=contact)

    return render(request, 'registration/editprofile.html', {'userForm': userForm,
                                                        'profileForm':profileForm,
                                                        'contactForm':contactForm,})

@login_required
def companyRegistration(request):
    if request.method == 'POST':
        companyForm = CompanyForm(request.POST)
        if companyForm.is_valid():
            company = companyForm.save()
            cu = CompanyUser(user=request.user,company=company,is_admin=True)
            cu.save()
            return redirect('index')
    else:
        companyForm = CompanyForm()
        return render(request, 'registration/companyregistration.html',{'companyForm':companyForm})

def completeSignup(request):
    if request.method == 'POST':
        print 'here'
        #user already created by social pipeline
        user = User.objects.get(username=request.POST['username'])
        userForm = UserForm(request.POST, instance=user)
        profileForm = ProfileForm(request.POST)
        contactForm = ContactForm(request.POST)
        if userForm.is_valid():
            print 'here!?!?!'
            userForm.save()
            user.set_password(userForm.cleaned_data.get('password'))
            user.save()
            profile = profileForm.save(commit=False)
            profile.user = user
            profile.save()
            contact = contactForm.save(commit=False)
            contact.user = user
            contact.save()
            return redirect(reverse('social:complete', args=[request.session['backend']]))
        else:
            print "not valid..."
            return render(request, 'registration/signup.html', {'userForm': userForm,
                                                            'profileForm':profileForm,
                                                            'contactForm':contactForm,
                                                            'backend':request.session['backend']})
    else:
        username = request.GET.get('username')
        backend = request.GET.get('backend')
        request.session['backend'] = backend
        user = User.objects.get(username=username)
        user.password = ""
        userForm = UserForm(instance=user)
        profileForm = ProfileForm()
        contactForm = ContactForm()
        return render(request, 'registration/signup.html', {'userForm': userForm,
                                                            'profileForm':profileForm,
                                                            'contactForm':contactForm,
                                                            'backend':backend})

@login_required
def accountSettings(request):
    user = request.user

    try:
        linkedin_login = user.social_auth.get(provider='linkedin-oauth2')
    except UserSocialAuth.DoesNotExist:
        linkedin_login = None

    try:
        facebook_login = user.social_auth.get(provider='facebook')
    except UserSocialAuth.DoesNotExist:
        facebook_login = None

    try:
        google_login = user.social_auth.get(provider='google-oauth2')
    except UserSocialAuth.DoesNotExist:
        google_login = None

    can_disconnect = (user.social_auth.count() > 1 or user.has_usable_password())

    return render(request, 'registration/accountSettings.html', {
    	'linkedin_login': linkedin_login,
        'facebook_login': facebook_login,
        'google_login' : google_login,
        'can_disconnect': can_disconnect
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

def forum(request):
    threads = Thread.objects.order_by('createdOn')
    return render(request, 'forum.html',{'threads':threads})

def thread(request,thread_id):
    try:
        thread = Thread.objects.get(pk=thread_id)
    except Thread.DoesNotExist:
        raise Http404("Thread does not exist")
    if request.method == 'POST' and request.user.is_authenticated:
        threadReplyForm = ThreadReplyForm(request.POST)
        if threadReplyForm.is_valid():
            post = threadReplyForm.save(commit=False)
            post.parent = thread
            post.createdBy = request.user
            post.save()
            thread.refresh_from_db()
    flattenedThread = thread.flattenReplies(-1)
    for flatReply in flattenedThread:
        if len(UserUpvote.objects.filter(user=request.user,postId=flatReply['reply'].pk))>0:
            flatReply['scoreClass'] = "upvoted"
        else:
            flatReply['scoreClass'] = ""
    if len(UserUpvote.objects.filter(user=request.user,postId=thread.pk))>0:
        threadScoreClass = "upvoted"
    else:
        threadScoreClass = ""
    threadReplyForm = ThreadReplyForm()
    return render(request, 'thread.html', {'thread':thread,
                                            'threadScoreClass':threadScoreClass,
                                            'flattenedReplies':flattenedThread[1:],
                                            'threadReplyForm':threadReplyForm})

@login_required
def createThread(request):
    if request.method=='POST':
        threadForm = ThreadForm(request.POST)
        if threadForm.is_valid():
            thread = threadForm.save(commit=False)
            thread.createdBy = request.user
            thread.save();
            return redirect(reverse('thread',kwargs={'thread_id':thread.id}))
        else:
            return render(request,'createThread.html',{'threadForm':threadForm})
    else:
        threadForm = ThreadForm()
        return render(request,'createThread.html',{'threadForm':threadForm})

@login_required
def postReply(request):
    post = Post(parent=Post.objects.get(pk=request.POST['postId']),
                content=request.POST['replyContent'],
                createdBy=request.user)
    post.save()
    return redirect(reverse('thread',kwargs={'thread_id':request.POST['threadId']}))

@login_required
def upvotePost(request):
    postData = json.loads(request.body)
    #pprint("POST ID: "+str(request.POST['postId'])) 
    userUpvote = UserUpvote(user=request.user,postId=postData['postId'])
    userUpvote.save()
    post = Post.objects.get(pk=postData['postId'])
    post.score += 1
    post.save()
    return HttpResponse()

def termsOfService(request):
    return render(request, 'termsOfService.html');

def privacy(request):
    return render(request, 'privacy.html');

@login_required
def signout(request):
    logout(request)
    return render(request, 'index.html');

#jj nelson for taylors terrance west
#/1210475/4/16783/20/8/17514/20
def ffl(request,leagueId,victimTeamId,victimPlayerId,victimPlayerRosterPosition,sourceTeamId,sourcePlayerId,sourcePlayerRosterPosition):
    url = "games.espn.com/ffl/tradereview?leagueId="+leagueId+"&teamId=-2147483648&batchId=39"
    transaction = "4_{0}_{1}_{2}_{3}_20|4_{4}_{3}_{5}_{1}_20".format(str(victimPlayerId),str(victimTeamId),str(victimPlayerRosterPosition),str(sourceTeamId),str(sourcePlayerId),str(sourcePlayerRosterPosition))
    html = '<html><form enctype="application/x-www-form-urlencoded" method="POST" action="http://'+url+'"><table><tr><td>incoming</td><td><input type="text" value="1" name="incoming"></td></tr>\
<tr><td>trans</td><td><input type="text" value="'+transaction+'" name="trans"></td></tr>\
<tr><td>accept</td><td><input type="text" value="1" name="accept"></td></tr>\
<tr><td></td><td><input type="text" value="0" name="dealbreaker_'+str(sourcePlayerId)+'"></td></tr>\
<tr><td></td><td><input type="text" value="0" name="dealbreaker_'+str(victimPlayerId)+'"></td></tr>\
<tr><td>overallRating</td><td><input type="text" value="" name="overallRating"></td></tr>\
<tr><td>mailText</td><td><input type="text" value="" name="mailText"></td></tr>\
<tr><td>sendMail</td><td><input type="text" value="0" name="sendMail"></td></tr>\
<tr><td>proposeTradeTo</td><td><input type="text" value="-1" name="proposeTradeTo"></td></tr>\
</table><input type="submit" value="'+url+'"></form></html>'
    return HttpResponse(html)

