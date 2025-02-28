from django.shortcuts import  render, redirect
from .forms import RegistrationForm, RegistrationUpdateForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse

from punchlist.models import Product

from bootstrap_modal_forms.generic import BSModalCreateView

from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.db import transaction

from punchlist.forms import PunchlistHunterForm, PunchlistSetterForm

from punchlist.models import PunchlistHunter, PunchlistSetter

from django.contrib import messages

from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

User = get_user_model()

from django_tables2 import SingleTableView
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from .tables import ProductTable

from django.views.generic import ListView

from social_django.models import UserSocialAuth


class ProductListView(SingleTableView):
    model = Product
    table_class = ProductTable  # This should be your table class
    template_name = 'product_list.html'  # Update with your template path

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(owner=self.request.user)
        return queryset

from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import ProductForm  # Assuming you have a ProductForm

class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'product_form.html'
    success_url = reverse_lazy('product_list')
    
    def get_form_kwargs(self):
        kwargs = super(ProductCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
    def form_valid(self, form):
        # Optional: Add custom logic here if needed
        return super().form_valid(form)

from django.views.generic import UpdateView

class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'product_form.html'
    success_url = reverse_lazy('product_list')
    
    def get_form_kwargs(self):
        kwargs = super(ProductUpdateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        # Optional: Add custom logic here if needed
        return super().form_valid(form)


from django.views.generic import DeleteView

class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'product_confirm_delete.html'
    success_url = reverse_lazy('product_list')


from punchlist.models import Punchlist
from punchlist.forms import PunchlistForm

class CreatePunchlistView(CreateView):
    model = Punchlist
    form_class = PunchlistForm
    template_name = '/punchlist/punchlist_form.html'
    success_url = reverse_lazy('product_list')

    def get_form_kwargs(self):
        kwargs = super(CreatePunchlistView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
    def form_valid(self, form):
        form.instance.product = Product.objects.get(pk=self.kwargs['pk'])
        return super().form_valid(form)



def send_password_reset_email(request, email):
    user = User.objects.filter(email=email).first()

    if user:
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        reset_url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        reset_url = request.build_absolute_uri(reset_url)

        subject = 'Reset Your Password'
        message = f'Click the following link to reset your password:\n\n{reset_url}'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email]

        send_mail(subject, message, from_email, recipient_list)
        return True
    return False


def register(request):
    form = RegistrationForm(request.POST)
    if form.is_valid():
            user = form.save(commit=False)
            user.is_product_owner = True
            user.groups.add(1)
            user.save()
            
            # Create a new PunchlistHunter or PunchlistSetter object for the user
            try:
                get_user = User.objects.get(username=user.username)
                punchlist_setter = PunchlistSetter.objects.create(user=get_user)
            except User.DoesNotExist:
                pass

            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            messages.info(request, "Your Profile has been created and you should have been logged in, if not please process to the <a href='/login'>Login</a> page.")
            return redirect('product_add')  # Redirect to add product details manually

    return render(request, 'register.html', {'form': form})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = RegistrationUpdateForm(request.POST, instance=request.user)
        try:
            with transaction.atomic():
                # Create a new user object
                user = form.save()

                # Create a new PunchlistHunter or PunchlistSetter object for the user
                punchlist_setter, created = PunchlistSetter.objects.get_or_create(user=user)
                if created:
                    punchlist_setter = PunchlistSetter.objects.create(user=user)
                else:
                    punchlist_setter = PunchlistSetter.objects.get(user=user)
                
                messages.info(request, "Your Profile has been updated.")
                redirect("/login")
                
                
        except Exception as e:
            error_message = str(e)
            form.add_error(None, error_message)  # Add the error to non-field errors
            messages.error(request, error_message)  # Optional: Add the error to messages framework
    else:
        form = RegistrationUpdateForm(instance=request.user)

    context = {
        'form': form,
    }
    return render(request, 'register_update.html', context)


def login_request(request):
	if request.method == "POST":
		form = AuthenticationForm(request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user, backend='django.contrib.auth.backends.ModelBackend')
				messages.info(request, "You are now logged in.")
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


from .forms import ProductForm  # Assuming you have a ProductForm for manual entry

def add_product_details(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.organization_uuid = request.user.product_owner_profile.organization_name  # Or however you link this
            product.save()

            request.user.product_owner_profile.product = product
            request.user.product_owner_profile.save()
            return redirect('dashboard')  # Redirect to the dashboard or relevant page

    else:
        form = ProductForm()

    return render(request, 'main_app/add_product_details.html', {'form': form})


from django.shortcuts import redirect, render
from social_django.utils import load_strategy
from social_django.models import UserSocialAuth

def github_complete(request):
    # Get the OAuth token from the social auth framework
    user = request.user  # The user should already be logged in via your app

    if user.is_authenticated:
        # Load the GitHub access token using social auth
        strategy = load_strategy()
        social_user = user.social_auth.get(provider='github')
        github_access_token = social_user.extra_data['access_token']

        # Optionally, store the token in a user profile or database for future use
        # Example: Save token in a user profile (assuming you have a profile model)
        user.profile.github_token = github_access_token
        user.profile.save()

        return redirect('/')  # Redirect user after successful linking
    else:
        return redirect('/login/')  # Redirect to login if not authenticated

import punchlist.util_agency as util_agency

def agency_review_utility(request):
    util_status = util_agency.check_all_agencies()
    return redirect('/')  # Redirect to the home page after running the utility

