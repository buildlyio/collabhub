from django.shortcuts import  render, redirect
from .forms import RegistrationForm, RegistrationUpdateForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy

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

User = get_user_model()

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
        try:
            with transaction.atomic():
                # Create a new user object
                user = form.save()

                # Create a new PunchlistHunter or PunchlistSetter object for the user
                if request.POST.get('is_punchlist_hunter') == 'True':
                    punchlist_hunter = PunchlistHunter.objects.create(user=user)
                else:
                    punchlist_setter = PunchlistSetter.objects.create(user=user)
                
                messages.info(request, "You are now Registered, please login.")
                redirect("/login")
                
                
        except Exception as e:
            error_message = str(e)
            form.add_error(None, error_message)  # Add the error to non-field errors
            messages.error(request, error_message)  # Optional: Add the error to messages framework

    else:
        form = RegistrationForm()

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
                if request.POST.get('is_punchlist_hunter') == 'True':
                    punchlist_hunter, created = PunchlistHunter.objects.get_or_create(user=user)
                else:
                    punchlist_setter, created = PunchlistSetter.objects.get_or_create(user=user)
                
                messages.info(request, "Your Profile has been updated.")
                redirect("/login")
                
                
        except Exception as e:
            error_message = str(e)
            form.add_error(None, error_message)  # Add the error to non-field errors
            messages.error(request, error_message)  # Optional: Add the error to messages framework
    else:
        form = RegistrationUpdateForm(instance=request.user)

        # Get the related PunchlistHunter or PunchlistSetter object
        if hasattr(request.user, 'punchlisthunter'):
            profile = request.user.punchlisthunter
            profile_form = PunchlistHunterForm(instance=profile)
        elif hasattr(request.user, 'punchlistsetter'):
            profile = request.user.punchlistsetter
            profile_form = PunchlistSetterForm(instance=profile)
        else:
            # If the user doesn't have a related object, redirect to homepage
            messages.info(request, "You have not Registered as Punchlist Hunter or Setter, please contact support.")
            return redirect('/')

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


