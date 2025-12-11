# onboarding/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate
from django.views.generic import CreateView
from django.db.models import Q
from .forms import TeamMemberRegistrationForm, ResourceForm, TeamMemberUpdateForm, DevelopmentAgencyForm
from .models import TeamMember, Resource, TeamMemberResource,CertificationExam,Quiz, QuizQuestion, QuizAnswer, DevelopmentAgency
from submission.models import SubmissionLink, Submission
from django.contrib import messages
from django.utils.timezone import now
# from punchlist.models import Product


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
            # Redirect to assessment landing page after registration
            messages.info(request, 'Welcome! Please complete your skill assessment to get started.')
            return redirect('onboarding:assessment_landing')
    else:
        form = TeamMemberRegistrationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def edit_profile(request):
    try:
        team_member = TeamMember.objects.get(user=request.user)
    except TeamMember.DoesNotExist:
        return redirect('register')

    if request.method == 'POST':
        form = TeamMemberUpdateForm(request.POST, instance=team_member)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = TeamMemberUpdateForm(instance=team_member)
    
    return render(request, 'edit_profile.html', {'form': form})

@login_required
def dashboard(request):
    try:
        team_member = TeamMember.objects.get(user=request.user)
    except TeamMember.DoesNotExist:
        team_member = None

    # Redirect to assessment if not completed (regardless of approval status)
    if team_member is not None and not team_member.has_completed_assessment:
        messages.info(request, 'Please complete your skill assessment first.')
        return redirect('onboarding:assessment_landing')

    if team_member is not None and not team_member.approved:
        return render(request, 'not_approved.html')

    if team_member is not None:
        resources = Resource.objects.filter(team_member_type=team_member.team_member_type) | Resource.objects.filter(team_member_type='all')
        
        # Add progress data to resources
        for resource in resources:
            # Use filter().first() to handle potential duplicates and get the most recent one
            member_resource = TeamMemberResource.objects.filter(
                team_member=team_member, 
                resource=resource
            ).order_by('-id').first()
            
            if member_resource:
                resource.progress_percentage = member_resource.percentage_complete
            else:
                resource.progress_percentage = 0
        
        member_resource = TeamMemberResource.objects.filter(team_member=team_member)
        certification_exams = CertificationExam.objects.filter(team_member=team_member)
        calendar_embed_code = team_member.google_calendar_embed_code if team_member else None

        qr_codes = SubmissionLink.objects.filter(admin_user=request.user)
        submissions = Submission.objects.filter(submission_link__admin_user=request.user)

        # Fetch links to other team members
        other_team_members = TeamMember.objects.exclude(id=team_member.id)

        # Fetch startups with a status of 'open' - removed punchlist Product reference
        # startups_open = Product.objects.filter(status__in=[
        #     'Planned','Started','Draft','Found'       ])

        return render(request, 'dashboard.html', {
            'resources': resources,
            'qr_codes': qr_codes,
            'submissions': submissions,
            'calendar_embed_code': calendar_embed_code,
            'member_resource': member_resource, 
            'certification_exams': certification_exams,
            'team_member': team_member,
            'other_team_members': other_team_members,
            # 'startups_open': startups_open,
        })
    else:
        return render(request, 'not_approved.html')

@login_required
def upload_resource(request):
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Resource uploaded successfully!')
            return redirect('resource_list')
    else:
        form = ResourceForm()
    return render(request, 'upload_resource.html', {'form': form})

@user_passes_test(lambda u: u.is_superuser)
def resource_list(request):
    resources = Resource.objects.all()
    return render(request, 'resource_list.html', {'resources': resources})


# View all available quizzes
@login_required
def quiz_list(request):
    quizzes = Quiz.objects.filter(available_date__lte=now().date())  # Show only available quizzes
    return render(request, 'quiz/quiz_list.html', {'quizzes': quizzes})

# View quiz questions
@login_required
def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all()
    return render(request, 'quiz/quiz_detail.html', {'quiz': quiz, 'questions': questions})

# Submit quiz answers
@login_required
def submit_answers(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    team_member = get_object_or_404(TeamMember, user=request.user)
    
    if request.method == "POST":
        for question in quiz.questions.all():
            answer_text = request.POST.get(f'question_{question.id}', '').strip()
            if answer_text:
                QuizAnswer.objects.create(question=question, team_member=team_member, answer=answer_text)
        messages.success(request, "Your answers have been submitted successfully!")
        return redirect('quiz_list')

    return render(request, 'quiz/quiz_detail.html', {'quiz': quiz, 'questions': quiz.questions.all()})


# Agency Views
class DevelopmentAgencyCreateView(CreateView):
    model = DevelopmentAgency
    form_class = DevelopmentAgencyForm
    template_name = 'agency_form.html'
    success_url = '/'  # Redirect to homepage after successful registration
    
    def form_valid(self, form):
        agency_name = form.cleaned_data['agency_name']
        # Check if agency already exists
        if DevelopmentAgency.objects.filter(agency_name=agency_name).exists():
            error_message = "An agency with the same name already exists."
            return render(self.request, self.template_name, {'form': form, 'error_message': error_message})
        else:
            messages.info(self.request, "Thank you for registering your agency! We'll be in touch soon.")
        return super().form_valid(form)


def showcase_agencies(request):
    agencies = DevelopmentAgency.objects.all()
    
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
        'selected_agency_type': agency_type,
        'selected_skills': skills,
        'selected_background': background,
        'selected_industries_worked': industries_worked,
        'agency_types': DevelopmentAgency.AGENCY_TYPE,
        'industry_choices': DevelopmentAgency.INDUSTRY_CHOICES,
    }
    return render(request, 'agency_showcase.html', context)


# Assessment Views
@login_required
def assessment_landing(request):
    """Landing page for the developer skill assessment"""
    # Get or create TeamMember if it doesn't exist (for legacy users)
    team_member, created = TeamMember.objects.get_or_create(
        user=request.user,
        defaults={
            'team_member_type': 'community-member-generic',
            'first_name': request.user.first_name or request.user.username,
            'last_name': request.user.last_name or '',
            'email': request.user.email or f'{request.user.username}@example.com',
            'approved': False,
            'has_completed_assessment': False
        }
    )
    
    # Check if already completed
    if team_member.has_completed_assessment:
        return redirect('onboarding:dashboard')
    
    # Increment reminder count
    team_member.assessment_reminder_count += 1
    team_member.assessment_last_reminded = now()
    team_member.save()
    
    context = {
        'reminder_count': team_member.assessment_reminder_count,
    }
    return render(request, 'assessment_landing.html', context)


@login_required
def take_assessment(request):
    """Main view for taking the assessment question by question"""
    # Get or create TeamMember if it doesn't exist (for legacy users)
    team_member, created = TeamMember.objects.get_or_create(
        user=request.user,
        defaults={
            'team_member_type': 'community-member-generic',
            'first_name': request.user.first_name or request.user.username,
            'last_name': request.user.last_name or '',
            'email': request.user.email or f'{request.user.username}@example.com',
            'approved': False,
            'has_completed_assessment': False
        }
    )
    
    # Check if already completed
    if team_member.has_completed_assessment:
        return redirect('onboarding:assessment_complete')
    
    # Get the developer level quiz
    try:
        quiz = Quiz.objects.get(name='Developer Level Assessment')
    except Quiz.DoesNotExist:
        messages.error(request, 'Assessment quiz not found. Please contact support.')
        return redirect('onboarding:dashboard')
    
    # Get all questions ordered
    all_questions = quiz.questions.all().order_by('id')
    total_questions = all_questions.count()
    
    if total_questions == 0:
        messages.error(request, 'No questions available. Please contact support.')
        return redirect('onboarding:dashboard')
    
    # Determine current question (from query param or default to 1)
    current_question_num = int(request.GET.get('question', 1))
    current_question_num = max(1, min(current_question_num, total_questions))
    
    # Get the specific question (1-indexed)
    try:
        question = all_questions[current_question_num - 1]
    except IndexError:
        return redirect(f'{request.path}?question=1')
    
    # Get saved answer if exists
    saved_answer = None
    try:
        existing_answer = QuizAnswer.objects.get(
            team_member=team_member,
            question=question
        )
        saved_answer = existing_answer.answer
    except QuizAnswer.DoesNotExist:
        pass
    
    # Handle form submission
    if request.method == 'POST':
        answer_text = request.POST.get('answer', '').strip()
        action = request.POST.get('action', 'next')
        
        if not answer_text:
            messages.error(request, 'Please provide an answer before continuing.')
            return redirect(f'{request.path}?question={current_question_num}')
        
        # Save or update answer
        QuizAnswer.objects.update_or_create(
            team_member=team_member,
            question=question,
            defaults={
                'answer': answer_text,
                'submitted_at': now()
            }
        )
        
        # Handle different actions
        if action == 'save':
            messages.success(request, 'Answer saved! You can continue later.')
            return redirect('onboarding:dashboard')
        elif action == 'submit' or current_question_num >= total_questions:
            # Mark assessment as complete
            team_member.has_completed_assessment = True
            team_member.assessment_completed_at = now()
            team_member.save()
            
            messages.success(request, 'Assessment submitted successfully!')
            return redirect('onboarding:assessment_complete')
        else:
            # Go to next question
            next_question = current_question_num + 1
            return redirect(f'{request.path}?question={next_question}')
    
    # Prepare context
    progress_percent = int((current_question_num / total_questions) * 100)
    
    context = {
        'question': question,
        'current_question': current_question_num,
        'total_questions': total_questions,
        'progress_percent': progress_percent,
        'saved_answer': saved_answer,
    }
    
    return render(request, 'take_assessment.html', context)


@login_required
def assessment_complete(request):
    """Completion page shown after assessment is submitted"""
    # Get or create TeamMember if it doesn't exist (for legacy users)
    team_member, created = TeamMember.objects.get_or_create(
        user=request.user,
        defaults={
            'team_member_type': 'community-member-generic',
            'first_name': request.user.first_name or request.user.username,
            'last_name': request.user.last_name or '',
            'email': request.user.email or f'{request.user.username}@example.com',
            'approved': False,
            'has_completed_assessment': False
        }
    )
    
    # Redirect to assessment if not completed
    if not team_member.has_completed_assessment:
        return redirect('onboarding:assessment_landing')
    
    # Get quiz stats
    try:
        quiz = Quiz.objects.get(title='Developer Level Assessment')
        answers = QuizAnswer.objects.filter(team_member=team_member, quiz=quiz)
        
        mc_questions = answers.filter(question__question_type='multiple_choice').count()
        essay_questions = answers.filter(question__question_type='essay').count()
        total_questions = answers.count()
    except:
        mc_questions = 15
        essay_questions = 3
        total_questions = 18
    
    context = {
        'total_questions': total_questions,
        'mc_questions': mc_questions,
        'essay_questions': essay_questions,
    }
    
    return render(request, 'assessment_complete.html', context)
