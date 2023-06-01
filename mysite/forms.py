from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import *
from crispy_forms.layout import Layout, Submit, Reset, Field
from functools import partial
from django import forms
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
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

        return user


class RegistrationUpdateForm(UserChangeForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    github_profile = forms.URLField(required=False)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'username', 'github_profile')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].widget = forms.HiddenInput()

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field('email', placeholder='Email'),
            Field('first_name', placeholder='First Name'),
            Field('last_name', placeholder='Last Name'),
            Field('username', placeholder='Username'),
            Field('github_profile', placeholder='Github Profile URL'),
            Submit('submit', 'Update')
        )

        # Set initial values for is_bounty_hunter and github_profile fields
        user = self.instance
        if hasattr(user, 'bountyhunter'):
            bounty_hunter = user.bountyhunter
            self.initial['is_bounty_hunter'] = True
            self.initial['github_profile'] = bounty_hunter.github_profile
        else:
            self.initial['is_bounty_hunter'] = False

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()

        is_bounty_hunter = self.cleaned_data['is_bounty_hunter']
        if is_bounty_hunter:
            bounty_hunter, _ = BountyHunter.objects.get_or_create(user=user)
            bounty_hunter.github_profile = self.cleaned_data['github_profile']
            bounty_hunter.save()
        else:
            BountyHunter.objects.filter(user=user).delete()
            BountySetter.objects.get_or_create(user=user)

        return user