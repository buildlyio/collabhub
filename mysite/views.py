from django.shortcuts import  render, redirect
from .forms import RegistrationForm, RegistrationUpdateForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse


from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.db import transaction

from django.contrib import messages

from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .forms import CustomerIntakeForm

User = get_user_model()


def homepage(request):
    """View function for home page of site."""
    # Get some featured Forge apps for the homepage
    try:
        from forge.models import ForgeApp
        featured_apps = ForgeApp.objects.filter(is_published=True)[:6]
        apps_count = ForgeApp.objects.filter(is_published=True).count()
    except:
        # Handle case where Forge app is not available
        featured_apps = []
        apps_count = 0
    
    context = {
        'featured_apps': featured_apps,
        'apps_count': apps_count,
    }
    return render(request, 'home_page.html', context)


def agencies_list(request):
    """Placeholder view for agencies listing"""
    return render(request, 'agencies_list.html')


def agency_review_utility(request):
    """Simple agency review utility view"""
    return render(request, 'base.html')

from django_tables2 import SingleTableView
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
# from .tables import ProductTable

from django.views.generic import ListView

from social_django.models import UserSocialAuth



from django.views.generic import CreateView
from django.urls import reverse_lazy
# from .forms import ProductForm  # Assuming you have a ProductForm


from django.views.generic import UpdateView
from django.views.generic import DeleteView



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
            
            # User created successfully
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            messages.info(request, "Your Profile has been created and you should have been logged in, if not please process to the <a href='/login'>Login</a> page.")
            return redirect('/')  # Redirect to home page

    return render(request, 'register.html', {'form': form})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = RegistrationUpdateForm(request.POST, instance=request.user)
        try:
            with transaction.atomic():
                # Create a new user object
                user = form.save()
                
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
				
				# Check for 'next' parameter to redirect back to the original page
				next_url = request.POST.get('next') or request.GET.get('next')
				if next_url:
					return redirect(next_url)
				return redirect("/")
			else:
				messages.error(request,"Invalid username or password.")
		else:
			messages.error(request,"Invalid username or password.")
	else:
		form = AuthenticationForm()
	return render(request=request, template_name="login.html", context={"login_form":form})

def logout_request(request):
	logout(request)
	messages.info(request, "You have successfully logged out.")
	return redirect("/")


# from .forms import ProductForm  # Assuming you have a ProductForm for manual entry

# def add_product_details(request):
#     if request.method == 'POST':
#         form = ProductForm(request.POST)
#         if form.is_valid():
#             product = form.save(commit=False)
#             product.organization_uuid = request.user.product_owner_profile.organization_name  # Or however you link this
#             product.save()

#             request.user.product_owner_profile.product = product
#             request.user.product_owner_profile.save()
#             return redirect('dashboard')  # Redirect to the dashboard or relevant page

#     else:
#         form = ProductForm()

#     return render(request, 'main_app/add_product_details.html', {'form': form})


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


def customer_intake(request):
    """Public marketing-forward intake form for new customers."""
    # Dynamic product catalog for messaging + choices
    product_catalog = [
        {
            "key": "rad_ai_delivery",
            "name": "RAD Process for AI Delivery",
            "tagline": "Guardrails, governance, and delivery playbooks for AI features.",
            "description": "Refined Rapid Application Delivery process that keeps AI work safe, reviewable, and ship-ready with built-in checkpoints.",
        },
        {
            "key": "verified_devs",
            "name": "Verified Developers & Certifications",
            "tagline": "Hands-on builders with Buildly certifications, reviews, and live project history.",
            "description": "Pre-vetted engineers with proof of work, code reviews, and certification badges mapped to your stack.",
        },
        {
            "key": "cto_apprentice",
            "name": "CTO-in-Training (Mentored)",
            "tagline": "Try a rising technical lead with senior mentorship and guidance contracts.",
            "description": "Great for new startups to trial a future CTO while we provide architectural guardrails and weekly coaching.",
        },
        {
            "key": "scale_teams",
            "name": "Scale Your Team (Elastic Pods)",
            "tagline": "Add a Buildly pod short-term or long-term with product, design, and engineering.",
            "description": "Spin up or extend a squad that can own delivery, augment an in-house team, or cover critical initiatives.",
        },
        {
            "key": "labs_platform",
            "name": "Buildly Labs Portfolio Platform",
            "tagline": "Document products, roadmaps, and run delivery in one place.",
            "description": "Connect to Buildly Labs to manage briefs, artifacts, and team assignments across your portfolio.",
        },
    ]

    product_choices = [(item["key"], item["name"]) for item in product_catalog]

    if request.method == "POST":
        # Initialize form with timestamp on GET
        import time
        initial_data = {'form_timestamp': str(int(time.time()))}
        form = CustomerIntakeForm(request.POST, product_choices=product_choices)
        if form.is_valid():
            cleaned = form.cleaned_data
            selected = [p for p in product_catalog if p["key"] in cleaned["products"]]

            subject = "New Customer Intake - Buildly"
            lines = [
                "New customer request",
                f"Name: {cleaned['name']}",
                f"Email: {cleaned['email']}",
                f"Company: {cleaned['company']}",
                f"Timeline: {cleaned['timeline']}",
                "Products:",
            ]
            for s in selected:
                lines.append(f"- {s['name']}: {s['tagline']}")
            if cleaned.get("preferences"):
                lines.append("")
                lines.append("Notes/Preferences:")
                lines.append(cleaned["preferences"])

            # Save to database
            from onboarding.models import CustomerIntakeRequest
            products_str = ', '.join([s['name'] for s in selected])
            intake_request = CustomerIntakeRequest.objects.create(
                name=cleaned['name'],
                email=cleaned['email'],
                company=cleaned['company'],
                products=products_str,
                timeline=cleaned['timeline'],
                preferences=cleaned.get('preferences', ''),
                status='new'
            )

            # Create notifications for all superuser staff
            from onboarding.models import Notification
            from django.contrib.auth.models import User
            superusers = User.objects.filter(is_superuser=True, is_active=True)
            for user in superusers:
                Notification.objects.create(
                    recipient=user,
                    title="New Customer Intake Request",
                    message=f"{cleaned['company']} ({cleaned['name']}) submitted a request for: {products_str}",
                    link_url=f"/admin/onboarding/customerintakerequest/{intake_request.pk}/change/",
                    notification_type="custom"
                )

            # Also send email as backup
            message = "\n".join(lines)
            send_mail(
                subject,
                message,
                getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@buildly.io"),
                ["team@buildly.io"],
                fail_silently=True,
            )

            # Quick confirmation view
            return render(
                request,
                "customer_intake_thanks.html",
                {
                    "labs_url": "https://labs.buildly.io",
                },
            )
    else:
        # Set initial timestamp for new form
        import time
        form = CustomerIntakeForm(
            product_choices=product_choices,
            initial={'form_timestamp': str(int(time.time()))}
        )

    return render(
        request,
        "customer_intake.html",
        {
            "form": form,
            "product_catalog": product_catalog,
            "labs_url": "https://labs.buildly.io",
        },
    )


def partner_redirect(request):
    """Redirect partners to agency registration"""
    # If user is logged in and has an agency, go to dashboard
    if request.user.is_authenticated:
        try:
            from onboarding.models import DevelopmentAgency
            agency = DevelopmentAgency.objects.get(user=request.user)
            return redirect('/onboarding/agency/dashboard/')
        except:
            pass
    # Otherwise go to agency registration
    return redirect('/onboarding/agency/register/')


def agency_list_redirect(request):
    """Redirect agency list to onboarding agencies"""
    return redirect('/onboarding/agencies/')


def forge_redirect(request):
    """Redirect /forge/ to /marketplace/"""
    return redirect('/marketplace/')


def agency_review_utility(request):
    """Placeholder for agency review utility"""
    messages.info(request, "Agency review utility coming soon!")
    return redirect('/')


