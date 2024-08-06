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
from .models import Punchlist
from .forms import PunchlistHunterSubmissionForm
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .labs import get_labs_data

from .models import PunchlistHunter, Punchlist, Issue, PunchlistSubmission, AcceptedPunchlist, Contract, Bug, InsightsUser, Product
from .forms import PunchlistHunterForm, PunchlistForm, PunchlistHunterSubmissionForm, BugForm
from .filters import PunchlistFilter, IssueFilter
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
def new_punchlist(request):
    if request.user.user_type != 'provider':
        messages.error(request, 'You do not have permission to create a new punchlist.')
        return redirect('home')

    punchlist_form = PunchlistForm(request.user)
    if request.method == 'POST':
        punchlist_form = PunchlistForm(request.user, request.POST)
        if punchlist_form.is_valid():
            # Create the new punchlist object and associate it with the selected issue
            punchlist = punchlist_form.save(commit=False)
            issue_id = punchlist_form.cleaned_data.get('issue_id')
            issue = Issue.objects.get(id=issue_id)
            punchlist.issue = issue
            punchlist.save()
            messages.success(request, 'Punchlist created successfully!')
            
            # Send Email
            subject = "New Bug Punchlist!" 
            message = "A new form has been submitted"
            send_notification_email(subject, message)
            return redirect('home')
    
    return render(request, 'new_punchlist.html', {'punchlist_form': punchlist_form})


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

    getReport = Punchlist.objects.all().filter(id=pk)

    return render(request, 'dashboard.html', {'getReport': getReport, })


@login_required(login_url='/')
def report(request,pk):

    getReport = Punchlist.objects.all().filter(id=pk)
    getHunt = PunchlistHunter.objects.get(pk=pk)

    return render(request, 'report.html', {'getReport': getReport, 'id': pk})


class PunchlistFilterView(FilterView):
    model = Punchlist
    filterset_class = PunchlistFilter
    template_name = 'punchlist_filter.html'
    paginate_by = 16  # Display 16 items per page
    ordering = ['-create_date']  # Order by most recent

def punchlist_detail(request, punchlist_id):
    punchlist = Punchlist.objects.get(id=punchlist_id)
    return render(request, 'punchlist_detail.html', {'punchlist': punchlist})


class PunchlistList(ListView,LoginRequiredMixin):
    """
    Monitored Sites
    """
    # call get labs data to import data from Labs/Insights API
    get_labs_data()
    print("Data Imported")
    model = Punchlist
    template_name = 'punchlist_list.html'
    paginate_by = 16  # Display 16 items per page
    ordering = ['-create_date']  # Order by most recent
    

class PunchlistCreate(CreateView,LoginRequiredMixin,):
    """
    Montior for sites creation
    """
    model = Punchlist
    template_name = 'punchlist_form.html'
    #pre-populate parts of the form
    def get_initial(self):
        initial = {
            'user': self.request.user,
            }

        return initial

    def get_form_kwargs(self):
        kwargs = super(PunchlistCreate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):

        punchlist = form.save(commit=False)
        punchlist.owner = self.request.user
        punchlist.save()

         # Get or create the related object (RelatedObject)
        related_obj, _  = Issue.objects.get_or_create(punchlist=punchlist)

        # Update the related object fields
        related_obj.title = form.cleaned_data['issue_title']
        related_obj.description = form.cleaned_data['issue_description']
        related_obj.language = form.cleaned_data['issue_language']
        related_obj.framework = form.cleaned_data['issue_framework']
        related_obj.issue_url = form.cleaned_data['issue_github_link']
        related_obj.screenshot = form.cleaned_data['issue_screenshot']
        related_obj.save()
        
        messages.success(self.request, 'Success, Punchlist Created!')
        return redirect('/bounties/')

    form_class = PunchlistForm


class PunchlistUpdate(UpdateView,LoginRequiredMixin,):
    """
    Update and Edit Montiored Site.
    """
    model = Punchlist
    template_name = 'punchlist_form.html'
    form_class = PunchlistForm

    def get_form_kwargs(self):
        kwargs = super(PunchlistUpdate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Retrieve the related object instance
        punchlist = self.get_object()

        try:
            related_obj = Issue.objects.get(punchlist=punchlist)
            
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
        # Save the main object (Punchlist)
        punchlist = form.save()

        # Get or create the related object (RelatedObject)
        related_obj, _  = Issue.objects.get_or_create(punchlist=punchlist)

        # Update the related object fields
        related_obj.title = form.cleaned_data['issue_title']
        related_obj.description = form.cleaned_data['issue_description']
        related_obj.language = form.cleaned_data['issue_language']
        related_obj.framework = form.cleaned_data['issue_framework']
        related_obj.issue_url = form.cleaned_data['issue_github_link']
        related_obj.screenshot = form.cleaned_data['issue_screenshot']
        related_obj.save()

        messages.success(self.request, 'Success, Punchlist Updated!')

        return redirect('/bounties/')


class PunchlistDelete(DeleteView,LoginRequiredMixin,):
    """
    Delete a Punchlist
    """
    model = Punchlist

    def form_invalid(self, form):

        messages.error(self.request, 'Invalid Form', fail_silently=False)

        return render(self.get_context_data(form=form))

    def form_valid(self, form):

        form.save()
        messages.success(self.request, 'Success, Punchlist Deleted!')
        return redirect('/bounties/')


class PunchlistDetailView(LoginRequiredMixin, DetailView):
    model = Punchlist
    template_name = 'punchlist_detail.html'
    context_object_name = 'punchlist'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PunchlistHunterSubmissionForm()
        context['num_submissions'] = self.get_num_submissions()
        context['submissions'] = self.object.punchlistsubmission_set.all()  # Get the related Submission object
        issue = self.object.issue_set  # Get the related Issue object
        context['issues'] = issue
        bug = Bug.objects.all().filter(punchlist=self.object)  # Get the related Bug object
        context['bugs'] = bug
        return context

    def get_num_submissions(self):
        num_submissions = PunchlistSubmission.objects.filter(punchlist=self.object).count()
        return num_submissions

    def get_submissions(self):
        get_submissions = PunchlistSubmission.objects.filter(punchlist=self.object)
        return get_submissions

    def post(self, request, *args, **kwargs):
        punchlist_submission_form = PunchlistHunterSubmissionForm(request.POST)
        if punchlist_submission_form.is_valid():
            punchlist_submission = punchlist_submission_form.save(commit=False)
            punchlist_submission.punchlist = self.get_object()
            punchlist_submission.punchlist_hunter = self.request.user.punchlisthunter
            punchlist_submission.save()
            messages.success(request, 'Your profile has been submitted.')
            return redirect('punchlist_detail', pk=kwargs['pk'])
        else:
            messages.error(request, 'Error submitting profile.')
            return redirect('punchlist_detail', pk=kwargs['pk'])


from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Punchlist, PunchlistSubmission

@login_required
def submit_user_for_punchlist(request, punchlist_id):
    punchlist = get_object_or_404(Punchlist, id=punchlist_id)
    user = request.user
    
    # Check if user has already submitted for this punchlist
    if PunchlistSubmission.objects.filter(punchlist=punchlist, punchlist_hunter=user).exists():
        messages.error(request, "You have already submitted for this punchlist.")
        return HttpResponseRedirect(reverse('punchlist_detail', args=[punchlist_id]))
    
    # Create a new submission for the user and punchlist
    submission = PunchlistSubmission.objects.create(punchlist=punchlist, punchlist_hunter=user)
    submission.save()
    
    messages.success(request, "You have successfully submitted for this punchlist!")
    return HttpResponseRedirect(reverse('punchlist_detail', args=[punchlist_id]))


class PunchlistHunterCreate(CreateView,LoginRequiredMixin,):
    """
    Montior for sites creation
    """
    model = PunchlistHunter
    template_name = 'hunter_form.html'
    #pre-populate parts of the form
    def get_initial(self):
        initial = {
            'user': self.request.user,
            }

        return initial

    def get_form_kwargs(self):
        kwargs = super(PunchlistHunterCreate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.save()
        messages.success(self.request, 'Success, Monitored Site Created!')
        return redirect('/hunters/')

    form_class = PunchlistHunterForm


class PunchlistHunterUpdate(UpdateView,LoginRequiredMixin,):
    """
    Update and Edit Montiored Site.
    """
    model = PunchlistHunter
    template_name = 'hunter_form.html'
    form_class = PunchlistHunterForm

    def get_form_kwargs(self):
        kwargs = super(PunchlistHunterUpdate, self).get_form_kwargs()
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


class PunchlistHunterDelete(DeleteView,LoginRequiredMixin,):
    """
    Delete a MontiorSite
    """
    model = PunchlistHunter

    def form_invalid(self, form):

        messages.error(self.request, 'Invalid Form', fail_silently=False)

        return render(self.get_context_data(form=form))

    def form_valid(self, form):

        form.save()
        messages.success(self.request, 'Success, Montior Site Deleted!')
        return redirect('/hunters/')
    

class PunchlistHunterDetailView(LoginRequiredMixin, DetailView):
    model = PunchlistHunter
    template_name = 'punchlisthunter_detail.html'
    context_object_name = 'punchlisthunter'


def accept_punchlist(request, punchlist_id, submission_id):
    punchlist = get_object_or_404(Punchlist, id=punchlist_id)
    submission = get_object_or_404(PunchlistSubmission, id=submission_id, punchlist=punchlist)

    # Check if the punchlist has already been accepted
    if AcceptedPunchlist.objects.filter(punchlist=punchlist).exists():
        messages.warning(request, "This punchlist has already been accepted.")
        return redirect(reverse_lazy("punchlist_detail", kwargs={"pk": punchlist_id}))

    # Check if the user is the owner of the punchlist
    if request.user != punchlist.owner:
        messages.warning(request, "You do not have permission to accept this punchlist.")
        return redirect(reverse_lazy("punchlist_detail", kwargs={"pk": punchlist_id}))

    # Create a new accepted punchlist
    accepted_punchlist = AcceptedPunchlist(punchlist=punchlist, punchlist_hunter=submission.punchlist_hunter)
    accepted_punchlist.save()

    # Send email to the punchlist hunter
    subject = "Punchlist accepted!"
    message = render_to_string("email/punchlist_accepted.txt", {"punchlist": punchlist})
    send_mail(subject, message, "admin@example.com", [submission.punchlist_hunter.email])

    # Send email to the punchlist owner
    subject = "Punchlist accepted!"
    message = render_to_string("email/punchlist_accepted_owner.txt", {"punchlist": punchlist})
    send_mail(subject, message, "admin@example.com", [punchlist.owner.email])

    messages.success(request, "Punchlist accepted!")
    return redirect(reverse_lazy("accepted_punchlist_detail", kwargs={"pk": accepted_punchlist.pk}))


class AcceptedPunchlistDetailView(LoginRequiredMixin, DetailView):
    model = AcceptedPunchlist
    template_name = "accepted_punchlist_detail.html"


class CreateContractView(LoginRequiredMixin, CreateView):
    model = Contract
    fields = ["start_date", "end_date"]
    template_name = "contract_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["accepted_punchlist"] = get_object_or_404(AcceptedPunchlist, id=self.kwargs["accepted_punchlist_id"])
        return context

    def form_valid(self, form):
        accepted_punchlist = get_object_or_404(AcceptedPunchlist, id=self.kwargs["accepted_punchlist_id"])
        contract = form.save(commit=False)
        contract.owner = self.request.user
        contract.punchlist_hunter = accepted_punchlist.punchlist

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
            messages.info(self.request, "Thank you for Registering your Agency!")
        return super().form_valid(form)


from django.shortcuts import render
import requests  # Import the requests library for making API requests
from .models import Product, InsightsUser

def collabhub(request):
    # Check if the user is authenticated
    if not request.user.is_authenticated:
        messages.info(request, 'Please register for an Insights account at https://insights.buildly.io to access the collabhub.')
        return redirect('home')  # Redirect to the home page with a message

    try:
        # Try to retrieve the InsightsUser object for the authenticated user
        insights_user = InsightsUser.objects.get(user=request.user)
        organization_id = insights_user.insightsorganization_id
    except InsightsUser.DoesNotExist:
        # If the InsightsUser object doesn't exist for the user, redirect with a message
        messages.info(request, 'Please register for an Insights account at https://insights.buildly.io to access the collabhub.')
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

    return render(request, 'collabhub_list.html', context)


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

        # Map the Insights user to the current user in the CollabHub
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
    bounties = Punchlist.objects.all()
    
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
    message = "Bug Sent to GitHub!"
    if request.method == 'POST':
        # Get the selected punchlist ID from the form submission
        punchlist_id = request.POST.get('assign_to_punchlist')

        # Mark the bug as accepted
        bug.is_accepted = True
        bug.save()

        if punchlist_id:
            # Get the selected punchlist
            punchlist = get_object_or_404(Punchlist, id=punchlist_id)

            # Update the bug with the created issue
            bug.punchlist = punchlist
            bug.save()
            message ="Bug Assigned to Punchlist"
        else:
            # Create a new punchlist
            new_punchlist = Punchlist(
                title=f"Punchlist for Bug: {bug.title}",
                catagory='Bug',
                description=bug.description,
                owner=request.user,
                repo_owner='your_github_username',
                repo='your_repo_name',
                repo_access_token='your_github_access_token',
                status='ACTIVE',  # Change as needed
            )
            new_punchlist.save()
            
            # Update the bug with the created punchlist
            bug.punchlist = punchlist
            bug.save()
            message ="Bug Assigned to a New Punchlist"
        messages.info(request, message)
        return redirect(reverse_lazy("bug_list"))

@login_required
def accept_bug(request, pk):
    bug = get_object_or_404(Bug, id=pk)
    message ="Bug Accepted! Please assign to a Punchlist in the form below"
    # Update bug status and issue_id
    bug.is_approved = True
    bug.save()
    messages.info(request, message)
    return redirect(reverse_lazy("bug_list"))

@login_required
def submit_issue_to_github(request, pk):
    submit_to_github(request=request, object_type="issue", pk=pk)
    obj = Issue.objects.get(pk=pk)
    return redirect("punchlist_detail", pk=obj.punchlist.id)

@login_required
def submit_bug_to_github(request, pk):
    submit_to_github(request=request, object_type="bug", pk=pk)
    obj = Bug.objects.get(pk=pk)
    return redirect("punchlist_detail", pk=obj.punchlist.id)

@login_required
def submit_to_github(request, object_type, pk):
    # Determine the model based on object_type (issue or bug)
    if object_type == "issue":
        model_class = Issue
    elif object_type == "bug":
        model_class = Bug
    else:
        return redirect("punchlist_list")  # Handle invalid object_type

    try:
        # Get the object (issue or bug) by its ID
        obj = model_class.objects.get(pk=pk)

        if request.method == "POST":
            # Retrieve GitHub Token from the associated Punchlist
            punchlist = Punchlist.objects.get(id=obj.punchlist.id)
            github_token = punchlist.repo_access_token

            github_repo = request.POST.get("github_repo")  # Get the selected GitHub repo from the form


            # Construct the GitHub API endpoint for creating an issue
            api_url = f"https://api.github.com/repos/{github_repo}/issues"
            if object_type == "issue":
                # Define the issue payload
                description = f"DESCRIPTION: {obj.description} \n COLLAB ISSUE URL: {obj.issue_number} : {obj.issue_url} \n Compexity: {obj.complexity_estimate} \n ENVRIONMENT: {obj.hosting_environment}"
                issue_payload = {
                    "title": obj.title,
                    "body": obj.description,
                    # add other fields as needed
                }
            else:
                # Define the bug payload
                description = f"DESCRIPTION: {obj.description} \n ERROR MESSAGE: {obj.error_message} \n EXPECTED BEHAVIOUR: {obj.expected_behaviour} \n STEPS TO REPRODUCE: {obj.steps_to_reproduce} \n SEVERITY: {obj.severity} \n APP NAME: {obj.app_name} \n VERSION: {obj.version} \n COLLAB BUG URL {obj.url}  \n IS USER SUBMITTED: {obj.is_user_submitted} \n IS APPROVED: {obj.is_approved}"
                issue_payload = {
                    "title": obj.title,
                    "body": description,
                    "labels": ["bug"],
                    # add other fields as needed
                }

            headers = {
                "Authorization": f"Bearer {github_token}",
                "Accept": "application/vnd.github.v3+json",
            }

            try:
                # Send a POST request to create the issue on GitHub
                response = requests.post(api_url, json=issue_payload, headers=headers)

                if response.status_code == 201:
                    # Issue created successfully
                    messages.success(request, "Issue submitted to GitHub successfully.")
                    
                    # update status works for both issue and bug
                    obj.is_tracked = True
                    obj.url = response.json().get("url")
                    obj.save()
                else:
                    # Handle GitHub API error
                    messages.error(
                        request, f"Failed to submit issue to GitHub. Status code: {response.status_code}"
                    )
            except Exception as e:
                # Handle exceptions
                messages.error(request, f"An error occurred: {str(e)}")

            return redirect("punchlist_detail", pk=obj.punchlist.id)

        context = {
            "object": obj,
            "object_type": object_type,
        }

        return render(request, "submit_to_github.html", context)

    except model_class.DoesNotExist:
        return redirect("punchlist_list")  # Handle non-existing object