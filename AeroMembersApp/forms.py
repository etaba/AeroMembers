from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, AuthenticationForm
from django.contrib.auth.models import User
from AeroMembersApp.models import *
class BaseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class UserForm(BaseForm):
    class Meta:
        model = User
        fields = ('username','password','first_name','last_name','email')
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
            'password': forms.TextInput(attrs={'placeholder': 'Password','type':'password'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name'}),
            'email': forms.TextInput(attrs={'placeholder': 'Email'}),
        }

class SigninForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(SigninForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs = {'class': 'form-control', 'placeholder': 'Email'}
        self.fields['password'].widget.attrs = {'class': 'form-control', 'placeholder': 'Password'}

class ContactForm(BaseForm):
    class Meta:
        model = Contact
        fields = ('street_address', 'city', 'state', 'zip_code', 'phone')
        widgets = {
            'street_address': forms.TextInput(attrs={'placeholder': 'Street'}),
            'city': forms.TextInput(attrs={'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'placeholder': 'State'}),
            'zip_code': forms.TextInput(attrs={'placeholder': 'Zip Code'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Phone'}),
        }

class UserFormWithoutPassword(BaseForm):
    class Meta:
        model = User
        fields = ('username','first_name','last_name','email')
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name'}),
            'email': forms.TextInput(attrs={'placeholder': 'Email'}),
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('birthdate', 'private')
        widgets = {
            'birthdate': forms.TextInput(attrs={'placeholder': 'Birthday','class': 'form-control','type':'date'}),
            'private': forms.TextInput(attrs={'class': 'custom-control-input','type':'checkbox'}),
        }




class CompanyForm(BaseForm):
    class Meta:
        model = Company
        fields = ('name', 'department','cage_code', 'number_of_employees', 'activity_type','naics','description')
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Name'}),
            'department': forms.TextInput(attrs={'placeholder': 'Department'}),
            'number_of_employees': forms.TextInput(attrs={'placeholder': 'Number of Employees'}),
            'cage_code': forms.TextInput(attrs={'placeholder': 'Cage Code'}),
            'description': forms.TextInput(attrs={'placeholder' : 'Description'})
        }


class ThreadForm(BaseForm):
    class Meta:
        model = Thread
        fields = ('title','content','threadType')
        widgets = {
            'title': forms.TextInput(attrs={'placeholder':'Title'}),
            'content': forms.TextInput(attrs={'placeholder':'Description'}),
        }

class ThreadCommentForm(BaseForm):
    class Meta:
        model = Post
        fields = ('content',)
        widgets = {
            'content': forms.TextInput(attrs={'placeholder':'Enter a new comment here'}),
        }

class FancyPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(FancyPasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs = {'class': 'form-control', 'placeholder': 'Old Password'}
        self.fields['new_password1'].widget.attrs = {'class': 'form-control', 'placeholder': 'New Password'}
        self.fields['new_password2'].widget.attrs = {'class': 'form-control', 'placeholder': 'Confirm Password'}


