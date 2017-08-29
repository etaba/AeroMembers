from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from AeroMembersApp.models import Profile, Contact, Resume, JobDescription

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username','password','first_name','last_name','email')

class ProfileForm(forms.ModelForm):
	class Meta:
		model = Profile
		fields = ('birthdate', 'private')

class ContactForm(forms.ModelForm):
	class Meta:
		model = Contact
		fields = ('street_address', 'city', 'state', 'zip_code', 'phone')

