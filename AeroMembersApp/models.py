from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey,GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.core import serializers
from django.forms.models import model_to_dict
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
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
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

    def __str__(self):
        return '%s %s' % (self.user.first_name, self.user.last_name)

class Contact(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE, unique=True, null=True)
    company = models.OneToOneField('Company',on_delete=models.CASCADE, unique=True, null=True)
    street_address = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=200, blank=True)
    state = models.CharField(max_length=200, blank=True)
    zip_code = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=20, blank=True)

class Resume(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE, unique=True)
    #resumeFile = models.FileField(upload_to="resume/File/Directory", blank=True)
    education = models.CharField(max_length=200, blank=True)
    awards = models.TextField(max_length=200, blank=True)
    certifications = models.TextField(max_length=200, blank=True)

class JobDescription(models.Model):
    resume = models.OneToOneField('Resume', on_delete=models.CASCADE, unique=True)
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
    MEMBERSHIP_LEVEL = [
        ("S","Silver"),
        ("G","Gold"),
        ("P","Platinum")
    ]
    ACTIVITY_TYPE = [
        ("Contract Management","Contract Management"),
        ("Design","Design"),
        ("Engineering","Engineering"),
        ("Facility Management","Facility Management"),
        ("General Management","General Management"),
        ("Human Resources","Human Resources"),
        ("IT","IT"),
        ("Manufacturing Engineering","Manufacturing Engineering"),
        ("Marketing","Marketing"),
        ("Operations","Operations"),
        ("Planning","Planning"),
        ("Production","Production"),
        ("Purchasing","Purchasing"),
        ("Quality","Quality"),
        ("R&D","R&D"),
        ("Repair & Warranty","Repair & Warranty"),
        ("Sales","Sales"),
        ("Supply Chain Management","Supply Chain Management"),
    ]
    name = models.CharField(max_length=200)
    department = models.CharField(max_length=200)
    membership_level = models.CharField(max_length=200, choices=MEMBERSHIP_LEVEL)
    cage_code = models.CharField(max_length=6, null=True, blank=True)
    number_of_employees = models.IntegerField()
    activity_type = models.CharField(max_length = 200, choices=ACTIVITY_TYPE)
    def __str__(self):
        return self.name

class NAICS(models.Model):
    company = models.ForeignKey('Company', on_delete=models.CASCADE)
    code = models.IntegerField()

class SectorMapping(models.Model):
    code = models.IntegerField(unique=True)
    sector = models.CharField(max_length=200)

class Post(models.Model):
    content = models.TextField(max_length=1000)
    score = models.IntegerField(default=0)
    createdOn = models.DateTimeField(default=timezone.now)
    editedOn = models.DateTimeField(default = timezone.now)
    createdBy = models.ForeignKey(User)
    quotedText = models.TextField(max_length=1000,null=True,blank=True)
    content_type = models.ForeignKey(ContentType,on_delete=models.CASCADE,null=True)
    object_id = models.PositiveIntegerField(null=True)
    parent = GenericForeignKey('content_type','object_id')
    comments = GenericRelation('Post', on_delete=models.CASCADE)

    def getComments(self):
        children = self.comments.all().order_by('createdOn')
        print "my id: ",self.pk,"num children: ",len(children)
        commentDict = self.__dict__.copy()
        del commentDict['_state']
        commentDict['createdOn'] = unicode(commentDict['createdOn'].replace(microsecond=0))
        commentDict['editedOn'] = unicode(commentDict['editedOn'].replace(microsecond=0))
        commentDict['createdBy'] = self.createdBy.username
        commentDict['comments'] = [child.getComments() for child in children]
        #out = [commentDict]
        #for child in children:
        #    out+=child.getComments()
        return commentDict
        
    def Post(parent,content,createdBy):
        self.parent = parent
        self.content = content
        self.createdBy = createdBy
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
    tags = models.ManyToManyField('Tag',null=True,blank=True)
    def __str__(self):
        return self.title

class UserUpvote(models.Model):
    user = models.ForeignKey(User)
    postId = models.IntegerField()
    class Meta:
        unique_together = ("user","postId")

class Tag(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(max_length=1000)
    threads = models.ManyToManyField('Thread')
    def __str__(self):
        return self.name





