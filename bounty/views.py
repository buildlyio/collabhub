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


from .models import BountyHunter, Bounty, Issue, BountySubmission, AcceptedBounty, Contract
from .forms import BountyHunterForm, NewBountyForm, BountyForm, BountyHunterSubmissionForm
from .filters import BountyFilter, IssueFilter
import requests

from django.shortcuts import render, redirect


@login_required
def new_bounty(request):
    if request.user.user_type != 'provider':
        messages.error(request, 'You do not have permission to create a new bounty.')
        return redirect('home')

    bounty_form = NewBountyForm(request.user)
    if request.method == 'POST':
        bounty_form = NewBountyForm(request.user, request.POST)
        if bounty_form.is_valid():
            # Create the new bounty object and associate it with the selected issue
            bounty = bounty_form.save(commit=False)
            issue_id = bounty_form.cleaned_data.get('issue_id')
            issue = Issue.objects.get(id=issue_id)
            bounty.issue = issue
            bounty.save()
            messages.success(request, 'Bounty created successfully!')
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
        form.owner = self.request.user
        form.save()
        messages.success(self.request, 'Success, Bounty Created!')
        return redirect('/bounties/')

    form_class = NewBountyForm


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

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False)
        return render(self.get_context_data(form=form))

    def form_valid(self, form):
        form.instance.url = form.instance.url.replace("http://","")
        form.instance.url = form.instance.url.replace("https://","")
        form.save()
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
        context['submissions'] = self.get_submissions()
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
