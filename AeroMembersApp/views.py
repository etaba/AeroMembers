from django.http import HttpResponse
from django.contrib.auth import login, authenticate, update_session_auth_hash, logout
from django.shortcuts import render, redirect, reverse, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.contrib import messages
from AeroMembersApp.forms import *
from social_django.models import UserSocialAuth
from django.core.serializers.json import DjangoJSONEncoder
from pprint import pprint
import json
import braintree

BRAINTREE_MERCHANT_ID = "5vgz24sws5f9jw2k"
BRAINTREE_PUBLIC_KEY = "2wcngqdvwszvfyq7"
BRAINTREE_PRIVATE_KEY = "ee32c1d473e2cabe312a2d1c9b9ec89e"

def signin(request):
    context = {}
    if request.method == 'POST':
        #userForm = SigninForm(request.POST)
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            login(request, user)
            companies = CompanyUser.objects.filter(user=user)
            if len(companies) == 1:
                request.session['currCompanyId'] = companies[0].company.pk
            return redirect('index')
        else:
            context = {'error':"Invalid Credentials"}
            userForm = SigninForm()
    else:           
        userForm = SigninForm()

    context['userForm'] = userForm
    return render(request, 'registration/signin.html',context)

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
            print(userForm._errors)
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

def viewCompany(request,companyId):
    company  = Company.objects.get(pk=companyId)
    companyUser = CompanyUser.objects.filter(company=company,user=request.user)
    isAdmin = companyUser.get().is_admin if companyUser else False
    return render(request, 'viewCompany.html',{'company':company,'isAdmin':isAdmin})

def setCompany(request,companyId=None):
    if companyId == None:
        request.session['currCompanyId'] = None
    else:
        request.session['currCompanyId'] = companyId
    return redirect('index')

@login_required
def editCompany(request,companyId):
    company = Company.objects.get(pk=companyId)
    companyUser = CompanyUser.objects.get(company=company,user=request.user)
    if not companyUser or not companyUser.is_admin:
        return Http404()
    else:
        if request.method == 'POST':
            companyForm = CompanyForm(request.POST,instance=company)
            if companyForm.is_valid():
                companyForm.save()
            return redirect(reverse('viewcompany',kwargs={'companyId':companyId}))

        else:
            companyForm = CompanyForm(instance=company)
            return render(request, 'registration/editCompany.html',{'companyForm':companyForm,'companyId':companyId})


def completeSignup(request):
    if request.method == 'POST':
        #user already created by social pipeline
        user = User.objects.get(username=request.POST['username'])
        userForm = UserForm(request.POST, instance=user)
        profileForm = ProfileForm(request.POST)
        contactForm = ContactForm(request.POST)
        if userForm.is_valid():
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
        PasswordForm = FancyPasswordChangeForm
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

def thread(request,threadId):
    try:
        thread = Thread.objects.get(pk=threadId)
    except Thread.DoesNotExist:
        raise Http404("Thread does not exist")
    if request.method == 'POST' and request.user.is_authenticated:
        threadCommentForm = ThreadCommentForm(request.POST)
        if threadCommentForm.is_valid():
            post = threadCommentForm.save(commit=False)
            post.parent = thread
            post.createdBy = request.user
            post.save()
            thread.refresh_from_db()
    if len(UserUpvote.objects.filter(user=request.user,postId=thread.pk))>0:
        threadScoreClass = "upvoted"
    else:
        threadScoreClass = ""
    threadCommentForm = ThreadCommentForm()
    return render(request, 'thread.html', {'thread':thread,
                                            'threadScoreClass':threadScoreClass,
                                            'threadCommentForm':threadCommentForm})

def comments(request,threadId):
    try:
        thread = Thread.objects.get(pk=threadId)
        threadJSON = thread.getComments()
        for comment in threadJSON['comments']:
            if len(UserUpvote.objects.filter(user=request.user,postId=comment['id']))>0:
                comment['scoreClass'] = "upvoted"
            else:
                comment['scoreClass'] = ""
    except Thread.DoesNotExist:
        raise Http404("Thread does not exist")
    data = {
            'comments':threadJSON['comments'],
            'threadId':threadId,
            'user':request.user.username
            }
    data = json.dumps(data, cls=DjangoJSONEncoder)
    return HttpResponse(data, content_type='application/json')

def commentTemplate(request):
    return render(request,'commentTemplate.html')



@login_required
def createThread(request):
    if request.method=='POST':
        threadForm = ThreadForm(request.POST)
        if threadForm.is_valid():
            thread = threadForm.save(commit=False)
            thread.createdBy = request.user
            thread.save();
            return redirect(reverse('thread',kwargs={'threadId':thread.id}))
        else:
            return render(request,'createThread.html',{'threadForm':threadForm})
    else:
        threadForm = ThreadForm()
        return render(request,'createThread.html',{'threadForm':threadForm})

@login_required
def postComment(request,threadId):
    post = Post(parent=Post.objects.get(pk=request.POST['postId']),
                content=request.POST['commentContent'],
                createdBy=request.user)
    post.save()
    return redirect(reverse('thread',kwargs={'threadId':threadId}))

def editComment(request,threadId):
    post = Post.objects.get(pk=request.POST['postId'])
    if post.createdBy == request.user or request.user.is_superuser:
        post.content =  request.POST['commentContent']
    else:
        raise Http404("Cannot edit another user's post")
        return HttpResponse()
    post.save()
    return redirect(reverse('thread',kwargs={'threadId':threadId}))

def editThread(request):
    post = Post.objects.get(pk=request.POST['threadId'])
    if post.createdBy == request.user:
        post.content =  request.POST['threadContent']
    else:
        raise Http404("Cannot edit another user's post")
        return HttpResponse()
    post.save()
    return redirect(reverse('thread',kwargs={'threadId':request.POST['threadId']}))

@login_required
def upvoteComment(request):
    commentData = json.loads(request.body)
    userUpvote = UserUpvote(user=request.user,postId=commentData['commentId'])
    userUpvote.save()
    post = Post.objects.get(pk=commentData['commentId'])
    post.score += 1
    post.save()
    return HttpResponse()

@login_required
def deletePost(request, threadId, postId):
    post = Post.objects.get(pk=postId)
    if post.createdBy == request.user or request.user.is_superuser:
        post.delete()
    else:
        return Http404("Cannot delete another user's post")
    if threadId == postId:
        return redirect(reverse('forum'))
    else:
        return redirect(reverse('thread',kwargs={'threadId':threadId}))

def termsOfService(request):
    return render(request, 'termsOfService.html');

def privacy(request):
    return render(request, 'privacy.html');

def viewUser(request,userId):
    user  = User.objects.get(pk=userId)
    context = {'user':user}
    contact = Contact.objects.filter(user=user)
    if len(contact) > 0:
        context['contact'] = contact.get()
    profile = Profile.objects.filter(user=user)
    if len(profile) > 0:
        context['private'] = profile.get().private
    companies = map(lambda uc: uc.company, CompanyUser.objects.filter(user=user))
    context['companies'] = companies
    return render(request, 'viewUser.html',context);

def checkout(request):
    return render(request, 'checkout.html')

def membershipCheckout(request,plan):
    gateway = braintree.BraintreeGateway(
        braintree.Configuration(
            braintree.Environment.Sandbox,
            merchant_id=BRAINTREE_MERCHANT_ID,
            public_key=BRAINTREE_PUBLIC_KEY,
            private_key=BRAINTREE_PRIVATE_KEY
        )
    )
    if request.method == "GET":
        context = {'plan':plan}
        try:
            customer = gateway.customer.find(str(request.user.pk))
            context['paymentMethods'] = {'creditCards':[],'paypal':[],'applepay':[],'androidpay':[]}
            for pm in customer.payment_methods:
                if pm.__class__ == braintree.credit_card.CreditCard:
                    context['paymentMethods']['creditCards'].append(pm)
                if pm.__class__ == braintree.paypal_account.PayPalAccount:
                    context['paymentMethods']['paypal'].append(pm)
        except braintree.exceptions.unexpected_error.UnexpectedError:
            pass
        return render(request, 'membershipCheckout.html',context)
    elif request.method == "POST":
        postData = json.loads(request.body)
        paymentNonce = postData.get('paymentNonce',None)
        membership = postData.get('membership',None)
        if paymentNonce == None or membership == None:
            return Http404("nonce or membership not received")
        #check if braintree customer already exists
        try:
            customer = gateway.customer.find(str(request.user.pk))
        except braintree.exceptions.not_found_error.NotFoundError:
            phone = request.user.contact.phone if hasattr(request.user,'contact') else ""
            #create braintree customer
            customer = gateway.customer.create({
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "email": request.user.email,
                "phone": phone,
                "id": str(request.user.pk),
                "payment_method_nonce": paymentNonce,
            })
            if not customer.is_success:
                return Http404(customer.error)

        result = gateway.subscription.create({
            "payment_method_token": customer.payment_methods[0].token,
            "plan_id": membership,
        })
        if result.is_success:
            membership = Membership(user=request.user,level=membership)
            membership.save()
        else:
            for error in result.errors.deep_errors:
                print(error.attribute)
                print(error.code)
                print(error.message)
            return Http404(result.errors.deep_errors)
        return redirect(reverse(views.index))

def addPaymentMethod(request):
    if request.method == "POST":
        gateway = braintree.BraintreeGateway(
            braintree.Configuration(
                braintree.Environment.Sandbox,
                merchant_id=BRAINTREE_MERCHANT_ID,
                public_key=BRAINTREE_PUBLIC_KEY,
                private_key=BRAINTREE_PRIVATE_KEY
            )
        )
        postData = json.loads(request.body)
        paymentNonce = postData.get('paymentNonce',None)
        if paymentNonce == None:
            return Http404("nonce not received")
        #check if braintree customer already exists
        try:
            customer = gateway.customer.find(str(request.user.pk))
        except braintree.exceptions.not_found_error.NotFoundError:
            phone = request.user.contact.phone if hasattr(request.user,'contact') else ""
            #create braintree customer
            customer = gateway.customer.create({
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "email": request.user.email,
                "phone": phone,
                "id": str(request.user.pk),
                "payment_method_nonce": paymentNonce,
            })
            if not customer.is_success:
                return Http404(customer.error)
        #add payment method
        result = gateway.payment_method.create({
            "customer_id": str(request.user.pk),
            "payment_method_nonce": paymentNonce
        })
        if result.is_success:
            paymentMethod = {}
            if result.payment_method.__class__ == braintree.credit_card.CreditCard:
                cc = {
                    "type":result.payment_method.card_type,
                    "nameOnCard":result.payment_method.cardholder_name,
                    "last4":result.payment_method.last_4,
                    "expDate":"{}/{}".format(result.payment_method.expiration_month,result.payment_method.expiration_year[-2:]),
                    "token":result.payment_method.token
                }
                paymentMethod["creditCard"] = cc
            if result.payment_method.__class__ == braintree.paypal_account.PayPalAccount:
                paymentMethod['paypal'] = result.payment_method
            return HttpResponse(json.dumps(paymentMethod))

def getPaymentMethods(request):
    gateway = braintree.BraintreeGateway(
        braintree.Configuration(
            braintree.Environment.Sandbox,
            merchant_id=BRAINTREE_MERCHANT_ID,
            public_key=BRAINTREE_PUBLIC_KEY,
            private_key=BRAINTREE_PRIVATE_KEY
        )
    )
    try:
        customer = gateway.customer.find(str(request.user.pk))
        paymentMethods = {'creditCard':[],'paypal':[],'applepay':[],'androidpay':[]}
        for pm in customer.payment_methods:
            if pm.__class__ == braintree.credit_card.CreditCard:
                cc = {
                    "type":pm.card_type,
                    "nameOnCard":pm.cardholder_name,
                    "last4":pm.last_4,
                    "expDate":"{}/{}".format(pm.expiration_month,pm.expiration_year[-2:]),
                    "token":pm.token
                }
                paymentMethods['creditCard'].append(cc)
            if pm.__class__ == braintree.paypal_account.PayPalAccount:
                paymentMethods['paypal'].append(pm)
    except braintree.exceptions.unexpected_error.UnexpectedError:
        pass
    return HttpResponse(json.dumps(paymentMethods))

def clientToken(request):
    gateway = braintree.BraintreeGateway(
        braintree.Configuration(
            braintree.Environment.Sandbox,
            merchant_id=BRAINTREE_MERCHANT_ID,
            public_key=BRAINTREE_PUBLIC_KEY,
            private_key=BRAINTREE_PRIVATE_KEY
        )
    )
    try:
        customer = gateway.customer.find(str(request.user.pk))
        token = gateway.client_token.generate({"customer_id":str(request.user.pk)})
    except braintree.exceptions.not_found_error.NotFoundError:
        token = gateway.client_token.generate()
    return HttpResponse(token)

def payment(request):
    paymentNonce = request.POST['paymentNonce']
    result = gateway.transaction.sale({
        "amount": "10.00",
        "payment_method_nonce": paymentNonce,
        "options": {
          "submit_for_settlement": True
        }
})

def managePlan(request):
    return render(request,'manageplan.html')

@login_required
def signout(request):
    logout(request)
    return render(request, 'index.html');


