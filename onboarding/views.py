# onboarding/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.views.generic import CreateView
from django.db.models import Q, Count, Avg
from django.core.mail import send_mail
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

            # If they are not independent and provided a new agency, send invite email
            if not team_member.is_independent and not team_member.agency and team_member.agency_name_text:
                agency_contact_email = form.cleaned_data.get('agency_contact_email')
                if agency_contact_email:
                    try:
                        send_mail(
                            subject=f"Invitation to join Buildly as an agency - {team_member.agency_name_text}",
                            message=(
                                f"Hello,\n\n"
                                f"{team_member.first_name} {team_member.last_name} listed your agency ("
                                f"{team_member.agency_name_text}) while registering on Buildly.\n\n"
                                f"Please register your agency here to collaborate: https://collab.buildly.io/onboarding/agency/register/\n\n"
                                f"If you have questions, reply to this email."
                            ),
                            from_email=None,
                            recipient_list=[agency_contact_email],
                            fail_silently=True,
                        )
                    except Exception:
                        # Fail silently to avoid blocking registration
                        pass
            
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


# Agency Portal Views
def agency_login(request):
    """Login view for development agencies"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if user has an associated agency
            try:
                agency = DevelopmentAgency.objects.get(user=user)
                if not agency.is_approved:
                    messages.error(request, "Your agency account is pending approval. Please contact support.")
                    return render(request, 'agency_login.html')
                login(request, user)
                return redirect('onboarding:agency_dashboard')
            except DevelopmentAgency.DoesNotExist:
                messages.error(request, "No agency account found for this user.")
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, 'agency_login.html')


def agency_register(request):
    """Registration view for development agencies with user account creation"""
    if request.method == 'POST':
        form = DevelopmentAgencyForm(request.POST, request.FILES)
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        if password != password_confirm:
            messages.error(request, "Passwords do not match.")
            return render(request, 'agency_register.html', {'form': form})
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'agency_register.html', {'form': form})
        
        if form.is_valid():
            # Create user account
            user = User.objects.create_user(
                username=username,
                password=password,
                email=form.cleaned_data['contact_email'],
                first_name=form.cleaned_data['contact_name']
            )
            
            # Create agency and link to user
            agency = form.save(commit=False)
            agency.user = user
            agency.is_approved = False  # Requires admin approval
            agency.save()
            
            messages.success(request, "Thank you for registering! Your agency account is pending approval. We'll notify you once it's approved.")
            return redirect('onboarding:agency_login')
    else:
        form = DevelopmentAgencyForm()
    
    return render(request, 'agency_register.html', {'form': form})


@login_required
def agency_dashboard(request):
    """Dashboard for agencies to view their developers and assignments"""
    try:
        agency = DevelopmentAgency.objects.get(user=request.user)
    except DevelopmentAgency.DoesNotExist:
        messages.error(request, "No agency account found.")
        return redirect('onboarding:agency_login')
    
    if not agency.is_approved:
        messages.warning(request, "Your agency account is pending approval.")
        return render(request, 'agency_dashboard.html', {'agency': agency, 'pending_approval': True})
    
    # Get all developers associated with this agency
    developers = TeamMember.objects.filter(agency=agency).select_related('user')
    
    # Get all customer assignments for agency's developers
    assignments = CustomerDeveloperAssignment.objects.filter(
        developer__agency=agency
    ).select_related('customer', 'developer', 'developer__user').order_by('-assigned_at')
    
    # Calculate stats
    total_developers = developers.count()
    approved_developers = developers.filter(approved=True).count()
    pending_developers = total_developers - approved_developers
    
    total_assignments = assignments.count()
    approved_assignments = assignments.filter(status='approved').count()
    pending_assignments = assignments.filter(status='pending').count()
    active_customers = assignments.values('customer').distinct().count()
    
    context = {
        'agency': agency,
        'developers': developers,
        'assignments': assignments,
        'total_developers': total_developers,
        'approved_developers': approved_developers,
        'pending_developers': pending_developers,
        'total_assignments': total_assignments,
        'approved_assignments': approved_assignments,
        'pending_assignments': pending_assignments,
        'active_customers': active_customers,
    }
    
    return render(request, 'agency_dashboard.html', context)


@login_required
def agency_edit_profile(request):
    """Allow agency to update their own information"""
    try:
        agency = DevelopmentAgency.objects.get(user=request.user)
    except DevelopmentAgency.DoesNotExist:
        messages.error(request, "No agency account found.")
        return redirect('onboarding:agency_login')
    
    if request.method == 'POST':
        form = DevelopmentAgencyForm(request.POST, request.FILES, instance=agency)
        if form.is_valid():
            form.save()
            messages.success(request, "Agency profile updated successfully!")
            return redirect('onboarding:agency_dashboard')
    else:
        form = DevelopmentAgencyForm(instance=agency)
    
    context = {
        'agency': agency,
        'form': form,
    }
    
    return render(request, 'agency_edit_profile.html', context)


@login_required
def agency_logout(request):
    """Logout view for agencies"""
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('onboarding:agency_login')


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
    total_team_members = TeamMember.objects.count()
    
    # Get ALL recent signups (not just [:10]) for accurate count
    recent_signups_queryset = TeamMember.objects.filter(
        user__date_joined__gte=thirty_days_ago
    ).select_related('user').order_by('-user__date_joined')
    
    recent_signups_count = recent_signups_queryset.count()
    recent_signups = recent_signups_queryset[:10]  # Just top 10 for display
    
    # Assessment stats
    completed_assessments = TeamMember.objects.filter(has_completed_assessment=True).count()
    pending_assessments = TeamMember.objects.filter(has_completed_assessment=False).count()
    
    # Get ALL recent completions for accurate count
    recent_completions_queryset = TeamMember.objects.filter(
        has_completed_assessment=True,
        assessment_completed_at__isnull=False
    ).order_by('-assessment_completed_at')
    
    recent_completions_count = recent_completions_queryset.count()
    recent_completions = recent_completions_queryset[:10]  # Just top 10 for display
    
    # Quiz stats
    total_quizzes = Quiz.objects.count()
    total_questions = QuizQuestion.objects.count()
    total_answers = QuizAnswer.objects.count()
    
    # Evaluation stats
    awaiting_evaluation = QuizAnswer.objects.filter(
        question__question_type='essay',
        evaluator_score__isnull=True
    ).count()
    
    # Team member type distribution - using the ManyToMany 'types' field
    type_distribution = TeamMemberType.objects.annotate(
        count=Count('team_members')
    ).order_by('-count')[:10]
    
    context = {
        'total_users': total_users,
        'total_team_members': total_team_members,
        'recent_signups': recent_signups,
        'recent_signups_count': recent_signups_count,
        'completed_assessments': completed_assessments,
        'pending_assessments': pending_assessments,
        'recent_completions': recent_completions,
        'recent_completions_count': recent_completions_count,
        'total_quizzes': total_quizzes,
        'total_questions': total_questions,
        'total_answers': total_answers,
        'awaiting_evaluation': awaiting_evaluation,
        'type_distribution': type_distribution,
        'thirty_days_ago': thirty_days_ago,  # For debugging
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
    total_questions = 0
    total_participants = 0
    
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
        
        total_questions += quiz.question_count
        total_participants += quiz.participant_count
    
    # Calculate average questions per quiz
    avg_questions_per_quiz = round(total_questions / len(quiz_stats)) if quiz_stats else 0
    
    context = {
        'quiz_stats': quiz_stats,
        'total_questions': total_questions,
        'total_participants': total_participants,
        'avg_questions_per_quiz': avg_questions_per_quiz,
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
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            customer = Customer.objects.get(username=username, is_active=True)
            if customer.check_password(password):
                # Store customer ID in session
                request.session['customer_id'] = customer.id
                customer.last_login = now()
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
    
    # Calculate assessment score (essay evaluator_score is a 0-4 rubric)
    total_questions = quiz_answers.count()
    mc_total = quiz_answers.filter(question__question_type='multiple_choice').count()
    essay_total = quiz_answers.filter(question__question_type='essay').count()

    overall_score = 0
    if total_questions > 0:
        essay_scores = quiz_answers.filter(
            question__question_type='essay',
            evaluator_score__isnull=False
        )
        essay_count = essay_scores.count()

        if essay_count > 0:
            avg_score = sum([answer.evaluator_score for answer in essay_scores]) / essay_count
            essay_percentage = (avg_score / 4) * 100  # Convert 0-4 rubric to percentage
            overall_score = essay_percentage
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
        'essay_score': round(overall_score, 1),
        'mc_score': 0,
        'total_assessments': quiz_answers.values('question__quiz').distinct().count(),
        'developer_resources': developer_resources,
        'mc_total': mc_total,
        'essay_total': essay_total,
        'total_questions': total_questions,
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
            contract.signed_at = now()
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
    import logging
    from .models import Customer, CustomerDeveloperAssignment
    
    logger = logging.getLogger('collabhub.views')
    logger.info(f"🔍 customer_shared_developer_detail called - token={token}, developer_id={developer_id}")
    
    try:
        # Step 1: Get customer by share token
        logger.debug(f"Step 1: Looking up customer with token={token}")
        customer = Customer.objects.get(share_token=token, is_active=True)
        logger.info(f"✓ Found customer: {customer.id} - {customer.company_name}")
    except Customer.DoesNotExist as e:
        logger.warning(f"❌ Customer not found with token={token}: {e}")
        messages.error(request, 'Invalid or expired access link.')
        return redirect('onboarding:customer_login')
    
    try:
        # Step 2: Get developer
        logger.debug(f"Step 2: Looking up developer with id={developer_id}")
        developer = get_object_or_404(TeamMember, id=developer_id)
        logger.info(f"✓ Found developer: {developer.id} - {developer.first_name} {developer.last_name}")
    except Exception as e:
        logger.error(f"❌ Error getting developer {developer_id}: {e}", exc_info=True)
        raise
    
    try:
        # Step 3: Verify developer is assigned to this customer
        logger.debug(f"Step 3: Verifying assignment - customer={customer.id}, developer={developer.id}")
        assignment = CustomerDeveloperAssignment.objects.get(
            customer=customer,
            developer=developer
        )
        logger.info(f"✓ Assignment verified")
    except CustomerDeveloperAssignment.DoesNotExist as e:
        logger.warning(f"❌ No assignment found for customer={customer.id}, developer={developer.id}: {e}")
        messages.error(request, 'You do not have access to this developer profile.')
        return redirect('onboarding:customer_shared_view', token=token)
    
    try:
        # Step 4: Get quiz answers for assessment results
        logger.debug(f"Step 4: Querying quiz answers for developer={developer.id}")
        quiz_answers = QuizAnswer.objects.filter(
            team_member=developer
        ).select_related('question__quiz').order_by('-submitted_at')
        logger.info(f"✓ Found {quiz_answers.count()} quiz answers")
        
        # Step 5: Calculate assessment score (essay evaluator_score is 0-4 rubric)
        logger.debug(f"Step 5: Calculating assessment scores")
        total_questions = quiz_answers.count()
        mc_total = quiz_answers.filter(question__question_type='multiple_choice').count()
        essay_total = quiz_answers.filter(question__question_type='essay').count()
        overall_score = 0
        if total_questions > 0:
            essay_scores = quiz_answers.filter(
                question__question_type='essay',
                evaluator_score__isnull=False
            )
            essay_count = essay_scores.count()
            if essay_count > 0:
                avg_score = sum([answer.evaluator_score for answer in essay_scores]) / essay_count
                essay_percentage = (avg_score / 4) * 100  # 0-4 rubric → percentage
                overall_score = essay_percentage
                logger.info(f"✓ Assessment scores - Essay: {essay_percentage:.1f}%, Overall: {overall_score:.1f}% ({essay_count}/{essay_total} essays graded)")
            else:
                overall_score = 0
                logger.info(f"✓ No graded assessments available ({essay_total} essay questions answered but not yet graded)")
        else:
            overall_score = 0
            logger.info(f"✓ No assessment scores available")
        
        # Step 6: Get resources
        logger.debug(f"Step 6: Getting developer resources")
        developer_resources = TeamMemberResource.objects.filter(
            team_member=developer
        ).select_related('resource')
        logger.info(f"✓ Found {developer_resources.count()} resources")
        
        # Step 7: Build context and render
        logger.debug(f"Step 7: Building context for template render")
        context = {
            'customer': customer,
            'developer': developer,
            'assignment': assignment,
            'quiz_answers': quiz_answers[:10],
            'overall_score': round(overall_score, 1),
            'essay_score': round(overall_score, 1),
            'mc_score': 0,
            'total_assessments': quiz_answers.values('question__quiz').distinct().count(),
            'developer_resources': developer_resources,
            'token': token,
            'mc_total': mc_total,
            'essay_total': essay_total,
            'total_questions': total_questions,
        }
        logger.info(f"✓ Context prepared, about to render template")
        
        response = render(request, 'customer_shared_developer_detail.html', context)
        logger.info(f"✅ Successfully rendered customer_shared_developer_detail page")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error in customer_shared_developer_detail: {e}", exc_info=True)
        raise


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
        assignment.reviewed_at = now()
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
        assignment.reviewed_at = now()
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
            contract.signed_at = now()
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
    from datetime import timedelta
    from django.utils import timezone
    
    # Assessment stats - use correct 'essay' value
    awaiting_evaluation = QuizAnswer.objects.filter(
        question__question_type='essay',
        evaluator_score__isnull=True
    ).values('team_member').distinct().count()
    
    total_quizzes = Quiz.objects.count()
    total_developers = TeamMember.objects.filter(approved=True).count()
    completed_assessments = TeamMember.objects.filter(has_completed_assessment=True).count()
    pending_developers = TeamMember.objects.filter(approved=False).count()
    
    # User stats
    total_users = User.objects.count()
    total_team_members = TeamMember.objects.count()
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_signups_count = TeamMember.objects.filter(user__date_joined__gte=thirty_days_ago).count()
    
    # Content stats
    total_questions = QuizQuestion.objects.count()
    total_answers = QuizAnswer.objects.count()
    pending_assessments = TeamMember.objects.filter(has_completed_assessment=False).count()
    
    # Recent signups for list
    recent_signups = TeamMember.objects.select_related('user').order_by('-user__date_joined')[:5]
    
    context = {
        'awaiting_evaluation': awaiting_evaluation,
        'total_quizzes': total_quizzes,
        'total_developers': total_developers,
        'completed_assessments': completed_assessments,
        'pending_developers': pending_developers,
        'total_users': total_users,
        'total_team_members': total_team_members,
        'recent_signups_count': recent_signups_count,
        'total_questions': total_questions,
        'total_answers': total_answers,
        'pending_assessments': pending_assessments,
        'recent_signups': recent_signups,
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
    
    # Handle skill level updates
    if request.method == 'POST' and request.POST.get('action') == 'update_skills':
        from onboarding.models import TechnologySkill
        for tech in ['javascript', 'python', 'typescript', 'nodejs', 'kubernetes', 'git', 'bash']:
            skill_level = request.POST.get(f'skill_{tech}')
            if skill_level:
                TechnologySkill.objects.update_or_create(
                    team_member=developer,
                    technology=tech,
                    defaults={'skill_level': int(skill_level)}
                )
        messages.success(request, "Technology skills updated successfully.")
        return redirect('onboarding:admin_developer_profile', developer_id=developer.id)
    
    # Get quiz answers - using all() to ensure queryset is evaluated
    quiz_answers = QuizAnswer.objects.filter(
        team_member=developer
    ).select_related('question', 'question__quiz').order_by('-submitted_at')
    
    # Calculate scores - note: question_type is 'multiple_choice' or 'essay', not 'MC' or 'ES'
    mc_questions = quiz_answers.filter(question__question_type='multiple_choice')
    essay_questions = quiz_answers.filter(question__question_type='essay')
    
    mc_score = 0
    mc_total = mc_questions.count()
    # Note: MC questions don't have an is_correct field, they're just stored as text answers
    # So MC score calculation would need to compare against correct answers or be manually evaluated
    
    essay_score = 0
    essay_total = essay_questions.count()
    if essay_total > 0:
        scored_essays = essay_questions.exclude(evaluator_score__isnull=True)
        if scored_essays.exists():
            avg_score = scored_essays.aggregate(Avg('evaluator_score'))['evaluator_score__avg']
            # evaluator_score uses 0-4 rubric; convert to percentage for display
            essay_score = int((avg_score / 4) * 100) if avg_score else 0
    
    # For overall score, we can only use evaluated answers
    all_evaluated = quiz_answers.exclude(evaluator_score__isnull=True)
    overall_score = 0
    if all_evaluated.exists():
        avg_score = all_evaluated.aggregate(Avg('evaluator_score'))['evaluator_score__avg']
        overall_score = int((avg_score / 4) * 100) if avg_score else 0
    
    # Count total quiz answers for debugging
    total_answers = quiz_answers.count()
    
    # Get learning resources
    resources = TeamMemberResource.objects.filter(
        team_member=developer
    ).select_related('resource').order_by('-id')
    
    # Get customer assignments
    assignments = CustomerDeveloperAssignment.objects.filter(
        developer=developer
    ).select_related('customer').order_by('-assigned_at')
    
    # Get technology skills
    from onboarding.models import TechnologySkill
    tech_skills = TechnologySkill.objects.filter(team_member=developer).order_by('technology')
    
    # Create dict of existing skills for easy lookup
    skills_dict = {skill.technology: skill for skill in tech_skills}
    
    # Primary technologies we want to track
    primary_techs = ['javascript', 'python', 'typescript', 'nodejs', 'kubernetes', 'git', 'bash']
    
    context = {
        'developer': developer,
        'quiz_answers': quiz_answers,
        'mc_score': mc_score,
        'essay_score': essay_score,
        'overall_score': overall_score,
        'resources': resources,
        'assignments': assignments,
        'total_assessments': quiz_answers.values('question__quiz').distinct().count(),
        'total_answers': total_answers,
        'mc_total': mc_total,
        'essay_total': essay_total,
        'tech_skills': tech_skills,
        'skills_dict': skills_dict,
        'primary_techs': primary_techs,
    }
    
    return render(request, 'admin_developer_profile.html', context)


@user_passes_test(lambda u: u.is_staff)
def sync_github_skills(request, developer_id):
    """Sync technology skills from GitHub"""
    import requests
    from django.utils import timezone
    from onboarding.models import TechnologySkill
    
    developer = get_object_or_404(TeamMember, id=developer_id)
    github_username = developer.get_github_username()
    
    if not github_username:
        messages.error(request, "No GitHub account linked for this developer.")
        return redirect('onboarding:admin_developer_profile', developer_id=developer.id)
    
    try:
        # Get repos from GitHub API
        response = requests.get(f'https://api.github.com/users/{github_username}/repos', timeout=10)
        response.raise_for_status()
        repos = response.json()
        
        # Technology mapping
        tech_mapping = {
            'javascript': ['JavaScript'],
            'python': ['Python'],
            'typescript': ['TypeScript'],
            'bash': ['Shell'],
        }
        
        # Count repos per technology
        tech_counts = {tech: 0 for tech in tech_mapping.keys()}
        tech_counts['nodejs'] = 0
        tech_counts['kubernetes'] = 0
        tech_counts['git'] = len(repos)  # All repos use git
        
        for repo in repos:
            if repo.get('language'):
                lang = repo['language']
                for tech, langs in tech_mapping.items():
                    if lang in langs:
                        tech_counts[tech] += 1
            
            # Check for Node.js (look for package.json indicator)
            if repo.get('language') == 'JavaScript':
                tech_counts['nodejs'] += 1
            
            # Check for Kubernetes (repos with k8s in name or description)
            repo_name = repo.get('name', '').lower()
            repo_desc = repo.get('description', '').lower() if repo.get('description') else ''
            if 'kubernetes' in repo_name or 'k8s' in repo_name or 'kubernetes' in repo_desc:
                tech_counts['kubernetes'] += 1
        
        # Calculate skill levels (1-5 scale)
        def calculate_level(count):
            if count == 0:
                return 0
            elif count <= 2:
                return 2
            elif count <= 5:
                return 3
            elif count <= 10:
                return 4
            else:
                return 5
        
        # Update or create TechnologySkill records
        updated_count = 0
        for tech, count in tech_counts.items():
            if count > 0:
                calculated_level = calculate_level(count)
                skill, created = TechnologySkill.objects.get_or_create(
                    team_member=developer,
                    technology=tech,
                    defaults={
                        'skill_level': calculated_level,
                        'github_calculated_level': calculated_level,
                        'github_repos_count': count,
                        'last_github_sync': timezone.now()
                    }
                )
                if not created:
                    # Update GitHub data but keep manual skill_level if set
                    skill.github_calculated_level = calculated_level
                    skill.github_repos_count = count
                    skill.last_github_sync = timezone.now()
                    # Only update skill_level if not manually set (i.e., if it matches old calculated level)
                    if skill.skill_level == skill.github_calculated_level or skill.skill_level <= 1:
                        skill.skill_level = calculated_level
                    skill.save()
                updated_count += 1
        
        messages.success(request, f"Successfully synced skills from GitHub! Updated {updated_count} technologies.")
    except requests.RequestException as e:
        messages.error(request, f"Failed to fetch GitHub data: {str(e)}")
    except Exception as e:
        messages.error(request, f"Error syncing GitHub skills: {str(e)}")
    
    return redirect('onboarding:admin_developer_profile', developer_id=developer.id)


@user_passes_test(lambda u: u.is_staff)
def admin_customer_create(request):
    """Create a new customer"""
    if request.method == 'POST':
        company_name = request.POST.get('company_name')
        contact_name = request.POST.get('contact_name')
        contact_email = request.POST.get('contact_email')
        contact_phone = request.POST.get('contact_phone', '')
        is_active = request.POST.get('is_active') == 'on'
        notes = request.POST.get('notes', '')
        
        if company_name and contact_name and contact_email:
            # Generate unique username from email
            username = contact_email.split('@')[0]
            base_username = username
            counter = 1
            while Customer.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            customer = Customer.objects.create(
                company_name=company_name,
                contact_name=contact_name,
                contact_email=contact_email,
                contact_phone=contact_phone,
                username=username,
                password='',
                is_active=is_active,
                notes=notes
            )
            
            # Generate shareable token
            token = customer.generate_share_token()
            messages.success(request, f'Customer "{company_name}" created successfully with shareable link!')
            return redirect('onboarding:admin_customer_detail', customer_id=customer.id)
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    return render(request, 'admin_customer_create.html', {})


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

