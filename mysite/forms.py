from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import *
from crispy_forms.layout import Layout, Submit, Reset, Field
from functools import partial
from django import forms
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordResetForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from punchlist.models import Product
from .models import ProductOwnerProfile

# paypal
from django.views.generic import FormView
from paypal.standard.forms import PayPalPaymentsForm

from bootstrap_modal_forms.forms import BSModalModelForm

from .models import CustomUser


class PasswordResetForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError('No user with this email address.')
        return email



from django.contrib.auth.forms import UserCreationForm
from punchlist.models import PunchlistHunter, PunchlistSetter

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    organization_name = forms.CharField(required=True)
    is_labs_user = forms.BooleanField(required=False, label="I already have a product on Buildly Labs")

    
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'username', 'password1', 'password2','is_labs_user','organization_name')
        
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
        user.save()

        return user


class ProductOwnerProfileForm(forms.ModelForm):
    class Meta:
        model = ProductOwnerProfile
        fields = ['organization_name']

class RegistrationUpdateForm(UserChangeForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    is_punchlist_hunter = forms.BooleanField(required=False)
    github_profile = forms.URLField(required=False)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'username')

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
            Submit('submit', 'Update')
        )

        # Set initial values for is_punchlist_hunter and github_profile fields
        user = self.instance

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()

        return user
    
# main_app/forms.py

from django import forms
from punchlist.models import Product

"""
This form is used to create a new product in the Punchlist app.
"""

class ProductForm(forms.ModelForm):
    
    class Meta:
        model = Product
        fields = [
            'name', 
            'description', 
            'product_info',
            'dev_url',
            'prod_url',
            'repository_url', 
            'start_date', 
            'end_date',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter product name', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'placeholder': 'Enter a brief description of the product', 'class': 'form-control'}),
            'product_info': forms.Textarea(attrs={'placeholder': 'Enter detailed product information', 'class': 'form-control'}),
            'dev_url': forms.URLInput(attrs={'placeholder': 'Enter development URL', 'class': 'form-control'}),
            'prod_url': forms.URLInput(attrs={'placeholder': 'Enter production URL', 'class': 'form-control'}),
            'repository_url': forms.URLInput(attrs={'placeholder': 'Enter repository URL', 'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
        labels = {
            'name': 'Product Name',
            'description': 'Product Description',
            'product_info': 'Product Information',
            'dev_url': 'Development URL',
            'prod_url': 'Production URL',
            'repository_url': 'Repository URL',
            'start_date': 'Start Date',
            'end_date': 'End Date',
        }
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')  # Store request object
        super().__init__(*args, **kwargs)
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.owner = self.request.user
        if commit:
            instance.save()
        return instance 
    