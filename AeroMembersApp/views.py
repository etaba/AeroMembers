from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login, authenticate, update_session_auth_hash, logout
from django.shortcuts import render, redirect, reverse, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.contrib import messages
from django.forms.models import model_to_dict
from AeroMembersApp.forms import *
from social_django.models import UserSocialAuth
import json, braintree
from datetime import datetime
import os

BRAINTREE_MERCHANT_ID = "5vgz24sws5f9jw2k"
BRAINTREE_PUBLIC_KEY = "2422g8bt255hpqdf"
BRAINTREE_PRIVATE_KEY = os.environ.get('BRAINTREE_SECRET_KEY')

def signin(request):
    context = {}
    if request.method == 'POST':
        #userForm = SigninForm(request.POST)
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            login(request, user)
            request.session['companies'] = list(CompanyUser.objects.filter(user=user).values('company'))
            if len(request.session['companies']) == 1:
                request.session['currCompany'] = model_to_dict(request.session['companies'][0])
            activeUserPlan = Subscription.objects.filter(user=user,status="Active",plan__type="USER")
            if activeUserPlan.exists():
                request.session['userPlan'] = model_to_dict(activeUserPlan.get().plan)
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
            return redirect('managecompanyplan')
        else:
            return render(request, 'registration/companyregistration.html',{'companyForm':companyForm})
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
    if UserUpvote.objects.filter(user=request.user,postId=thread.pk).exists():
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
            if UserUpvote.objects.filter(user=request.user,postId=comment['id']).exists():
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
    #data = json.dumps(data, cls=DjangoJSONEncoder)
    #return HttpResponse(data, content_type='application/json')
    return JsonResponse(data)

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
    if contact.exists():
        context['contact'] = contact.get()
    profile = Profile.objects.filter(user=user)
    if profile.exists():
        context['private'] = profile.get().private
    companies = map(lambda uc: uc.company, CompanyUser.objects.filter(user=user))
    context['companies'] = companies
    return render(request, 'viewUser.html',context);

@login_required
def checkout(request):
    gateway = braintree.BraintreeGateway(
        braintree.Configuration(
            braintree.Environment.Sandbox,
            merchant_id=BRAINTREE_MERCHANT_ID,
            public_key=BRAINTREE_PUBLIC_KEY,
            private_key=BRAINTREE_PRIVATE_KEY
        )
    )
    if request.method == "GET":
        #try:
        #    customer = gateway.customer.find(str(request.user.pk))
        #    context['paymentMethods'] = {'creditCards':[],'paypal':[],'applepay':[],'androidpay':[]}
        #    for pm in customer.payment_methods:
        #        if pm.__class__ == braintree.credit_card.CreditCard:
        #            context['paymentMethods']['creditCards'].append(pm)
        #        if pm.__class__ == braintree.paypal_account.PayPalAccount:
        #            context['paymentMethods']['paypal'].append(pm)
        #except braintree.exceptions.unexpected_error.UnexpectedError:
        #    pass
        return render(request, 'checkout.html')
    elif request.method == "POST":
        postData = json.loads(request.body)
        paymentNonce = postData.get('paymentNonce',None)
        if paymentNonce == None:
            raise Http404("Braintree payment nonce not received")
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
                raise Http404(customer.error)
        #retrieve order
        orderQ = Order.objects.filter(requestingUser=request.user,status="O")
        if not orderQ.exists():
            raise Http404("No open orders found for user.")
        else:
            order = orderQ.get()

        #regular resource items
        total = sum([o.price for o in order.orderLines])
        result = gateway.transaction.sale({  
            "amount": str(total),
            "payment_method_nonce": paymentNonce,
            "options": {
              "submit_for_settlement": True
            }})
        if result.is_success:
            #TODO: attach transaction id?
            #TODO: process purchase here: start download, associate item with user, etc
            pass
        else:
            for error in result.errors.deep_errors:
                print(error.attribute)
                print(error.code)
                print(error.message)
            raise Http404(result.errors.deep_errors)
        #TODO: return transaction id or redirect to confirmation page
        return HttpResponse("Payment success")

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

'''def getPaymentMethods(request):
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
    return HttpResponse(json.dumps(paymentMethods))'''

@login_required
def getOrder(request):
    #get open order
    orderLines = OrderLine.objects.filter(order__requestingUser=request.user,order__status="O")
    if orderLines.exists():
        response = list(orderLines.values('pk','item__name','item__type','item__description','price','discount__rate'))
    else:
        response = []
    return HttpResponse(json.dumps(response))

# def getInactiveSubscription(request):
#     sub = Subscription.objects.filter(user=request.user,status="inactive")
#     if sub.exists():
#         response = list(sub.values('pk','plan__name','plan__description','plan__monthlyRate','discount__rate'))
#     else:
#         response = []
#     return HttpResponse(json.dumps(response))

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

@login_required
def subscribe(request):
    if request.method == 'GET':
        plans = Plan.objects.filter(type='USER')
        context = {"plans":plans}
        #retrieve active user subscriptions
        activeSub = Subscription.objects.filter(user=request.user,status="O",plan__type="USER")
        if activeSub.exists():
            context["activePlan"] = activeSub.plan
        return render(request,'subscribe.html',context)

@login_required
def manageCompanyPlan(request):
    if request.method == 'GET':
        plans = Plan.objects.filter(type='COMPANY')
        return render(request,'manageplan.html',{"plans":plans})

@login_required
def selectPlan(request):
    if request.method == 'POST':
        postData = json.loads(request.body)
        request.session['selectedPlan'] = postData['plan']
    return HttpResponse()

@login_required
def getPlan(request,planId):
    plan = Plan.objects.get(pk=planId)
    #response = list(plan.values('pk','name','description','monthlyRate'))
    #data = json.dumps(plan, cls=DjangoJSONEncoder)
    return JsonResponse(model_to_dict(plan))

@login_required
def subscriptionCheckout(request):
    gateway = braintree.BraintreeGateway(
        braintree.Configuration(
            braintree.Environment.Sandbox,
            merchant_id=BRAINTREE_MERCHANT_ID,
            public_key=BRAINTREE_PUBLIC_KEY,
            private_key=BRAINTREE_PRIVATE_KEY
        ))
    postData = json.loads(request.body)
    paymentNonce = postData.get('paymentNonce',None)
    plan = Plan.objects.get(pk=postData['planId'])
    if paymentNonce == None:
        raise Http404("Braintree payment nonce not received")
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
            raise Http404(customer.error)

    #membership/recurring payment order
    subscription = {
        "payment_method_token": customer.payment_methods[0].token,
        "plan_id": plan.braintreeID,
    }
    if 'discountCode' in postData.keys():
        discount = Discount.objects.get(code=postData['discountCode'])
        if discount != None:
            subscription['discounts'] = {'add':[{'inherited_from_id':discount.braintreeID}]}

    #TODO: deal with preexisting or coexisting memberships

    result = gateway.subscription.create(subscription)
    import pdb; pdb.set_trace()
    if result.is_success:
        activeSub = Subscription.objects.filter(user=request.user,status="Active",plan__type="USER")
        #if item is membership, delete any existing active order. memberships should be only lines on an order
        if activeSub.exists():
            activeSub.delete()
        newSub = Subscription(user=request.user, plan=plan, status='Active', braintreeID=result.subscription.id)
        newSub.save()
        request.session['userPlan'] = model_to_dict(plan)
        #TODO: log transaction detials? send order confirmation?
    else:
        for error in result.errors.deep_errors:
            print(error.attribute)
            print(error.code)
            print(error.message)
        raise Http404(result.errors.deep_errors)

    #TODO: return transaction id or redirect to confirmation page
    return HttpResponse("Payment success")

def addOrderLine(request):
    if request.method == 'POST':
        postData = json.loads(request.body)
        item = Item.objects.get(pk=postData['item'])
        activeOrder = Order.objects.filter(requestingUser=request.user,status="O")

        if item.type == 'CM' or item.type == 'UM':
            #if item is membership, delete any existing active order. memberships should be only lines on an order
            if activeOrder.exists():
                activeOrder.delete()
            #create new order
            newOrder = Order(requestingUser=request.user, type="R")
            newOrder.save()
            orderLine = OrderLine(item=item,order=newOrder,price=item.price)
            orderLine.save()
        else:
            #regular items can be appended to existing orders, so long as existing order doesnt have a membership item
            if not activeOrder.exists():
                activeOrder = Order(requestingUser=request.user, type="S")
                activeOrder.save()
            elif activeOrder.get().type == "R":
                #existing recurring order with membership exists and must be deleted
                activeOrder.delete()
                activeOrder = Order(requestingUser=request.user, type="S")
                activeOrder.save()
            else:
                #item can be appended as orderline to existing order
                activeOrder = activeOrder.get()

            if not OrderLine.objects.filter(order=activeOrder,item=item).exists():
                #item does not exist on order, so add it
                orderLine = OrderLine(item=item,order=newOrder,price=item.price)
                orderLine.save()
    return HttpResponse()

def cancelOrderLine(request):
    if request.method == 'POST':
        postData = json.loads(request.body)
        orderLine = OrderLine.objects.get(pk=postData['orderLine'])
        if orderLine.order.requestingUser == request.user:
            orderLine.delete()
            return getOrder(request)
        else:
            return Http404("could not cancel order "+postData['order'])

#discounts only apply to recurring payments, as per braintree's functionality
#aeromember discount objects are each single use, and map to a braintree discount
def applyDiscount(request):
    postData = json.loads(request.body)
    discountCode = postData['discountCode']
    discount = Discount.objects.get(code=discountCode)
    if discount.active and discount.expiration >= datetime.now().date():
        return HttpResponse(discount.rate)
    else:
        return Http404("Invalid Discount Code")


def googleVerification(request):
    return render(request,"google25f6029237164a78.html")


@login_required
def signout(request):
    logout(request)
    return render(request, 'index.html');


