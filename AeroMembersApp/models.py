from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey,GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from pprint import pprint

User._meta.get_field('email')._unique = True
User._meta.get_field('email')._null = False


INDUSTRY_CHOICES = (
    ("Accommodation and Food Services","Accommodation and Food Services"),
    ("Administrative and Support and Waste Management and Remediation Services","Administrative and Support and Waste Management and Remediation Services"),
    ("Agriculture, Forestry, Fishing and Hunting","Agriculture, Forestry, Fishing and Hunting"),
    ("Arts, Entertainment, and Recreation","Arts, Entertainment, and Recreation"),
    ("Construction","Construction"),
    ("Educational Services","Educational Services"),
    ("Finance and Insurance","Finance and Insurance"),
    ("Health Care and Social Assistance","Health Care and Social Assistance"),
    ("Information","Information"),
    ("Management of Companies and Enterprises","Management of Companies and Enterprises"),
    ("Mining, Quarrying, and Oil and Gas Extraction","Mining, Quarrying, and Oil and Gas Extraction"),
    ("Other Services (except Public Administration)","Other Services (except Public Administration)"),
    ("Professional, Scientific, and Technical Services","Professional, Scientific, and Technical Services"),
    ("Public Administration","Public Administration"),
    ("Real Estate and Rental and Leasing","Real Estate and Rental and Leasing"),
    ("Utilities","Utilities"),
    ("Wholesale Trade","Wholesale Trade"),
)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='profile', unique=True)
        #User has:
            #username
            #first_name
            #last_name
            #email
            #password
            #groups (many to many)
            #user_permissions
            #is_staff (can access admin site)
            #is_active
            #is_superuser (all permissions without explicitly assigning them)
            #last_login
            #date_joined
    birthdate = models.DateTimeField('date of birth', null=True, blank = True, help_text="Will not be visible to other users.")
    private = models.BooleanField(help_text="Keep personal information hidden from other users. Only your username will be visible.",default=False)

    def __repr__(self):
        return '%s %s' % (self.user.first_name, self.user.last_name)

class Contact(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='contact', unique=True, null=True)
    company = models.OneToOneField('Company',on_delete=models.CASCADE,related_name='contact', unique=True, null=True)
    street_address = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=200, blank=True)
    state = models.CharField(max_length=200, blank=True)
    zip_code = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=20, blank=True)

class Resume(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='resume', unique=True)
    #resumeFile = models.FileField(upload_to="resume/File/Directory", blank=True)
    education = models.CharField(max_length=200, blank=True)
    awards = models.TextField(max_length=200, blank=True)
    certifications = models.TextField(max_length=200, blank=True)

class JobDescription(models.Model):
    profile = models.OneToOneField('Profile',related_name='jobDescription', on_delete=models.CASCADE)
    industry = models.CharField(max_length=200, choices=INDUSTRY_CHOICES)
    job_title = models.CharField(max_length=200)
    salary = models.IntegerField(blank=True, help_text="Will not be visible to other users.")
    start_date = models.DateTimeField('start date')
    end_date = models.DateTimeField('end date')

class CompanyUser(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    company = models.ForeignKey('Company',on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)
    class Meta:
        unique_together = ("user","company")

class Company(models.Model):
    ACTIVITY_TYPE = [
        ("CM","Contract Management"),
        ("DES","Design"),
        ("ENG","Engineering"),
        ("FM","Facility Management"),
        ("GM","General Management"),
        ("HR","Human Resources"),
        ("IT","IT"),
        ("ME","Manufacturing Engineering"),
        ("MKT","Marketing"),
        ("OP","Operations"),
        ("PLN","Planning"),
        ("PROD","Production"),
        ("PRCH","Purchasing"),
        ("QA","Quality"),
        ("RD","R&D"),
        ("RW","Repair & Warranty"),
        ("SAL","Sales"),
        ("SCM","Supply Chain Management"),
    ]
    name = models.CharField(max_length=200)
    department = models.CharField(max_length=200)
    cage_code = models.CharField(max_length=6, null=True, blank=True)
    number_of_employees = models.IntegerField()
    activity_type = models.CharField(max_length = 200, choices=ACTIVITY_TYPE)
    naics = models.IntegerField()
    description = models.TextField(max_length=1000, blank=True)
    def __repr__(self):
        return self.name

'''
class NAICS(models.Model):
    company = models.ForeignKey('Company', on_delete=models.CASCADE)
    code = models.IntegerField()'''

#maps naics code to industry sector. see naicsSectorTable.sql file which has all mappings ready to load into this table
class SectorMapping(models.Model):
    code = models.IntegerField(unique=True)
    sector = models.CharField(max_length=200)

class Post(models.Model):
    content = models.TextField(max_length=1000)
    score = models.IntegerField(default=0)
    createdOn = models.DateTimeField(default=timezone.now)
    editedOn = models.DateTimeField(default = timezone.now)
    createdBy = models.ForeignKey(User,models.DO_NOTHING)
    quotedText = models.TextField(max_length=1000,null=True,blank=True)
    content_type = models.ForeignKey(ContentType,on_delete=models.CASCADE,null=True)
    object_id = models.PositiveIntegerField(null=True)
    parent = GenericForeignKey('content_type','object_id')
    comments = GenericRelation('Post', on_delete=models.CASCADE)

    def getComments(self):
        children = self.comments.all().order_by('createdOn')
        commentDict = self.__dict__.copy()
        del commentDict['_state']
        commentDict['createdOn'] = commentDict['createdOn'].replace(microsecond=0)
        commentDict['editedOn'] = commentDict['editedOn'].replace(microsecond=0)
        commentDict['createdBy'] = {"username":self.createdBy.username,"id":self.createdBy.pk}
        commentDict['comments'] = [child.getComments() for child in children]
        return commentDict
        
    def Post(parent,content,createdBy):
        self.parent = parent
        self.content = content
        self.createdBy = createdBy
    def __repr__(self):
        return f"Post({self.createdBy},{self.content})"
    def __str__(self):
        return self.content 

class Thread(Post):
    STATUS = [
        ("O","Open"),
        ("C","Closed"),
        ("R","Resolved"),
    ]
    TYPE = [
        ("Q","Question"),
        ("D","Discussion"),
    ]
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=200,choices=STATUS,default="O")
    threadType = models.CharField(max_length=200,choices=TYPE)
    tags = models.ManyToManyField('Tag',blank=True)
    def __repr__(self):
        return f"Thread({self.title},{self.threadType})"
    def __str__(self):
        return self.title

class UserUpvote(models.Model):
    user = models.ForeignKey(User,models.DO_NOTHING)
    postId = models.IntegerField()
    class Meta:
        unique_together = ("user","postId")

class Tag(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(max_length=1000)
    threads = models.ManyToManyField('Thread')
    def __repr__(self):
        return self.name

class Order(models.Model):
    STATUS = [
        ("O","Open"),
        ("C","Closed"),
        ("CA","Canceled"),
        ("IP","In Progress")
    ]
    status = models.CharField(max_length=200,choices=STATUS,default="O")
    date = models.DateTimeField(default=timezone.now)
    requestingUser = models.ForeignKey(User,related_name='order',on_delete=models.CASCADE)
    requestingCompany = models.ForeignKey('Company',related_name='order',on_delete=models.CASCADE,null=True)
    braintreeID = models.CharField(max_length=10,null=True)

class OrderLine(models.Model):
    order = models.ForeignKey('Order',related_name='orderLines',on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.FloatField(default=0)
    item = models.ForeignKey('Item',on_delete=models.CASCADE)

class Item(models.Model):
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=1000)
    price = models.FloatField()

class Subscription(models.Model):
    company = models.ForeignKey('Company',on_delete=models.CASCADE,related_name='subscription', null=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='subscription', null=True)
    plan = models.ForeignKey('Plan',on_delete=models.CASCADE)
    #statuses: active, pending, canceled, inactive
    status = models.CharField(max_length=64,default="inactive")
    braintreeID = models.CharField(max_length=32,null=True)
    discount = models.OneToOneField('Discount',related_name='discount',on_delete=models.DO_NOTHING,null=True)
    def totalPrice(self):
        return self.plan.monthlyRate - (self.plan.monthlyRate * (self.discount.rate if self.discount != None else 0))
    def __repr__(self):
        return f"Subscription({self.company if self.company else self.user},{self.plan},{self.discount})"

class Plan(models.Model):
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=24)
    monthlyRate = models.FloatField()
    description = models.TextField()
    braintreeID = models.CharField(max_length=200)
    def __repr__(self):
        return f"Plan({self.name},{self.type})"
    def __str__(self):
        return self.name

class Discount(models.Model):
    code = models.CharField(max_length=200,unique=True)
    braintreeID = models.CharField(max_length=200)
    active = models.BooleanField()
    rate = models.FloatField()
    expiration = models.DateField()

class EmailRequest(models.Model):
    sentOn = models.DateTimeField(default=timezone.now)
    recipientEmail = models.CharField(max_length=255)
    code = models.CharField(max_length=32,unique=True)
    sender = models.ForeignKey(User,on_delete=models.CASCADE,related_name='emailRequests')
    company = models.ForeignKey('Company',on_delete=models.CASCADE,related_name='emailRequests', null=True)




