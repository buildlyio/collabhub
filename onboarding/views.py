# onboarding/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.views.generic import CreateView
from django.db.models import Q, Count, Avg
from .forms import TeamMemberRegistrationForm, ResourceForm, TeamMemberUpdateForm, DevelopmentAgencyForm
from .models import TeamMember, Resource, TeamMemberResource,CertificationExam,Quiz, QuizQuestion, QuizAnswer, DevelopmentAgency, TEAM_MEMBER_TYPES, Customer, CustomerDeveloperAssignment, Contract
from submission.models import SubmissionLink, Submission
from django.contrib import messages
from django.utils.timezone import now
from datetime import timedelta
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
                is_independent=form.cleaned_data.get('is_independent', True),
                agency=form.cleaned_data.get('agency'),
                agency_name_text=form.cleaned_data.get('agency_name_text', ''),
            )
            team_member.save()
            
            # Add profile types if selected
            profile_types = form.cleaned_data.get('profile_types')
            if profile_types:
                team_member.profile_types.set(profile_types)
            
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
    resources = Resource.objects.all().order_by('team_member_type', 'title')
    return render(request, 'resource_list.html', {'resources': resources})


@user_passes_test(lambda u: u.is_superuser)
def resource_create(request):
    if request.method == 'POST':
        team_member_type = request.POST.get('team_member_type')
        title = request.POST.get('title')
        link = request.POST.get('link', '')
        descr = request.POST.get('descr', '')
        document = request.FILES.get('document')
        
        Resource.objects.create(
            team_member_type=team_member_type,
            title=title,
            link=link,
            descr=descr,
            document=document
        )
        messages.success(request, f'Resource "{title}" created successfully!')
        return redirect('onboarding:resource_list')
    
    team_member_types = TEAM_MEMBER_TYPES
    return render(request, 'resource_form.html', {
        'team_member_types': team_member_types,
        'action': 'Create'
    })


@user_passes_test(lambda u: u.is_superuser)
def resource_edit(request, resource_id):
    resource = get_object_or_404(Resource, id=resource_id)
    
    if request.method == 'POST':
        resource.team_member_type = request.POST.get('team_member_type')
        resource.title = request.POST.get('title')
        resource.link = request.POST.get('link', '')
        resource.descr = request.POST.get('descr', '')
        
        if 'document' in request.FILES:
            resource.document = request.FILES['document']
        
        resource.save()
        messages.success(request, f'Resource "{resource.title}" updated successfully!')
        return redirect('onboarding:resource_list')
    
    team_member_types = TEAM_MEMBER_TYPES
    return render(request, 'resource_form.html', {
        'resource': resource,
        'team_member_types': team_member_types,
        'action': 'Edit'
    })


@user_passes_test(lambda u: u.is_superuser)
def resource_delete(request, resource_id):
    resource = get_object_or_404(Resource, id=resource_id)
    
    if request.method == 'POST':
        title = resource.title
        resource.delete()
        messages.success(request, f'Resource "{title}" deleted successfully!')
        return redirect('onboarding:resource_list')
    
    return render(request, 'resource_confirm_delete.html', {'resource': resource})


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
        messages.error(request, 'Assessment quiz not found. Please run "python manage.py create_developer_level_quiz" to create it.')
        return redirect('onboarding:assessment_landing')
    
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


# ============================================================================
# ADMIN VIEWS - Dashboard, Reports, and Management
# ============================================================================

@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    """Main admin dashboard showing overview stats and recent activity"""
    # Get date range for "recent" (last 30 days)
    thirty_days_ago = now() - timedelta(days=30)
    
    # User stats
    total_users = User.objects.count()
    recent_signups = TeamMember.objects.filter(
        user__date_joined__gte=thirty_days_ago
    ).order_by('-user__date_joined')[:10]
    
    # Assessment stats
    completed_assessments = TeamMember.objects.filter(has_completed_assessment=True).count()
    pending_assessments = TeamMember.objects.filter(has_completed_assessment=False).count()
    recent_completions = TeamMember.objects.filter(
        has_completed_assessment=True,
        assessment_completed_at__isnull=False
    ).order_by('-assessment_completed_at')[:10]
    
    # Quiz stats
    total_quizzes = Quiz.objects.count()
    total_questions = QuizQuestion.objects.count()
    total_answers = QuizAnswer.objects.count()
    
    # Evaluation stats
    awaiting_evaluation = QuizAnswer.objects.filter(
        question__question_type='essay',
        evaluator_score__isnull=True
    ).count()
    
    # Team member type distribution
    type_distribution = TeamMember.objects.values('team_member_type').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    context = {
        'total_users': total_users,
        'recent_signups': recent_signups,
        'completed_assessments': completed_assessments,
        'pending_assessments': pending_assessments,
        'recent_completions': recent_completions,
        'total_quizzes': total_quizzes,
        'total_questions': total_questions,
        'total_answers': total_answers,
        'awaiting_evaluation': awaiting_evaluation,
        'type_distribution': type_distribution,
    }
    
    return render(request, 'admin_dashboard.html', context)


@user_passes_test(lambda u: u.is_superuser)
def admin_assessment_reports(request):
    """List all assessment submissions with filtering and search"""
    # Get filter parameters
    quiz_filter = request.GET.get('quiz', '')
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    
    # Get all team members who have submitted answers
    team_members_with_answers = TeamMember.objects.filter(
        quizanswer__isnull=False
    ).distinct()
    
    # Apply filters
    if search_query:
        team_members_with_answers = team_members_with_answers.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(user__username__icontains=search_query)
        )
    
    if status_filter == 'evaluated':
        team_members_with_answers = team_members_with_answers.filter(
            quizanswer__evaluator_score__isnull=False
        ).distinct()
    elif status_filter == 'pending':
        team_members_with_answers = team_members_with_answers.filter(
            quizanswer__question__question_type='essay',
            quizanswer__evaluator_score__isnull=True
        ).distinct()
    
    # Get submission data for each team member
    submissions = []
    for tm in team_members_with_answers:
        answers = QuizAnswer.objects.filter(team_member=tm)
        
        # Get quiz info
        quiz = None
        if answers.exists():
            quiz = answers.first().question.quiz
        
        # Count questions by type
        mc_count = answers.filter(question__question_type='multiple_choice').count()
        essay_count = answers.filter(question__question_type='essay').count()
        
        # Check evaluation status
        essay_answers = answers.filter(question__question_type='essay')
        evaluated_essays = essay_answers.filter(evaluator_score__isnull=False).count()
        
        # AI detection
        ai_flagged = answers.filter(
            ai_detection_score__gte=70
        ).count()
        
        submissions.append({
            'team_member': tm,
            'quiz': quiz,
            'total_answers': answers.count(),
            'mc_count': mc_count,
            'essay_count': essay_count,
            'evaluated_essays': evaluated_essays,
            'ai_flagged': ai_flagged,
            'submitted_at': answers.order_by('-submitted_at').first().submitted_at if answers.exists() else None,
        })
    
    # Sort by submission date (newest first)
    submissions.sort(key=lambda x: x['submitted_at'] or now(), reverse=True)
    
    # Get available quizzes for filter dropdown
    available_quizzes = Quiz.objects.all()
    
    context = {
        'submissions': submissions,
        'available_quizzes': available_quizzes,
        'search_query': search_query,
        'status_filter': status_filter,
        'quiz_filter': quiz_filter,
    }
    
    return render(request, 'admin_assessment_reports.html', context)


@user_passes_test(lambda u: u.is_superuser)
def admin_assessment_review(request, team_member_id):
    """Detailed review of a specific team member's assessment"""
    team_member = get_object_or_404(TeamMember, id=team_member_id)
    
    # Handle evaluation form submission
    if request.method == 'POST':
        answer_id = request.POST.get('answer_id')
        evaluator_score = request.POST.get('evaluator_score')
        evaluator_notes = request.POST.get('evaluator_notes')
        
        if answer_id:
            answer = get_object_or_404(QuizAnswer, id=answer_id)
            answer.evaluator_score = evaluator_score if evaluator_score else None
            answer.evaluator_notes = evaluator_notes
            answer.evaluated_by = request.user
            answer.evaluated_at = now()
            answer.save()
            messages.success(request, 'Evaluation saved successfully.')
            return redirect('onboarding:admin_assessment_review', team_member_id=team_member_id)
    
    # Get all answers for this team member
    answers = QuizAnswer.objects.filter(
        team_member=team_member
    ).select_related('question', 'question__quiz').order_by('question__id')
    
    # Organize by quiz
    quiz_data = {}
    for answer in answers:
        quiz = answer.question.quiz
        if quiz not in quiz_data:
            quiz_data[quiz] = {
                'quiz': quiz,
                'mc_answers': [],
                'essay_answers': [],
            }
        
        if answer.question.question_type == 'multiple_choice':
            quiz_data[quiz]['mc_answers'].append(answer)
        else:
            quiz_data[quiz]['essay_answers'].append(answer)
    
    # Calculate stats
    total_mc = sum(len(data['mc_answers']) for data in quiz_data.values())
    total_essays = sum(len(data['essay_answers']) for data in quiz_data.values())
    evaluated_essays = QuizAnswer.objects.filter(
        team_member=team_member,
        question__question_type='essay',
        evaluator_score__isnull=False
    ).count()
    
    context = {
        'team_member': team_member,
        'quiz_data': quiz_data.values(),
        'total_mc': total_mc,
        'total_essays': total_essays,
        'evaluated_essays': evaluated_essays,
    }
    
    return render(request, 'admin_assessment_review.html', context)


@user_passes_test(lambda u: u.is_superuser)
def admin_quiz_list(request):
    """List all quizzes with management options"""
    quizzes = Quiz.objects.annotate(
        question_count=Count('questions'),
        participant_count=Count('questions__answers__team_member', distinct=True)
    )
    
    # Get additional stats for each quiz
    quiz_stats = []
    for quiz in quizzes:
        mc_questions = QuizQuestion.objects.filter(
            quiz=quiz,
            question_type='multiple_choice'
        ).count()
        
        essay_questions = QuizQuestion.objects.filter(
            quiz=quiz,
            question_type='essay'
        ).count()
        
        quiz_stats.append({
            'quiz': quiz,
            'mc_questions': mc_questions,
            'essay_questions': essay_questions,
            'total_questions': quiz.question_count,
            'participants': quiz.participant_count,
        })
    
    context = {
        'quiz_stats': quiz_stats,
    }
    
    return render(request, 'admin_quiz_list.html', context)


@user_passes_test(lambda u: u.is_superuser)
def admin_quiz_create(request):
    """Create a new quiz"""
    if request.method == 'POST':
        name = request.POST.get('name')
        url = request.POST.get('url')
        available_date = request.POST.get('available_date')
        resource_ids = request.POST.getlist('resources')
        
        if name and url and available_date:
            quiz = Quiz.objects.create(
                name=name,
                url=url,
                available_date=available_date,
                owner=request.user
            )
            # Link selected resources
            if resource_ids:
                quiz.resources.set(resource_ids)
            messages.success(request, f'Quiz "{quiz.name}" created successfully.')
            return redirect('onboarding:admin_quiz_questions', quiz_id=quiz.id)
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    # Get all resources for selection
    resources = Resource.objects.all().order_by('team_member_type', 'title')
    
    context = {
        'action': 'Create',
        'resources': resources,
    }
    return render(request, 'admin_quiz_form.html', context)


@user_passes_test(lambda u: u.is_superuser)
def admin_quiz_edit(request, quiz_id):
    """Edit an existing quiz"""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    if request.method == 'POST':
        quiz.name = request.POST.get('name', quiz.name)
        quiz.url = request.POST.get('url', quiz.url)
        available_date = request.POST.get('available_date')
        if available_date:
            quiz.available_date = available_date
        
        # Update resources
        resource_ids = request.POST.getlist('resources')
        quiz.resources.set(resource_ids)
        
        quiz.save()
        messages.success(request, f'Quiz "{quiz.name}" updated successfully.')
        return redirect('onboarding:admin_quiz_questions', quiz_id=quiz.id)
    
    # Get all resources for selection
    resources = Resource.objects.all().order_by('team_member_type', 'title')
    
    context = {
        'action': 'Edit',
        'quiz': quiz,
        'resources': resources,
    }
    return render(request, 'admin_quiz_form.html', context)


@user_passes_test(lambda u: u.is_superuser)
def admin_quiz_delete(request, quiz_id):
    """Delete a quiz"""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    if request.method == 'POST':
        quiz_name = quiz.name
        quiz.delete()
        messages.success(request, f'Quiz "{quiz_name}" deleted successfully.')
        return redirect('onboarding:admin_quiz_list')
    
    # Get stats for confirmation
    question_count = quiz.questions.count()
    answer_count = QuizAnswer.objects.filter(question__quiz=quiz).count()
    
    context = {
        'quiz': quiz,
        'question_count': question_count,
        'answer_count': answer_count,
    }
    return render(request, 'admin_quiz_confirm_delete.html', context)


@user_passes_test(lambda u: u.is_superuser)
def admin_quiz_questions(request, quiz_id):
    """Manage all questions for a quiz"""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Handle bulk delete
    if request.method == 'POST' and 'bulk_delete' in request.POST:
        question_ids = request.POST.getlist('question_ids')
        if question_ids:
            deleted_count = QuizQuestion.objects.filter(id__in=question_ids, quiz=quiz).delete()[0]
            messages.success(request, f'{deleted_count} question(s) deleted successfully.')
        return redirect('onboarding:admin_quiz_questions', quiz_id=quiz_id)
    
    # Get all questions for this quiz
    questions = QuizQuestion.objects.filter(quiz=quiz).order_by('id')
    
    # Organize questions by type
    mc_questions = questions.filter(question_type='multiple_choice')
    essay_questions = questions.filter(question_type='essay')
    
    context = {
        'quiz': quiz,
        'mc_questions': mc_questions,
        'essay_questions': essay_questions,
        'total_questions': questions.count(),
        'team_member_types': TEAM_MEMBER_TYPES,
    }
    
    return render(request, 'admin_quiz_questions.html', context)


@user_passes_test(lambda u: u.is_superuser)
def admin_question_create(request, quiz_id):
    """Create a new question for a quiz"""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    if request.method == 'POST':
        question_text = request.POST.get('question')
        question_type = request.POST.get('question_type')
        team_member_type = request.POST.get('team_member_type')
        
        if question_text and question_type and team_member_type:
            question = QuizQuestion.objects.create(
                quiz=quiz,
                question=question_text,
                question_type=question_type,
                team_member_type=team_member_type
            )
            messages.success(request, 'Question added successfully.')
            return redirect('onboarding:admin_quiz_questions', quiz_id=quiz_id)
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    context = {
        'action': 'Add',
        'quiz': quiz,
        'team_member_types': TEAM_MEMBER_TYPES,
    }
    return render(request, 'admin_question_form.html', context)


@user_passes_test(lambda u: u.is_superuser)
def admin_question_edit(request, question_id):
    """Edit an existing question"""
    question = get_object_or_404(QuizQuestion, id=question_id)
    
    if request.method == 'POST':
        question.question = request.POST.get('question', question.question)
        question.question_type = request.POST.get('question_type', question.question_type)
        question.team_member_type = request.POST.get('team_member_type', question.team_member_type)
        question.save()
        messages.success(request, 'Question updated successfully.')
        return redirect('onboarding:admin_quiz_questions', quiz_id=question.quiz.id)
    
    context = {
        'action': 'Edit',
        'quiz': question.quiz,
        'question': question,
        'team_member_types': TEAM_MEMBER_TYPES,
    }
    return render(request, 'admin_question_form.html', context)


@user_passes_test(lambda u: u.is_superuser)
def admin_question_delete(request, question_id):
    """Delete a question"""
    question = get_object_or_404(QuizQuestion, id=question_id)
    quiz_id = question.quiz.id
    
    if request.method == 'POST':
        question.delete()
        messages.success(request, 'Question deleted successfully.')
        return redirect('onboarding:admin_quiz_questions', quiz_id=quiz_id)
    
    # Get answer count for confirmation
    answer_count = question.answers.count()
    
    context = {
        'question': question,
        'answer_count': answer_count,
    }
    return render(request, 'admin_question_confirm_delete.html', context)


# ============================================================================
# CUSTOMER PORTAL VIEWS
# ============================================================================

def customer_login(request):
    """Customer login view"""
    from .models import Customer
    from django.utils.timezone import now as timezone_now
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            customer = Customer.objects.get(username=username, is_active=True)
            if customer.check_password(password):
                # Store customer ID in session
                request.session['customer_id'] = customer.id
                customer.last_login = timezone_now()
                customer.save()
                messages.success(request, f'Welcome, {customer.contact_name}!')
                return redirect('onboarding:customer_dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
        except Customer.DoesNotExist:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'customer_login.html')


def customer_logout(request):
    """Customer logout view"""
    if 'customer_id' in request.session:
        del request.session['customer_id']
    messages.success(request, 'You have been logged out successfully.')
    return redirect('onboarding:customer_login')


def customer_required(view_func):
    """Decorator to require customer authentication"""
    def wrapper(request, *args, **kwargs):
        from .models import Customer
        customer_id = request.session.get('customer_id')
        if not customer_id:
            messages.error(request, 'Please log in to access this page.')
            return redirect('onboarding:customer_login')
        try:
            customer = Customer.objects.get(id=customer_id, is_active=True)
            request.customer = customer
            return view_func(request, *args, **kwargs)
        except Customer.DoesNotExist:
            del request.session['customer_id']
            messages.error(request, 'Your session has expired. Please log in again.')
            return redirect('onboarding:customer_login')
    return wrapper


@customer_required
def customer_dashboard(request):
    """Customer dashboard showing assigned developers and contracts"""
    from .models import Contract
    
    customer = request.customer
    developers = customer.assigned_developers.all()
    contracts = customer.contracts.all()
    
    # Get stats
    pending_contracts = contracts.filter(status='pending').count()
    signed_contracts = contracts.filter(status='signed').count()
    
    context = {
        'customer': customer,
        'developers': developers,
        'contracts': contracts,
        'pending_contracts': pending_contracts,
        'signed_contracts': signed_contracts,
    }
    
    return render(request, 'customer_dashboard.html', context)


@customer_required
def customer_developer_detail(request, developer_id):
    """Detailed view of a single developer's profile"""
    customer = request.customer
    developer = get_object_or_404(TeamMember, id=developer_id)
    
    # Verify this developer is assigned to the customer
    if not customer.assigned_developers.filter(id=developer_id).exists():
        messages.error(request, 'You do not have access to this developer profile.')
        return redirect('onboarding:customer_dashboard')
    
    # Get quiz answers for assessment results
    quiz_answers = QuizAnswer.objects.filter(
        team_member=developer
    ).select_related('question__quiz').order_by('-submitted_at')
    
    # Calculate assessment score
    total_questions = quiz_answers.count()
    if total_questions > 0:
        # For MC questions, use is_correct; for essays, use evaluator_score
        mc_correct = quiz_answers.filter(
            question__question_type='multiple_choice',
            is_correct=True
        ).count()
        
        essay_scores = quiz_answers.filter(
            question__question_type='essay',
            evaluator_score__isnull=False
        )
        essay_total = sum([answer.evaluator_score for answer in essay_scores])
        essay_count = essay_scores.count()
        
        # Calculate percentage
        mc_questions = quiz_answers.filter(question__question_type='multiple_choice').count()
        essay_questions = quiz_answers.filter(question__question_type='essay').count()
        
        if mc_questions > 0:
            mc_percentage = (mc_correct / mc_questions) * 100
        else:
            mc_percentage = 0
            
        if essay_count > 0:
            essay_percentage = (essay_total / (essay_count * 10)) * 100  # Assuming 10 is max score
        else:
            essay_percentage = 0
        
        overall_score = (mc_percentage + essay_percentage) / 2 if (mc_questions + essay_questions) > 0 else 0
    else:
        overall_score = 0
    
    # Get resources the developer is working on
    developer_resources = TeamMemberResource.objects.filter(
        team_member=developer
    ).select_related('resource')
    
    context = {
        'customer': customer,
        'developer': developer,
        'quiz_answers': quiz_answers[:10],  # Recent 10 answers
        'overall_score': round(overall_score, 1),
        'total_assessments': quiz_answers.values('question__quiz').distinct().count(),
        'developer_resources': developer_resources,
    }
    
    return render(request, 'customer_developer_detail.html', context)


@customer_required
def customer_contract_view(request, contract_id):
    """View a specific contract"""
    from .models import Contract
    
    customer = request.customer
    contract = get_object_or_404(Contract, id=contract_id, customer=customer)
    
    context = {
        'customer': customer,
        'contract': contract,
    }
    
    return render(request, 'customer_contract_view.html', context)


@customer_required
def customer_contract_sign(request, contract_id):
    """Sign a contract with digital signature"""
    from .models import Contract
    import base64
    
    customer = request.customer
    contract = get_object_or_404(Contract, id=contract_id, customer=customer)
    
    # Only allow signing of pending contracts
    if contract.status != 'pending':
        messages.error(request, 'This contract cannot be signed.')
        return redirect('onboarding:customer_contract_view', contract_id=contract_id)
    
    if request.method == 'POST':
        signature_data = request.POST.get('signature_data')
        signed_by = request.POST.get('signed_by')
        
        if signature_data and signed_by:
            # Save signature
            contract.signature_data = signature_data
            contract.signed_by = signed_by
            contract.signed_at = timezone_now()
            contract.status = 'signed'
            
            # Get IP address
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                contract.ip_address = x_forwarded_for.split(',')[0]
            else:
                contract.ip_address = request.META.get('REMOTE_ADDR')
            
            contract.save()
            
            messages.success(request, 'Contract signed successfully!')
            return redirect('onboarding:customer_contract_view', contract_id=contract_id)
        else:
            messages.error(request, 'Please provide your signature and name.')
    
    context = {
        'customer': customer,
        'contract': contract,
    }
    
    return render(request, 'customer_contract_sign.html', context)


# ============================================================================
# SHAREABLE TOKEN-BASED CUSTOMER PORTAL VIEWS
# ============================================================================

def customer_shared_view(request, token):
    """
    Token-based view for customers to review developers and sign contracts
    No login required - access via unique shareable URL
    """
    from .models import Customer, CustomerDeveloperAssignment, Contract
    
    try:
        customer = Customer.objects.get(share_token=token, is_active=True)
    except Customer.DoesNotExist:
        messages.error(request, 'Invalid or expired access link.')
        return redirect('onboarding:customer_login')
    
    # Get developer assignments with approval status
    assignments = CustomerDeveloperAssignment.objects.filter(
        customer=customer
    ).select_related('developer')
    
    # Get contracts
    contracts = customer.contracts.all()
    pending_contracts = contracts.filter(status='pending')
    signed_contracts = contracts.filter(status='signed')
    
    # Calculate stats
    approved_count = assignments.filter(status='approved').count()
    rejected_count = assignments.filter(status='rejected').count()
    pending_count = assignments.filter(status='pending').count()
    
    context = {
        'customer': customer,
        'assignments': assignments,
        'contracts': contracts,
        'pending_contracts': pending_contracts,
        'signed_contracts': signed_contracts,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'pending_count': pending_count,
        'token': token,
    }
    
    return render(request, 'customer_shared_dashboard.html', context)


def customer_shared_developer_detail(request, token, developer_id):
    """View detailed developer profile via share token"""
    from .models import Customer, CustomerDeveloperAssignment
    
    try:
        customer = Customer.objects.get(share_token=token, is_active=True)
    except Customer.DoesNotExist:
        messages.error(request, 'Invalid or expired access link.')
        return redirect('onboarding:customer_login')
    
    developer = get_object_or_404(TeamMember, id=developer_id)
    
    # Verify developer is assigned to this customer
    try:
        assignment = CustomerDeveloperAssignment.objects.get(
            customer=customer,
            developer=developer
        )
    except CustomerDeveloperAssignment.DoesNotExist:
        messages.error(request, 'You do not have access to this developer profile.')
        return redirect('onboarding:customer_shared_view', token=token)
    
    # Get quiz answers for assessment results
    quiz_answers = QuizAnswer.objects.filter(
        team_member=developer
    ).select_related('question__quiz').order_by('-submitted_at')
    
    # Calculate assessment score (same logic as regular view)
    total_questions = quiz_answers.count()
    if total_questions > 0:
        mc_correct = quiz_answers.filter(
            question__question_type='multiple_choice',
            is_correct=True
        ).count()
        
        essay_scores = quiz_answers.filter(
            question__question_type='essay',
            evaluator_score__isnull=False
        )
        essay_total = sum([answer.evaluator_score for answer in essay_scores])
        essay_count = essay_scores.count()
        
        mc_questions = quiz_answers.filter(question__question_type='multiple_choice').count()
        essay_questions = quiz_answers.filter(question__question_type='essay').count()
        
        if mc_questions > 0:
            mc_percentage = (mc_correct / mc_questions) * 100
        else:
            mc_percentage = 0
            
        if essay_count > 0:
            essay_percentage = (essay_total / (essay_count * 10)) * 100
        else:
            essay_percentage = 0
        
        overall_score = (mc_percentage + essay_percentage) / 2 if (mc_questions + essay_questions) > 0 else 0
    else:
        overall_score = 0
    
    # Get resources
    developer_resources = TeamMemberResource.objects.filter(
        team_member=developer
    ).select_related('resource')
    
    context = {
        'customer': customer,
        'developer': developer,
        'assignment': assignment,
        'quiz_answers': quiz_answers[:10],
        'overall_score': round(overall_score, 1),
        'total_assessments': quiz_answers.values('question__quiz').distinct().count(),
        'developer_resources': developer_resources,
        'token': token,
    }
    
    return render(request, 'customer_shared_developer_detail.html', context)


def customer_shared_approve_developer(request, token, developer_id):
    """Approve a developer via share token"""
    from .models import Customer, CustomerDeveloperAssignment
    
    if request.method != 'POST':
        return redirect('onboarding:customer_shared_view', token=token)
    
    try:
        customer = Customer.objects.get(share_token=token, is_active=True)
    except Customer.DoesNotExist:
        messages.error(request, 'Invalid or expired access link.')
        return redirect('onboarding:customer_login')
    
    try:
        assignment = CustomerDeveloperAssignment.objects.get(
            customer=customer,
            developer_id=developer_id
        )
        assignment.status = 'approved'
        assignment.reviewed_at = timezone_now()
        assignment.notes = request.POST.get('notes', '')
        assignment.save()
        messages.success(request, f'{assignment.developer.first_name} {assignment.developer.last_name} has been approved.')
    except CustomerDeveloperAssignment.DoesNotExist:
        messages.error(request, 'Developer not found.')
    
    return redirect('onboarding:customer_shared_view', token=token)


def customer_shared_reject_developer(request, token, developer_id):
    """Reject a developer via share token"""
    from .models import Customer, CustomerDeveloperAssignment
    
    if request.method != 'POST':
        return redirect('onboarding:customer_shared_view', token=token)
    
    try:
        customer = Customer.objects.get(share_token=token, is_active=True)
    except Customer.DoesNotExist:
        messages.error(request, 'Invalid or expired access link.')
        return redirect('onboarding:customer_login')
    
    try:
        assignment = CustomerDeveloperAssignment.objects.get(
            customer=customer,
            developer_id=developer_id
        )
        assignment.status = 'rejected'
        assignment.reviewed_at = timezone_now()
        assignment.notes = request.POST.get('notes', '')
        assignment.save()
        messages.success(request, f'{assignment.developer.first_name} {assignment.developer.last_name} has been rejected.')
    except CustomerDeveloperAssignment.DoesNotExist:
        messages.error(request, 'Developer not found.')
    
    return redirect('onboarding:customer_shared_view', token=token)


def customer_shared_contract_sign(request, token, contract_id):
    """Sign contract via share token"""
    from .models import Customer, Contract
    import base64
    
    try:
        customer = Customer.objects.get(share_token=token, is_active=True)
    except Customer.DoesNotExist:
        messages.error(request, 'Invalid or expired access link.')
        return redirect('onboarding:customer_login')
    
    contract = get_object_or_404(Contract, id=contract_id, customer=customer)
    
    if contract.status != 'pending':
        messages.error(request, 'This contract cannot be signed.')
        return redirect('onboarding:customer_shared_view', token=token)
    
    if request.method == 'POST':
        signature_data = request.POST.get('signature_data')
        signed_by = request.POST.get('signed_by')
        
        if signature_data and signed_by:
            contract.signature_data = signature_data
            contract.signed_by = signed_by
            contract.signed_at = timezone_now()
            contract.status = 'signed'
            
            # Get IP address
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                contract.ip_address = x_forwarded_for.split(',')[0]
            else:
                contract.ip_address = request.META.get('REMOTE_ADDR')
            
            contract.save()
            
            messages.success(request, 'Contract signed successfully!')
            return redirect('onboarding:customer_shared_view', token=token)
        else:
            messages.error(request, 'Please provide your signature and name.')
    
    context = {
        'customer': customer,
        'contract': contract,
        'token': token,
    }
    
    return render(request, 'customer_shared_contract_sign.html', context)


# ============================================================
# CUSTOM ADMIN DASHBOARD VIEWS
# ============================================================

@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    """Assessment-focused admin dashboard (original)"""
    # Assessment stats
    awaiting_evaluation = QuizAnswer.objects.filter(
        question__question_type='ES',
        evaluator_score__isnull=True
    ).values('team_member').distinct().count()
    
    total_quizzes = Quiz.objects.count()
    
    context = {
        'awaiting_evaluation': awaiting_evaluation,
        'total_quizzes': total_quizzes,
    }
    
    return render(request, 'admin_dashboard.html', context)


@user_passes_test(lambda u: u.is_staff)
def admin_customer_dashboard(request):
    """Customer management admin dashboard (new)"""
    customers = Customer.objects.all().order_by('-created_at')
    developers = TeamMember.objects.filter(approved=True).order_by('-id')
    
    # Stats
    total_customers = customers.count()
    active_customers = customers.filter(is_active=True).count()
    total_developers = developers.count()
    pending_assignments = CustomerDeveloperAssignment.objects.filter(status='pending').count()
    
    context = {
        'customers': customers[:10],  # Recent 10
        'developers': developers[:10],  # Recent 10
        'total_customers': total_customers,
        'active_customers': active_customers,
        'total_developers': total_developers,
        'pending_assignments': pending_assignments,
    }
    
    return render(request, 'admin_dashboard_custom.html', context)


@user_passes_test(lambda u: u.is_staff)
def admin_customers_list(request):
    """List all customers with search and filter"""
    customers = Customer.objects.all().order_by('-created_at')
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        customers = customers.filter(
            Q(company_name__icontains=search_query) |
            Q(contact_name__icontains=search_query) |
            Q(contact_email__icontains=search_query)
        )
    
    # Filter by active status
    status_filter = request.GET.get('status', '')
    if status_filter == 'active':
        customers = customers.filter(is_active=True)
    elif status_filter == 'inactive':
        customers = customers.filter(is_active=False)
    
    # Add assignment counts
    for customer in customers:
        assignments = CustomerDeveloperAssignment.objects.filter(customer=customer)
        customer.total_devs = assignments.count()
        customer.approved_devs = assignments.filter(status='approved').count()
        customer.pending_devs = assignments.filter(status='pending').count()
        customer.rejected_devs = assignments.filter(status='rejected').count()
    
    context = {
        'customers': customers,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    
    return render(request, 'admin_customers_list.html', context)


@user_passes_test(lambda u: u.is_staff)
def admin_customer_detail(request, customer_id):
    """View and edit customer details, assign developers"""
    customer = get_object_or_404(Customer, id=customer_id)
    
    # Get all assignments
    assignments = CustomerDeveloperAssignment.objects.filter(customer=customer).select_related('developer')
    
    # Get available developers (approved and not yet assigned)
    assigned_dev_ids = assignments.values_list('developer_id', flat=True)
    available_developers = TeamMember.objects.filter(approved=True).exclude(id__in=assigned_dev_ids)
    
    # Get contracts
    contracts = Contract.objects.filter(customer=customer).order_by('-created_at')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_customer':
            customer.company_name = request.POST.get('company_name', customer.company_name)
            customer.contact_name = request.POST.get('contact_name', customer.contact_name)
            customer.contact_email = request.POST.get('contact_email', customer.contact_email)
            customer.contact_phone = request.POST.get('contact_phone', customer.contact_phone)
            customer.is_active = request.POST.get('is_active') == 'on'
            customer.notes = request.POST.get('notes', customer.notes)
            customer.save()
            messages.success(request, 'Customer updated successfully!')
            return redirect('onboarding:admin_customer_detail', customer_id=customer.id)
        
        elif action == 'assign_developer':
            developer_id = request.POST.get('developer_id')
            if developer_id:
                developer = get_object_or_404(TeamMember, id=developer_id)
                assignment, created = CustomerDeveloperAssignment.objects.get_or_create(
                    customer=customer,
                    developer=developer
                )
                if created:
                    messages.success(request, f'Assigned {developer.first_name} {developer.last_name} to {customer.company_name}')
                else:
                    messages.warning(request, f'{developer.first_name} {developer.last_name} is already assigned')
                return redirect('onboarding:admin_customer_detail', customer_id=customer.id)
        
        elif action == 'remove_assignment':
            assignment_id = request.POST.get('assignment_id')
            if assignment_id:
                assignment = get_object_or_404(CustomerDeveloperAssignment, id=assignment_id, customer=customer)
                dev_name = f"{assignment.developer.first_name} {assignment.developer.last_name}"
                assignment.delete()
                messages.success(request, f'Removed {dev_name} from {customer.company_name}')
                return redirect('onboarding:admin_customer_detail', customer_id=customer.id)
        
        elif action == 'generate_token':
            customer.generate_share_token()
            messages.success(request, 'Shareable link generated!')
            return redirect('onboarding:admin_customer_detail', customer_id=customer.id)
        
        elif action == 'regenerate_token':
            customer.generate_share_token()
            messages.warning(request, 'Shareable link regenerated! Old link is now invalid.')
            return redirect('onboarding:admin_customer_detail', customer_id=customer.id)
    
    # Generate share URL if token exists
    share_url = None
    if customer.share_token:
        share_url = request.build_absolute_uri(
            f"/onboarding/client/shared/{customer.share_token}/"
        )
    
    context = {
        'customer': customer,
        'assignments': assignments,
        'available_developers': available_developers,
        'contracts': contracts,
        'share_url': share_url,
    }
    
    return render(request, 'admin_customer_detail.html', context)


@user_passes_test(lambda u: u.is_staff)
def admin_developers_list(request):
    """List all developers with search and filter"""
    developers = TeamMember.objects.all().order_by('-id')
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        developers = developers.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Filter by approval status
    approval_filter = request.GET.get('approval', '')
    if approval_filter == 'approved':
        developers = developers.filter(approved=True)
    elif approval_filter == 'pending':
        developers = developers.filter(approved=False)
    
    # Filter by team member type
    type_filter = request.GET.get('type', '')
    if type_filter:
        developers = developers.filter(team_member_type=type_filter)
    
    # Add assignment count
    for dev in developers:
        dev.assignment_count = CustomerDeveloperAssignment.objects.filter(developer=dev).count()
    
    context = {
        'developers': developers,
        'search_query': search_query,
        'approval_filter': approval_filter,
        'type_filter': type_filter,
        'team_member_types': TEAM_MEMBER_TYPES,
    }
    
    return render(request, 'admin_developers_list.html', context)


@user_passes_test(lambda u: u.is_staff)
def admin_developer_profile(request, developer_id):
    """View full developer profile with assessment results"""
    developer = get_object_or_404(TeamMember, id=developer_id)
    
    # Handle approval toggle
    if request.method == 'POST' and request.POST.get('action') == 'toggle_approval':
        developer.approved = not developer.approved
        developer.save()
        status = "approved" if developer.approved else "revoked"
        messages.success(request, f"Developer approval {status} successfully.")
        return redirect('onboarding:admin_developer_profile', developer_id=developer.id)
    
    # Get quiz answers
    quiz_answers = QuizAnswer.objects.filter(
        team_member=developer
    ).select_related('question', 'question__quiz').order_by('-submitted_at')
    
    # Calculate scores
    mc_questions = quiz_answers.filter(question__question_type='MC')
    essay_questions = quiz_answers.filter(question__question_type='ES')
    
    mc_score = 0
    if mc_questions.exists():
        correct_count = mc_questions.filter(is_correct=True).count()
        mc_score = int((correct_count / mc_questions.count()) * 100)
    
    essay_score = 0
    if essay_questions.exists():
        scored_essays = essay_questions.exclude(evaluator_score__isnull=True)
        if scored_essays.exists():
            avg_score = scored_essays.aggregate(Avg('evaluator_score'))['evaluator_score__avg']
            essay_score = int((avg_score / 10) * 100)
    
    overall_score = 0
    if mc_score > 0 or essay_score > 0:
        scores = [s for s in [mc_score, essay_score] if s > 0]
        overall_score = int(sum(scores) / len(scores))
    
    # Get learning resources
    resources = TeamMemberResource.objects.filter(
        team_member=developer
    ).select_related('resource').order_by('-id')
    
    # Get customer assignments
    assignments = CustomerDeveloperAssignment.objects.filter(
        developer=developer
    ).select_related('customer').order_by('-assigned_at')
    
    context = {
        'developer': developer,
        'quiz_answers': quiz_answers,
        'mc_score': mc_score,
        'essay_score': essay_score,
        'overall_score': overall_score,
        'resources': resources,
        'assignments': assignments,
        'total_assessments': quiz_answers.values('question__quiz').distinct().count(),
    }
    
    return render(request, 'admin_developer_profile.html', context)


@user_passes_test(lambda u: u.is_staff)
def admin_customer_create(request):
    """Create a new customer"""
    if request.method == 'POST':
        company_name = request.POST.get('company_name')
        contact_name = request.POST.get('contact_name')
        contact_email = request.POST.get('contact_email')
        contact_phone = request.POST.get('contact_phone', '')
        user_id = request.POST.get('user_id', '')
        is_active = request.POST.get('is_active') == 'on'
        notes = request.POST.get('notes', '')
        
        if company_name and contact_name and contact_email:
            customer = Customer.objects.create(
                company_name=company_name,
                contact_name=contact_name,
                contact_email=contact_email,
                contact_phone=contact_phone,
                is_active=is_active,
                notes=notes
            )
            
            # Link to existing user if selected
            if user_id:
                try:
                    user = User.objects.get(id=user_id)
                    customer.user = user
                    customer.save()
                except User.DoesNotExist:
                    pass
            
            customer.generate_share_token()
            messages.success(request, f'Customer "{company_name}" created successfully!')
            return redirect('onboarding:admin_customer_detail', customer_id=customer.id)
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    # Pass all users for the dropdown
    users = User.objects.all().order_by('username')
    return render(request, 'admin_customer_create.html', {'users': users})


@user_passes_test(lambda u: u.is_staff)
def admin_customer_delete(request, customer_id):
    """Delete a customer"""
    customer = get_object_or_404(Customer, id=customer_id)
    
    if request.method == 'POST':
        company_name = customer.company_name
        customer.delete()
        messages.success(request, f'Customer "{company_name}" deleted successfully!')
        return redirect('onboarding:admin_customers_list')
    
    return redirect('onboarding:admin_customer_detail', customer_id=customer_id)

