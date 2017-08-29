from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.

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
    user = models.ForeignKey(User, on_delete=models.CASCADE, unique=True)
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

#@receiver(post_save, sender=User)
#def create_user_profile(sender, instance, created, **kwargs):
#    if created:
#        Profile.objects.create(user=instance)
#
#@receiver(post_save, sender=User)
#def save_user_profile(sender, instance, **kwargs):
#    instance.profile.save()

def __str__(self):
    return '%s %s' % (self.user.first_name, self.user.last_name)

class Contact(models.Model):
	profile = models.ForeignKey('Profile',on_delete=models.CASCADE, unique=True, null=True)
	company = models.ForeignKey('Company',on_delete=models.CASCADE, unique=True, null=True)
	street_address = models.CharField(max_length=200, blank=True)
	city = models.CharField(max_length=200, blank=True)
	state = models.CharField(max_length=200, blank=True)
	zip_code = models.CharField(max_length=200, blank=True)
	phone = models.CharField(max_length=20, blank=True)

class Resume(models.Model):
	profile = models.ForeignKey('Profile',on_delete=models.CASCADE, unique=True)
	#resumeFile = models.FileField(upload_to="resume/File/Directory", blank=True)
	education = models.CharField(max_length=200, blank=True)
	awards = models.TextField(max_length=200, blank=True)
	certifications = models.TextField(max_length=200, blank=True)

class JobDescription(models.Model):
	resume = models.ForeignKey('Resume', on_delete=models.CASCADE, unique=True)
	industry = models.CharField(max_length=200, choices=INDUSTRY_CHOICES)
	job_title = models.CharField(max_length=200)
	salary = models.IntegerField(blank=True, help_text="Will not be visible to other users.")
	start_date = models.DateTimeField('start date')
	end_date = models.DateTimeField('end date')

class CompanyUser(models.Model):
	user = models.ForeignKey('Profile',unique=True,on_delete=models.CASCADE)
	company = models.ForeignKey('Company',unique=True,on_delete=models.CASCADE)
	is_admin = models.BooleanField(default=False)

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

