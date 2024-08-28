# onboarding/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate
from .forms import TeamMemberRegistrationForm, ResourceForm
from .models import TeamMember, Resource
from submission.models import SubmissionLink, Submission

def register(request):
    if request.method == 'POST':
        form = TeamMemberRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            team_member = TeamMember(
                user=user,
                team_member_type=form.cleaned_data.get('team_member_type'),
                first_name=form.cleaned_data.get('first_name'),
                last_name=form.cleaned_data.get('last_name'),
                email=form.cleaned_data.get('email'),
                bio=form.cleaned_data.get('bio'),
                linkedin=form.cleaned_data.get('linkedin'),
                experience_years=form.cleaned_data.get('experience_years'),
                github_account=form.cleaned_data.get('github_account'),
            )
            team_member.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('dashboard')
    else:
        form = TeamMemberRegistrationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def dashboard(request):
    team_member = TeamMember.objects.get(user=request.user)
    if not team_member.approved:
        return render(request, 'not_approved.html')

    resources = Resource.objects.filter(team_member_type=team_member.team_member_type) | Resource.objects.filter(team_member_type='all')
    calendar_embed_code = team_member.google_calendar_embed_code
    
    qr_codes = SubmissionLink.objects.filter(admin_user=request.user)
    submissions = Submission.objects.filter(submission_link__admin_user=request.user)

    return render(request, 'dashboard.html', {
        'resources': resources,
        'qr_codes': qr_codes,
        'submissions': submissions,
        'calendar_embed_code': calendar_embed_code
    })

@user_passes_test(lambda u: u.is_superuser)
def upload_resource(request):
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('resource_list')
    else:
        form = ResourceForm()
    return render(request, 'upload_resource.html', {'form': form})

@user_passes_test(lambda u: u.is_superuser)
def resource_list(request):
    resources = Resource.objects.all()
    return render(request, 'resource_list.html', {'resources': resources})


