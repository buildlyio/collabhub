from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import *
from crispy_forms.layout import Layout, Submit, Reset
from functools import partial
from django import forms
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# paypal
from django.views.generic import FormView
from paypal.standard.forms import PayPalPaymentsForm

from bootstrap_modal_forms.forms import BSModalModelForm


# User Forms
class NewUserForm(UserCreationForm):
	email = forms.EmailField(required=True)

	class Meta:
		model = User
		fields = ("username", "email", "password1", "password2")

	def save(self, commit=True):
		user = super(NewUserForm, self).save(commit=False)
		user.email = self.cleaned_data['email']
		if commit:
			user.save()
		return user


from django.contrib.auth.forms import UserCreationForm
from bounty.models import BountyHunter, BountySetter

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    is_bounty_hunter = forms.BooleanField(required=False)
    github_profile = forms.URLField(required=False)
    phone_number = forms.CharField(required=False)
    street_address = forms.CharField(required=False)
    city = forms.CharField(required=False)
    state = forms.CharField(required=False)
    postal_code = forms.CharField(required=False)
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'username', 'password1', 'password2', 'is_bounty_hunter', 'github_profile')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
        
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field('email', placeholder='Email'),
            Field('first_name', placeholder='First Name'),
            Field('last_name', placeholder='Last Name'),
            Field('password1', placeholder='Password'),
            Field('password2', placeholder='Confirm Password'),
            Field('is_bounty_hunter', placeholder='Are you a Bounty Hunter?'),
            Field('github_profile', placeholder='Github Profile URL'),
            Submit('submit', 'Register')
        )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already taken")
        return email
    
    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_bounty_hunter = self.cleaned_data['is_bounty_hunter']
        user.save()
        if user.is_bounty_hunter:
            user=user,
         
            bounty_hunter = BountyHunter(
                user=user,
                github_profile=self.cleaned_data['github_profile']
            )
            bounty_hunter.save()
        else:
       
            user=user,
            phone_number=self.cleaned_data['phone_number'],
            street_address=self.cleaned_data['street_address'],
            city=self.cleaned_data['city'],
            state=self.cleaned_data['state'],
            postal_code=self.cleaned_data['postal_code']
  
            bounty_setter = BountySetter(
                user=user,
            )
            bounty_setter.save()
        return user


class RegistrationUpdateForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    is_bounty_hunter = forms.BooleanField(required=False)
    github_profile = forms.URLField(required=False)
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'username', 'phone_number', 'street_address', 'city', 'state', 'postal_code')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field('email', placeholder='Email'),
            Field('first_name', placeholder='First Name'),
            Field('last_name', placeholder='Last Name'),
            Field('username', placeholder='username'),
            Field('github_profile', placeholder='Github Profile URL'),
            Submit('submit', 'Register')
        )
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_bounty_hunter = self.cleaned_data['is_bounty_hunter']
        user.save()
        
        if user.is_bounty_hunter:
            user=user,
            bounty_hunter = BountyHunter(
                github_profile=self.cleaned_data['github_profile'],
            )
            bounty_hunter.save()
        else:
            user=user,
        return user
