from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import View
from django.views.generic import DetailView
from django.views.generic.edit import FormMixin
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from .models import Bounty
from .forms import BountyHunterSubmissionForm
from django.core.mail import send_mail
from django.template.loader import render_to_string


from .models import BountyHunter, Bounty, Issue, BountySubmission, AcceptedBounty, Contract, Bug, InsightsUser, Product
from .forms import BountyHunterForm, BountyForm, BountyHunterSubmissionForm, BugForm
from .filters import BountyFilter, IssueFilter
import requests
import json

from django.shortcuts import render, redirect

import sendgrid
from sendgrid.helpers.mail import Mail
from django.conf import settings

def send_notification_email(subject, message):
    sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
    from_email = "team@buildly.io"  # Your "from" email address
    to_email = "greg@buildly.io"      # Admin's email address

    mail = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject=subject,
        html_content=message
    )

    response = sg.send(mail)
    return response.status_code


@login_required
def new_bounty(request):
    if request.user.user_type != 'provider':
        messages.error(request, 'You do not have permission to create a new bounty.')
        return redirect('home')

    bounty_form = BountyForm(request.user)
    if request.method == 'POST':
        bounty_form = BountyForm(request.user, request.POST)
        if bounty_form.is_valid():
            # Create the new bounty object and associate it with the selected issue
            bounty = bounty_form.save(commit=False)
            issue_id = bounty_form.cleaned_data.get('issue_id')
            issue = Issue.objects.get(id=issue_id)
            bounty.issue = issue
            bounty.save()
            messages.success(request, 'Bounty created successfully!')
            
            # Send Email
            subject = "New Bug Bounty!" 
            message = "A new form has been submitted"
            send_notification_email(subject, message)
            return redirect('home')
    
    return render(request, 'new_bounty.html', {'bounty_form': bounty_form})


class MyView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'


def homepage(request):
    """View function for home page of site."""

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'home_page.html')

from django.shortcuts import render
from django_filters.views import FilterView
from django.core.paginator import Paginator
from .filters import IssueFilter

class IssueListView(ListView):
    model = Issue
    template_name = 'issue_list.html'
    context_object_name = 'issues'
    paginate_by = 16  # Display 16 items per page
    ordering = ['-created_at']  # Order by most recent

class IssueFilterView(FilterView):
    model = Issue
    filterset_class = IssueFilter
    template_name = 'issue_filter.html'
    paginate_by = 16  # Display 16 items per page
    ordering = ['-created_at']  # Order by most recent

@login_required(login_url='/')
def dashboard(request,pk):

    getReport = Bounty.objects.all().filter(id=pk)

    return render(request, 'dashboard.html', {'getReport': getReport, })


@login_required(login_url='/')
def report(request,pk):

    getReport = Bounty.objects.all().filter(id=pk)
    getHunt = BountyHunter.objects.get(pk=pk)

    return render(request, 'report.html', {'getReport': getReport, 'id': pk})


class BountyFilterView(FilterView):
    model = Bounty
    filterset_class = BountyFilter
    template_name = 'bounty_filter.html'
    paginate_by = 16  # Display 16 items per page
    ordering = ['-create_date']  # Order by most recent

def bounty_detail(request, bounty_id):
    bounty = Bounty.objects.get(id=bounty_id)
    return render(request, 'bounty_detail.html', {'bounty': bounty})


class BountyList(ListView,LoginRequiredMixin):
    """
    Monitored Sites
    """
    model = Bounty
    template_name = 'bounty_list.html'
    paginate_by = 16  # Display 16 items per page
    ordering = ['-create_date']  # Order by most recent
    

class BountyCreate(CreateView,LoginRequiredMixin,):
    """
    Montior for sites creation
    """
    model = Bounty
    template_name = 'bounty_form.html'
    #pre-populate parts of the form
    def get_initial(self):
        initial = {
            'user': self.request.user,
            }

        return initial

    def get_form_kwargs(self):
        kwargs = super(BountyCreate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):

        bounty = form.save(commit=False)
        bounty.owner = self.request.user
        bounty.save()

         # Get or create the related object (RelatedObject)
        related_obj, _  = Issue.objects.get_or_create(bounty=bounty)

        # Update the related object fields
        related_obj.title = form.cleaned_data['issue_title']
        related_obj.description = form.cleaned_data['issue_description']
        related_obj.language = form.cleaned_data['issue_language']
        related_obj.framework = form.cleaned_data['issue_framework']
        related_obj.issue_url = form.cleaned_data['issue_github_link']
        related_obj.screenshot = form.cleaned_data['issue_screenshot']
        related_obj.save()
        
        messages.success(self.request, 'Success, Bounty Created!')
        return redirect('/bounties/')

    form_class = BountyForm


class BountyUpdate(UpdateView,LoginRequiredMixin,):
    """
    Update and Edit Montiored Site.
    """
    model = Bounty
    template_name = 'bounty_form.html'
    form_class = BountyForm

    def get_form_kwargs(self):
        kwargs = super(BountyUpdate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Retrieve the related object instance
        bounty = self.get_object()

        try:
            related_obj = Issue.objects.get(bounty=bounty)
            
            # Populate the related object fields in the form
            form.fields['issue_title'].initial = related_obj.title
            form.fields['issue_description'].initial = related_obj.description
            form.fields['issue_language'].initial =  related_obj.language
            form.fields['issue_framework'].initial =  related_obj.framework
            form.fields['issue_github_link'].initial =  related_obj.issue_url
            form.fields['issue_screenshot'].initial  = related_obj.screenshot
        
        except Issue.DoesNotExist:
            related_obj = None

        
        return form

    def form_invalid(self, form):
        print("TEST")
        messages.error(self.request, 'Invalid Form', fail_silently=False)
        return render(self.get_context_data(form=form))
    
    def form_valid(self, form):
        # Save the main object (Bounty)
        bounty = form.save()

        # Get or create the related object (RelatedObject)
        related_obj, _  = Issue.objects.get_or_create(bounty=bounty)

        # Update the related object fields
        related_obj.title = form.cleaned_data['issue_title']
        related_obj.description = form.cleaned_data['issue_description']
        related_obj.language = form.cleaned_data['issue_language']
        related_obj.framework = form.cleaned_data['issue_framework']
        related_obj.issue_url = form.cleaned_data['issue_github_link']
        related_obj.screenshot = form.cleaned_data['issue_screenshot']
        related_obj.save()

        messages.success(self.request, 'Success, Bounty Updated!')

        return redirect('/bounties/')


class BountyDelete(DeleteView,LoginRequiredMixin,):
    """
    Delete a Bounty
    """
    model = Bounty

    def form_invalid(self, form):

        messages.error(self.request, 'Invalid Form', fail_silently=False)

        return render(self.get_context_data(form=form))

    def form_valid(self, form):

        form.save()
        messages.success(self.request, 'Success, Bounty Deleted!')
        return redirect('/bounties/')


class BountyDetailView(LoginRequiredMixin, DetailView):
    model = Bounty
    template_name = 'bounty_detail.html'
    context_object_name = 'bounty'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = BountyHunterSubmissionForm()
        context['num_submissions'] = self.get_num_submissions()
        context['submissions'] = self.object.bountysubmission_set.all()  # Get the related Submission object
        issue = self.object.issue_set  # Get the related Issue object
        context['issues'] = issue
        bug = self.object.bug_set  # Get the related Bug object
        context['bugs'] = bug
        return context

    def get_num_submissions(self):
        num_submissions = BountySubmission.objects.filter(bounty=self.object).count()
        return num_submissions

    def get_submissions(self):
        get_submissions = BountySubmission.objects.filter(bounty=self.object)
        return get_submissions

    def post(self, request, *args, **kwargs):
        bounty_submission_form = BountyHunterSubmissionForm(request.POST)
        if bounty_submission_form.is_valid():
            bounty_submission = bounty_submission_form.save(commit=False)
            bounty_submission.bounty = self.get_object()
            bounty_submission.bounty_hunter = self.request.user.bountyhunter
            bounty_submission.save()
            messages.success(request, 'Your profile has been submitted.')
            return redirect('bounty_detail', pk=kwargs['pk'])
        else:
            messages.error(request, 'Error submitting profile.')
            return redirect('bounty_detail', pk=kwargs['pk'])


from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Bounty, BountySubmission

@login_required
def submit_user_for_bounty(request, bounty_id):
    bounty = get_object_or_404(Bounty, id=bounty_id)
    user = request.user
    
    # Check if user has already submitted for this bounty
    if BountySubmission.objects.filter(bounty=bounty, bounty_hunter=user).exists():
        messages.error(request, "You have already submitted for this bounty.")
        return HttpResponseRedirect(reverse('bounty_detail', args=[bounty_id]))
    
    # Create a new submission for the user and bounty
    submission = BountySubmission.objects.create(bounty=bounty, bounty_hunter=user)
    submission.save()
    
    messages.success(request, "You have successfully submitted for this bounty!")
    return HttpResponseRedirect(reverse('bounty_detail', args=[bounty_id]))


class BountyHunterCreate(CreateView,LoginRequiredMixin,):
    """
    Montior for sites creation
    """
    model = BountyHunter
    template_name = 'hunter_form.html'
    #pre-populate parts of the form
    def get_initial(self):
        initial = {
            'user': self.request.user,
            }

        return initial

    def get_form_kwargs(self):
        kwargs = super(BountyHunterCreate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.save()
        messages.success(self.request, 'Success, Monitored Site Created!')
        return redirect('/hunters/')

    form_class = BountyHunterForm


class BountyHunterUpdate(UpdateView,LoginRequiredMixin,):
    """
    Update and Edit Montiored Site.
    """
    model = BountyHunter
    template_name = 'hunter_form.html'
    form_class = BountyHunterForm

    def get_form_kwargs(self):
        kwargs = super(BountyHunterUpdate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False)
        return render(self.get_context_data(form=form))

    def form_valid(self, form):
        form.instance.url = form.instance.url.replace("http://","")
        form.instance.url = form.instance.url.replace("https://","")
        form.save()
        messages.success(self.request, 'Success, Monitored Site Updated!')

        return redirect('/hunters/')


class BountyHunterDelete(DeleteView,LoginRequiredMixin,):
    """
    Delete a MontiorSite
    """
    model = BountyHunter

    def form_invalid(self, form):

        messages.error(self.request, 'Invalid Form', fail_silently=False)

        return render(self.get_context_data(form=form))

    def form_valid(self, form):

        form.save()
        messages.success(self.request, 'Success, Montior Site Deleted!')
        return redirect('/hunters/')
    

class BountyHunterDetailView(LoginRequiredMixin, DetailView):
    model = BountyHunter
    template_name = 'bountyhunter_detail.html'
    context_object_name = 'bountyhunter'


def accept_bounty(request, bounty_id, submission_id):
    bounty = get_object_or_404(Bounty, id=bounty_id)
    submission = get_object_or_404(BountySubmission, id=submission_id, bounty=bounty)

    # Check if the bounty has already been accepted
    if AcceptedBounty.objects.filter(bounty=bounty).exists():
        messages.warning(request, "This bounty has already been accepted.")
        return redirect(reverse_lazy("bounty_detail", kwargs={"pk": bounty_id}))

    # Check if the user is the owner of the bounty
    if request.user != bounty.owner:
        messages.warning(request, "You do not have permission to accept this bounty.")
        return redirect(reverse_lazy("bounty_detail", kwargs={"pk": bounty_id}))

    # Create a new accepted bounty
    accepted_bounty = AcceptedBounty(bounty=bounty, bounty_hunter=submission.bounty_hunter)
    accepted_bounty.save()

    # Send email to the bounty hunter
    subject = "Bounty accepted!"
    message = render_to_string("email/bounty_accepted.txt", {"bounty": bounty})
    send_mail(subject, message, "admin@example.com", [submission.bounty_hunter.email])

    # Send email to the bounty owner
    subject = "Bounty accepted!"
    message = render_to_string("email/bounty_accepted_owner.txt", {"bounty": bounty})
    send_mail(subject, message, "admin@example.com", [bounty.owner.email])

    messages.success(request, "Bounty accepted!")
    return redirect(reverse_lazy("accepted_bounty_detail", kwargs={"pk": accepted_bounty.pk}))


class AcceptedBountyDetailView(LoginRequiredMixin, DetailView):
    model = AcceptedBounty
    template_name = "accepted_bounty_detail.html"


class CreateContractView(LoginRequiredMixin, CreateView):
    model = Contract
    fields = ["start_date", "end_date"]
    template_name = "contract_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["accepted_bounty"] = get_object_or_404(AcceptedBounty, id=self.kwargs["accepted_bounty_id"])
        return context

    def form_valid(self, form):
        accepted_bounty = get_object_or_404(AcceptedBounty, id=self.kwargs["accepted_bounty_id"])
        contract = form.save(commit=False)
        contract.owner = self.request.user
        contract.bounty_hunter = accepted_bounty.bounty

import re
from difflib import SequenceMatcher

def similar_text(a, b):
    return SequenceMatcher(None, a, b).ratio()

def check_validity(url, description):
    # Check if URL is valid
    url_pattern = r'^(http|https)://'
    if not re.match(url_pattern, url):
        return False

    # Check if bug description is valid
    if len(description.strip()) < 10:  # Example: Description should be at least 10 characters long
        return False

    # Compare with existing bugs to check for similarity
    existing_bugs = Bug.objects.all()  # Assuming you have a Bug model defined
    
    for bug in existing_bugs:
        if similar_text(bug.url, url) > 0.8 or similar_text(bug.description, description) > 0.8:
            return False  # A similar bug already exists in the system
    
    return True

class BugCreateView(CreateView):
    model = Bug
    template_name = 'bug_form.html'
    fields = ['url', 'notes', 'error_message', 'severity', 'name', 'email']
    success_url = '/'  # Replace with the desired URL
    
    def form_valid(self, form):
        check = check_validity(form.instance.url, form.instance.notes)
        if check is True:
            form.save()
            
            # Send Email
            subject = "New Bug!" 
            message = "A new bug form has been submitted"
            send_notification_email(subject, message)
            return redirect('home')
            messages.success(self.request, 'Success, Your Bug has been Submitted!')

        else:
            messages.error(self.request, 'Sorry, that bug or one similar was found in our system already or is invalid.', fail_silently=False)
            return render(self.request, self.template_name, {'form': form})
        return super().form_valid(form)

from .forms import DevelopmentAgencyForm
from .models import DevelopmentAgency

class DevelopmentAgencyCreateView(CreateView):
    model = DevelopmentAgency
    form_class = DevelopmentAgencyForm
    template_name = 'agency_form.html'
    success_url = '/'  # Replace with the desired URL

    def form_valid(self, form):
        agency_name = form.cleaned_data['agency_name']
        # Send Email
        subject = "New Market Agency!" 
        message = "A new form has been submitted by " + str(form.cleaned_data['contact_email'])
        # send_notification_email(subject, message)

        if DevelopmentAgency.objects.filter(agency_name=agency_name).exists():
            error_message = "An agency with the same name already exists."
            return render(self.request, self.template_name, {'form': form, 'error_message': error_message})
        else:
            messages.info("Thank you for Registering your Agency!")
        return super().form_valid(form)


from django.shortcuts import render
import requests  # Import the requests library for making API requests
from .models import Product, InsightsUser

def marketplace(request):
    # Check if the user is authenticated
    if not request.user.is_authenticated:
        messages.info(request, 'Please register for an Insights account at https://insights.buildly.io to access the marketplace.')
        return redirect('home')  # Redirect to the home page with a message

    try:
        # Try to retrieve the InsightsUser object for the authenticated user
        insights_user = InsightsUser.objects.get(user=request.user)
        organization_id = insights_user.insightsorganization_id
    except InsightsUser.DoesNotExist:
        # If the InsightsUser object doesn't exist for the user, redirect with a message
        messages.info(request, 'Please register for an Insights account at https://insights.buildly.io to access the marketplace.')
        return redirect('home')  # Redirect to the home page with a message
    
    # Fetch data from the Buildly Insights API
    organization_id = insights_user.insightsorganization_id
    api_url = f"https://insights-api.buildly.io/product/product?organization_id={organization_id}"
    response = requests.get(api_url)

    if response.status_code == 200:
        product_data = response.json()

        # Create or update Product objects with API data
        for product_info in product_data:
            product, created = Product.objects.get_or_create(product_uuid=product_info['product_uuid'])
            product.name = product_info['name']
            product.description = product_info['description']
            product.product_info = product_info['product_info']
            product.product_uuid = product_info['product_uuid']
            product.organization_uuid = organization_id  # Set organization UUID
            product.product_team = product_info['product_team']  # Set product team UUID
            product.start_date = product_info['start_date']
            product.end_date = product_info['end_date']
            product.create_date = product_info['create_date']
            product.edit_date = product_info['edit_date']
            product.save()

        products = Product.objects.all()
    else:
        products = []

    context = {
        'products': products
    }

    return render(request, 'marketplace_list.html', context)


import requests

def get_insights_user_id_from_api(username, api_url):
    # Define the headers if needed, e.g., for authentication
    headers = {
        'Authorization': 'Bearer YOUR_ACCESS_TOKEN'  # Include any required headers
    }

    # Construct the URL for the CoreUser API endpoint based on the provided `username`
    coreuser_api_url = f"{api_url}/coreuser?username={username}"

    try:
        # Make a GET request to the CoreUser API endpoint
        response = requests.get(coreuser_api_url, headers=headers)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the JSON response
            user_data = response.json()

            # Extract and return the Insights user ID (core_user_uuid)
            return user_data['core_user_uuid']

        # If the request was not successful, handle the error here
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None

    except requests.RequestException as e:
        # Handle any exceptions that may occur during the request
        print(f"Request Exception: {str(e)}")
        return None

# Example usage:
# insights_user_id = get_insights_user_id_from_api('your_username', 'https://insights-api.buildly.io')
# if insights_user_id:
#     print(f"Insights User ID: {insights_user_id}")
# else:
#     print("Failed to fetch Insights User ID")


@login_required
def sour(request):
    # Fetch products from Buildly Insights API
    buildly_insights_api_url = 'https://insights-api.buildly.io/product/product'
    response = requests.get(buildly_insights_api_url)

    if response.status_code == 200:
        product_data = response.json()

        # Extract organization UUID from API response
        organization_uuid = product_data.get('organization_uuid')

        # Assuming you have a method to get Insights user ID, replace this with the actual method
        insights_user_id = get_insights_user_id_from_api()

        # Get or create InsightsUser associated with the Insights user ID
        insights_user, created = InsightsUser.objects.get_or_create(
            user_uuid=insights_user_id,
            defaults={'organization_id': organization_uuid}
        )

        # Map the Insights user to the current user in the Marketplace
        insights_user.user = request.user
        insights_user.save()

        # Create or update Product objects
        product, created = Product.objects.get_or_create(
            product_uuid=product_data['product_uuid'],
            defaults={
                'name': product_data['name'],
                'description': product_data['description'],
                # Set other fields as needed
            }
        )

        return render(request, 'sync_success.html', {'message': 'Products synced successfully.'})
    else:
        return render(request, 'sync_error.html', {'message': 'Failed to sync products.'})
    

from django.shortcuts import render
from .models import DevelopmentAgency, Product

@login_required
def showcase_agencies(request):
    agencies = DevelopmentAgency.objects.all()
    products = Product.objects.all()

    # Fetch selected product based on user choice
    selected_product_id = request.GET.get('product_id')
    selected_product = None
    if selected_product_id:
        try:
            selected_product = Product.objects.get(pk=selected_product_id)
        except Product.DoesNotExist:
            selected_product = None

    # Apply filtering based on user input
    agency_type = request.GET.get('agency_type')
    skills = request.GET.get('skills')
    background = request.GET.get('background')
    industries_worked = request.GET.get('industries_worked')

    filtered_agencies = agencies
    if agency_type:
        filtered_agencies = filtered_agencies.filter(agency_type=agency_type)
    if skills:
        filtered_agencies = filtered_agencies.filter(skills__icontains=skills)
    if background:
        filtered_agencies = filtered_agencies.filter(background__icontains=background)
    if industries_worked:
        filtered_agencies = filtered_agencies.filter(industries_worked=industries_worked)

    context = {
        'agencies': filtered_agencies,
        'products': products,
        'selected_product': selected_product,
        'selected_agency_type': agency_type,
        'selected_skills': skills,
        'selected_background': background,
        'selected_industries_worked': industries_worked,
    }

    return render(request, 'agency_showcase.html', context)


def bug_list(request):
    # Fetch bugs from the database, sorted and grouped by app_name and version
    bugs = Bug.objects.order_by('app_name', 'version')
    bounties = Bounty.objects.all()
    
        # Filter by app_name
    app_name_filter = request.GET.get('app_name')
    if app_name_filter:
        bugs = bugs.filter(app_name=app_name_filter)

    # Filter by version
    version_filter = request.GET.get('version')
    if version_filter:
        bugs = bugs.filter(version=version_filter)

    context = {
        'bugs': bugs,
        'bounties': bounties
    }

    return render(request, 'bugs/bug_list.html', context)


@login_required
def send_to_github(request, pk):
    bug = get_object_or_404(Bug, id=pk)
    message = "Bug Send to GitHub!"
    if request.method == 'POST':
        # Get the selected bounty ID from the form submission
        bounty_id = request.POST.get('assign_to_bounty')

        # Mark the bug as accepted
        bug.is_accepted = True
        bug.save()

        if bounty_id:
            # Get the selected bounty
            bounty = get_object_or_404(Bounty, id=bounty_id)

            # Create an issue associated with the bounty
            issue = Issue.objects.create(
                title=bug.title,
                description=bug.description,
                # Add other fields as needed
                bounty=bounty,
                bug=bug
            )

            # Update the bug with the created issue
            bug.issue = issue
            bug.save()
            message ="Bug Assigned to Bounty"
        else:
            # Create a new bounty
            new_bounty = Bounty(
                title=f"Bounty for Bug: {bug.title}",
                catagory='Bug',
                description=bug.description,
                owner=request.user,
                repo_owner='your_github_username',
                repo='your_repo_name',
                repo_access_token='your_github_access_token',
                status='ACTIVE',  # Change as needed
            )
            new_bounty.save()

            # Create a new issue associated with the bounty
            new_issue = Issue(
                title=bug.title,
                description=bug.description,
                bounty=new_bounty,
                bug=bug
            )
            new_issue.save()
            
            # Update the bug with the created issue
            bug.issue = issue
            bug.save()
            message ="Bug Assigned to a New Bounty"
        messages.info(request, message)
        return redirect(reverse_lazy("bug_list"))

@login_required
def accept_bug(request, pk):
    bug = get_object_or_404(Bug, id=pk)
    message ="Bug Accepted! Please assign to a Bounty in the form below"
    # Update bug status and issue_id
    bug.is_approved = True
    bug.save()
    messages.info(request, message)
    return redirect(reverse_lazy("bug_list"))
