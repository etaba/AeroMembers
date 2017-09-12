from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from AeroMembersApp.models import *#Profile, Contact, Resume, JobDescription

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username','password','first_name','last_name','email')

class UserFormWithoutPassword(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username','first_name','last_name','email')

class ProfileForm(forms.ModelForm):
	class Meta:
		model = Profile
		fields = ('birthdate', 'private')


class ContactForm(forms.ModelForm):
	class Meta:
		model = Contact
		fields = ('street_address', 'city', 'state', 'zip_code', 'phone')

class CompanyForm(forms.ModelForm):
	class Meta:
		model = Company
		fields = ('name', 'department', 'membership_level','cage_code', 'number_of_employees', 'activity_type')

class NAICSForm(forms.ModelForm):
	class Meta:
		model = NAICS
		fields = ('code',)

