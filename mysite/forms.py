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

class PaypalFormView(BSModalModelForm):
    template_name = 'paypal_form.html'
    form_class = PayPalPaymentsForm

    def get_initial(self):
        return {
            "business": 'health@open.build',
            "amount": 20,
            "currency_code": "USD",
            "item_name": 'Annual Monitoring',
            "invoice": 1,
            "notify_url": self.request.build_absolute_uri(reverse('paypal-ipn')),
            "return_url": self.request.build_absolute_uri(reverse('paypal-return')),
            "cancel_return": self.request.build_absolute_uri(reverse('paypal-cancel')),
            "lc": 'EN',
            "no_shipping": '1',
        }
