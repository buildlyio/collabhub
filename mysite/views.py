from django.shortcuts import  render, redirect
from .forms import NewUserForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.views.generic import TemplateView

from django.urls import reverse_lazy
from .forms import PayPalPaymentsForm

from bootstrap_modal_forms.generic import BSModalCreateView

from allauth.socialaccount.forms import SignupForm

class MyCustomSocialSignupForm(SignupForm):

    def save(self, request):

        # Ensure you call the parent class's save.
        # .save() returns a User object.
        user = super(MyCustomSocialSignupForm, self).save(request)

        # Add your own processing here.

        # You must return the original result.
        return user

def register_request(request):
	if request.method == "POST":
		form = NewUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user, backend='django.contrib.auth.backends.ModelBackend')
			messages.success(request, "Registration successful." )
			return redirect("/")
		messages.error(request, "Unsuccessful registration. Invalid information.")
	form = NewUserForm()
	return render (request=request, template_name="register.html", context={"register_form":form})

def login_request(request):
	if request.method == "POST":
		form = AuthenticationForm(request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user, backend='django.contrib.auth.backends.ModelBackend')
				messages.info(request, f"You are now logged in as {username}.")
				return redirect("/")
			else:
				messages.error(request,"Invalid username or password.")
		else:
			messages.error(request,"Invalid username or password.")
	form = AuthenticationForm()
	return render(request=request, template_name="login.html", context={"login_form":form})

def logout_request(request):
	logout(request)
	messages.info(request, "You have successfully logged out.")
	return redirect("/")

from django.urls import reverse
from django.shortcuts import render
from paypal.standard.forms import PayPalPaymentsForm

def paypal_payment(request):

    # What you want the button to do.
    paypal_dict = {
        "business": "team@open.build",
        "amount": "10000000.00",
        "item_name": "DevHunter Assigned",
        "invoice": "00001",
        "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
        "return": request.build_absolute_uri(reverse('paypal-return')),
        "cancel_return": request.build_absolute_uri(reverse('paypal-cancel')),
        "custom": "premium_plan",  # Custom command to correlate to some function later (optional)
    }

    # Create the instance.
    form = PayPalPaymentsForm(initial=paypal_dict)
    context = {"form": form}
    return render(request, "payment.html", context)


class PaypalView(BSModalCreateView):
    template_name = 'payment.html'
    form_class = PayPalPaymentsForm
    success_message = 'Success: Payment was created.'
    success_url = reverse_lazy('index')

class PaypalReturnView(TemplateView):
    template_name = 'paypal_success.html'

class PaypalCancelView(TemplateView):
    template_name = 'paypal_cancel.html'
