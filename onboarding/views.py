# onboarding/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.views.generic import CreateView
from django.db.models import Q, Count, Avg
from django.core.mail import send_mail
from .forms import TeamMemberRegistrationForm, ResourceForm, TeamMemberUpdateForm, DevelopmentAgencyForm
from .models import TeamMember, TeamMemberType, Resource, TeamMemberResource,CertificationExam,Quiz, QuizQuestion, QuizAnswer, DevelopmentAgency, TEAM_MEMBER_TYPES, Customer, CustomerDeveloperAssignment, Contract, TeamTraining, DeveloperTrainingEnrollment, DeveloperTeam
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

        # Fetch contracts for company admins
        contracts = []
        company_admin = None
        try:
            company_admin = CompanyAdmin.objects.get(user=request.user)
            # Get contracts for this company admin's customer
            contracts = Contract.objects.filter(
                customer=company_admin.customer
            ).order_by('-created_at')
        except CompanyAdmin.DoesNotExist:
            pass
        
        # Fetch certificates for this developer
        from .models import DeveloperCertification
        developer_certifications = DeveloperCertification.objects.filter(
            developer=team_member
        ).select_related('certification_level')

        return render(request, 'dashboard.html', {
            'resources': resources,
            'qr_codes': qr_codes,
            'submissions': submissions,
            'calendar_embed_code': calendar_embed_code,
            'member_resource': member_resource, 
            'certification_exams': certification_exams,
            'team_member': team_member,
            'other_team_members': other_team_members,
            'contracts': contracts,
            'company_admin': company_admin,
            'developer_certifications': developer_certifications,
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

@user_passes_test(lambda u: u.is_superuser)
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
    recent_signups = TeamMember.objects.select_related('user').prefetch_related('profile_types').order_by('-user__date_joined')[:5]
    
    # Recent assessment completions (team members who completed assessment, ordered by completion date)
    recent_completions = TeamMember.objects.filter(
        has_completed_assessment=True,
        assessment_completed_at__isnull=False
    ).select_related('user').prefetch_related('profile_types').order_by('-assessment_completed_at')[:10]
    
    # Community Members (approved developers) for new section
    # Use approved=True to show all approved developers, not just community_approval_date
    approved_developers = TeamMember.objects.filter(
        approved=True
    ).select_related('user').prefetch_related('profile_types').order_by('-id')[:10]
    total_community_members = TeamMember.objects.filter(approved=True).count()
    
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
        'recent_completions': recent_completions,
        'approved_developers': approved_developers,
        'total_community_members': total_community_members,
    }
    
    return render(request, 'admin_dashboard.html', context)


@user_passes_test(lambda u: u.is_superuser)
def admin_intake_requests(request):
    """List intake requests for superusers"""
    from .models import CustomerIntakeRequest
    status_filter = request.GET.get('status')
    allowed_statuses = [choice[0] for choice in CustomerIntakeRequest.STATUS_CHOICES]
    requests_qs = CustomerIntakeRequest.objects.select_related('assigned_to', 'customer').order_by('-created_at')
    if status_filter in allowed_statuses:
        requests_qs = requests_qs.filter(status=status_filter)
    status_counts = {status: CustomerIntakeRequest.objects.filter(status=status).count() for status in allowed_statuses}
    context = {
        'requests': requests_qs,
        'status_filter': status_filter,
        'status_choices': CustomerIntakeRequest.STATUS_CHOICES,
        'status_counts': status_counts,
    }
    return render(request, 'admin_intake_requests.html', context)


@user_passes_test(lambda u: u.is_superuser)
def admin_intake_request_detail(request, intake_id):
    """Detail view and actions for a single intake request"""
    from .models import CustomerIntakeRequest
    intake = get_object_or_404(CustomerIntakeRequest, pk=intake_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'assign_me':
            intake.assigned_to = request.user
            if intake.status == 'new':
                intake.status = 'in_review'
            intake.save()
            messages.success(request, 'Assigned to you and moved to In Review.')
        elif action == 'mark_in_review':
            if intake.status == 'new':
                intake.status = 'in_review'
            if not intake.assigned_to:
                intake.assigned_to = request.user
            intake.save()
            messages.success(request, 'Request marked as In Review.')
        elif action == 'mark_contacted':
            intake.mark_contacted(request.user)
            messages.success(request, 'Marked as Contacted.')
        elif action == 'convert':
            customer = intake.convert_to_customer()
            if customer:
                messages.success(request, 'Converted to Customer record.')
            else:
                messages.warning(request, 'Request cannot be converted from current status.')
        elif action == 'reject':
            intake.status = 'rejected'
            intake.save()
            messages.info(request, 'Request rejected.')
        return redirect('onboarding:admin_intake_request_detail', intake_id=intake.id)
    context = {
        'intake': intake,
        'status_choices': CustomerIntakeRequest.STATUS_CHOICES,
    }
    return render(request, 'admin_intake_request_detail.html', context)


@user_passes_test(lambda u: u.is_superuser)
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


@user_passes_test(lambda u: u.is_superuser)
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


@user_passes_test(lambda u: u.is_superuser)
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
        
        elif action == 'update_assignment_status':
            assignment_id = request.POST.get('assignment_id')
            new_status = request.POST.get('status')
            if assignment_id and new_status in ['pending', 'approved', 'rejected']:
                assignment = get_object_or_404(CustomerDeveloperAssignment, id=assignment_id, customer=customer)
                assignment.status = new_status
                assignment.reviewed_at = now() if new_status in ['approved', 'rejected'] else None
                assignment.save(update_fields=['status', 'reviewed_at'])
                messages.success(request, f'Updated assignment status to {new_status}')
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


@user_passes_test(lambda u: u.is_superuser)
def admin_contract_create(request, customer_id):
    """Create a new contract for a customer"""
    customer = get_object_or_404(Customer, id=customer_id)
    
    # Get approved developers for this customer
    approved_assignments = CustomerDeveloperAssignment.objects.filter(
        customer=customer,
        status='approved'
    ).select_related('developer')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        contract_text = request.POST.get('contract_text', '')
        contract_type = request.POST.get('contract_type', 'engagement')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        hourly_rate = request.POST.get('hourly_rate') or None
        project_rate = request.POST.get('project_rate') or None
        developer_ids = request.POST.getlist('developers')
        
        contract = Contract.objects.create(
            customer=customer,
            title=title,
            contract_text=contract_text,
            contract_type=contract_type,
            start_date=start_date,
            end_date=end_date,
            hourly_rate=hourly_rate,
            project_rate=project_rate,
            status='draft',
            created_by=request.user
        )
        
        # Add developers
        if developer_ids:
            developers = TeamMember.objects.filter(id__in=developer_ids)
            contract.developers.set(developers)
        
        # Process line items from form
        from .models import ContractLineItem
        line_item_count = 0
        while f'line_items[{line_item_count}][service_type]' in request.POST:
            service_type = request.POST.get(f'line_items[{line_item_count}][service_type]')
            description = request.POST.get(f'line_items[{line_item_count}][description]')
            quantity = request.POST.get(f'line_items[{line_item_count}][quantity]', 1)
            unit_price = request.POST.get(f'line_items[{line_item_count}][unit_price]', 0)
            billing_frequency = request.POST.get(f'line_items[{line_item_count}][billing_frequency]', 'monthly')
            discount_percentage = request.POST.get(f'line_items[{line_item_count}][discount_percentage]', 0)
            notes = request.POST.get(f'line_items[{line_item_count}][notes]', '')
            
            if service_type and description:
                ContractLineItem.objects.create(
                    contract=contract,
                    service_type=service_type,
                    description=description,
                    quantity=quantity,
                    unit_price=unit_price,
                    billing_frequency=billing_frequency,
                    discount_percentage=discount_percentage,
                    notes=notes
                )
            
            line_item_count += 1
        
        messages.success(request, f'Contract "{title}" created successfully!')
        return redirect('onboarding:admin_customer_detail', customer_id=customer.id)
    
    context = {
        'customer': customer,
        'approved_assignments': approved_assignments,
        'contract_types': Contract.CONTRACT_TYPE,
    }
    
    return render(request, 'admin_contract_create.html', context)


@user_passes_test(lambda u: u.is_superuser)
def admin_contract_edit(request, contract_id):
    """Edit an existing contract"""
    contract = get_object_or_404(Contract, id=contract_id)
    customer = contract.customer
    
    # Get approved developers for this customer
    approved_assignments = CustomerDeveloperAssignment.objects.filter(
        customer=customer,
        status='approved'
    ).select_related('developer')
    
    if request.method == 'POST':
        contract.title = request.POST.get('title', contract.title)
        contract.contract_text = request.POST.get('contract_text', contract.contract_text)
        contract.contract_type = request.POST.get('contract_type', contract.contract_type)
        contract.start_date = request.POST.get('start_date', contract.start_date)
        contract.end_date = request.POST.get('end_date', contract.end_date)
        contract.hourly_rate = request.POST.get('hourly_rate') or None
        contract.project_rate = request.POST.get('project_rate') or None
        contract.status = request.POST.get('status', contract.status)
        
        developer_ids = request.POST.getlist('developers')
        if developer_ids:
            developers = TeamMember.objects.filter(id__in=developer_ids)
            contract.developers.set(developers)
        
        contract.save()
        messages.success(request, f'Contract "{contract.title}" updated successfully!')
        return redirect('onboarding:admin_customer_detail', customer_id=customer.id)
    
    context = {
        'contract': contract,
        'customer': customer,
        'approved_assignments': approved_assignments,
        'contract_types': Contract.CONTRACT_TYPE,
        'contract_statuses': Contract.CONTRACT_STATUS,
    }
    
    return render(request, 'admin_contract_edit.html', context)


@user_passes_test(lambda u: u.is_superuser)
def admin_contract_delete(request, contract_id):
    """Delete a contract"""
    if request.method != 'POST':
        return redirect('onboarding:admin_customers_list')
    
    contract = get_object_or_404(Contract, id=contract_id)
    customer_id = contract.customer.id
    contract_title = contract.title
    
    contract.delete()
    messages.success(request, f'Contract "{contract_title}" deleted successfully!')
    return redirect('onboarding:admin_customer_detail', customer_id=customer_id)


@user_passes_test(lambda u: u.is_superuser)
@user_passes_test(lambda u: u.is_superuser)
def admin_developers_list(request):
    """Unified admin developer management with search, filters, and approval"""
    from onboarding.models import DeveloperTeam, DeveloperTrainingEnrollment, Quiz
    developers = TeamMember.objects.all().prefetch_related('tech_skills', 'types', 'profile_types', 'developer_teams').order_by('-id')
    # Annotate each developer with approval status, team, and profile/quiz/training links
    developer_list = []
    for dev in developers:
        # Approval status
        if dev.community_approval_date:
            approval_status = 'approved'
        elif dev.approved:
            approval_status = 'legacy'
        else:
            approval_status = 'pending'
        # Team (first team or None)
        team = dev.developer_teams.first()
        team_name = team.name if team else None
        # Profile URL
        from django.urls import reverse
        profile_url = reverse('onboarding:admin_developer_profile', args=[dev.id])
        # Quizzes: link to profile with anchor
        quizzes_url = f"{profile_url}#assessmentDetails"
        # Trainings: link to profile with anchor
        trainings_url = f"{profile_url}#resources"
        developer_list.append({
            'id': dev.id,
            'first_name': dev.first_name,
            'last_name': dev.last_name,
            'email': dev.email,
            'github_account': dev.get_github_username() or '',
            'experience_years': dev.experience_years,
            'tech_skills': dev.tech_skills.all(),
            'user': dev.user,
            'approval_status': approval_status,
            'team': team_name,
            'profile_url': profile_url,
            'quizzes_url': quizzes_url,
            'trainings_url': trainings_url,
            'community_approval_date': dev.community_approval_date,
            'approved': dev.approved,
            'types': dev.types.all(),
        })
    # ...existing code...
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        developer_list = [d for d in developer_list if search_query.lower() in (d['first_name'].lower() + d['last_name'].lower() + d['email'].lower() + (d['github_account'] or '').lower())]
    
    # Filter by approval status
    approval_filter = request.GET.get('approval', '')
    if approval_filter:
        developer_list = [d for d in developer_list if d['approval_status'] == approval_filter]
    
    # Filter by team member type
    type_filter = request.GET.get('type', '')
    if type_filter:
        developer_list = [d for d in developer_list if any(t.key == type_filter for t in d['types'])]
    
    # Filter by experience level
    exp_filter = request.GET.get('experience', '')
    if exp_filter == 'junior':
        developer_list = [d for d in developer_list if d['experience_years'] and d['experience_years'] < 3]
    elif exp_filter == 'mid':
        developer_list = [d for d in developer_list if d['experience_years'] and 3 <= d['experience_years'] < 7]
    elif exp_filter == 'senior':
        developer_list = [d for d in developer_list if d['experience_years'] and d['experience_years'] >= 7]
    
    # Filter by affiliation
    affiliation_filter = request.GET.get('affiliation', '')
    if affiliation_filter == 'independent':
        developer_list = [d for d in developer_list if getattr(TeamMember.objects.get(id=d['id']), 'is_independent', True)]
    elif affiliation_filter == 'agency':
        developer_list = [d for d in developer_list if not getattr(TeamMember.objects.get(id=d['id']), 'is_independent', True)]
    
    # Sort by last name, first name
    developer_list = sorted(developer_list, key=lambda d: (d['last_name'], d['first_name']))

    # Get unique types for filter dropdown
    all_types = TeamMemberType.objects.all().order_by('label')

    context = {
        'developers': developer_list,
        'search_query': search_query,
        'approval_filter': approval_filter,
        'type_filter': type_filter,
        'exp_filter': exp_filter,
        'affiliation_filter': affiliation_filter,
        'all_types': all_types,
    }

    return render(request, 'admin_developers_list.html', context)


@user_passes_test(lambda u: u.is_superuser)
def admin_developer_profile(request, developer_id):
    """View full developer profile with assessment results and approval options"""
    developer = get_object_or_404(TeamMember, id=developer_id)

    # Default assignments to prevent UnboundLocalError
    quiz_answers = QuizAnswer.objects.none()
    mc_score = 0
    essay_score = 0
    overall_score = 0
    resources = TeamMemberResource.objects.none()
    assignments = CustomerDeveloperAssignment.objects.none()
    total_assessments = 0
    total_answers = 0
    mc_total = 0
    essay_total = 0
    tech_skills = []
    skills_dict = {}
    primary_techs = ['javascript', 'python', 'typescript', 'nodejs', 'kubernetes', 'git', 'bash']
    all_types = TeamMemberType.objects.none()

    # Handle community approval
    if request.method == 'POST' and request.POST.get('action') == 'approve_community':
        profile_type_key = request.POST.get('profile_type')
        if not profile_type_key:
            messages.error(request, 'Please select a profile type before approving.')
            return redirect('onboarding:admin_developer_profile', developer_id=developer.id)
        
        profile_type = TeamMemberType.objects.filter(key=profile_type_key).first()
        if not profile_type:
            messages.error(request, 'Invalid profile type selected.')
            return redirect('onboarding:admin_developer_profile', developer_id=developer.id)
        
        if developer.community_approval_date:
            messages.warning(request, f'{developer.first_name} {developer.last_name} is already approved.')
            return redirect('onboarding:admin_developer_profile', developer_id=developer.id)
        
        if profile_type not in developer.profile_types.all():
            developer.profile_types.add(profile_type)
        
        # Approve developer
        developer.community_approval_date = now()
        developer.community_approved_by = request.user
        developer.approved = True
        developer.save(update_fields=['community_approval_date', 'community_approved_by', 'approved'])

        # Auto-assign to Buildly customer if not already assigned
        buildly_customer = Customer.objects.filter(company_name__icontains='Buildly').first()
        if buildly_customer:
            already_assigned = CustomerDeveloperAssignment.objects.filter(customer=buildly_customer, developer=developer).exists()
            if not already_assigned:
                CustomerDeveloperAssignment.objects.create(
                    customer=buildly_customer,
                    developer=developer,
                    status='approved',
                    reviewed_at=now(),
                    notes='Auto-assigned on community approval.'
                )
        # Send email notification
        send_community_approval_email(developer)
        
        # Create in-app notification
        Notification.objects.create(
            recipient=developer.user,
            notification_type='community_approved',
            title='Welcome to Buildly Open Source Community!',
            message=f'Your profile has been approved! You now have access to community trainings, certifications, and can be evaluated for job openings.',
            is_read=False
        )
        
        messages.success(request, f'{developer.first_name} {developer.last_name} approved successfully!')
        return redirect('onboarding:admin_developer_profile', developer_id=developer.id)
    
    # Handle approval toggle (legacy)
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
    
    # Handle assessment reminder
    if request.method == 'POST' and request.POST.get('action') == 'send_reminder':
        from onboarding.utils import send_assessment_reminder_email
        
        # Increment reminder count
        developer.assessment_reminder_count += 1
        developer.assessment_last_reminded = now()
        developer.save(update_fields=['assessment_reminder_count', 'assessment_last_reminded'])
        
        # Send the reminder email
        send_assessment_reminder_email(developer, developer.assessment_reminder_count)
        
        if developer.assessment_reminder_count >= 3:
            messages.warning(request, f"Final reminder (#{developer.assessment_reminder_count}) sent to {developer.first_name} {developer.last_name}. Consider removing if no response.")
        else:
            messages.success(request, f"Reminder #{developer.assessment_reminder_count} sent to {developer.first_name} {developer.last_name}.")
        return redirect('onboarding:admin_developer_profile', developer_id=developer.id)
    
    # Handle member deletion
    if request.method == 'POST' and request.POST.get('action') == 'delete_member':
        developer_name = f"{developer.first_name} {developer.last_name}"
        user = developer.user
        
        # Delete the TeamMember first (cascade will handle related objects)
        developer.delete()
        
        # Deactivate the associated user account
        if user:
            user.is_active = False
            user.save()
        
        messages.success(request, f"{developer_name} has been removed from the system.")
        return redirect('onboarding:admin_approval_queue')
    
    # Get quiz answers - using all() to ensure queryset is evaluated
    quiz_answers = QuizAnswer.objects.filter(
        team_member=developer
    ).select_related('question', 'question__quiz').order_by('-submitted_at')

    # Calculate scores - note: question_type is 'multiple_choice' or 'essay', not 'MC' or 'ES'
    mc_questions = quiz_answers.filter(question__question_type='multiple_choice')
    essay_questions = quiz_answers.filter(question__question_type='essay')

    mc_total = mc_questions.count()
    essay_total = essay_questions.count()

    if mc_total > 0:
        # If you have a way to calculate MC score, do it here
        pass

    if essay_total > 0:
        scored_essays = essay_questions.exclude(evaluator_score__isnull=True)
        if scored_essays.exists():
            avg_score = scored_essays.aggregate(Avg('evaluator_score'))['evaluator_score__avg']
            essay_score = int((avg_score / 4) * 100) if avg_score else 0

    # For overall score, we can only use evaluated answers
    all_evaluated = quiz_answers.exclude(evaluator_score__isnull=True)
    if all_evaluated.exists():
        avg_score = all_evaluated.aggregate(Avg('evaluator_score'))['evaluator_score__avg']
        overall_score = int((avg_score / 4) * 100) if avg_score else 0

    total_answers = quiz_answers.count()
    resources = TeamMemberResource.objects.filter(
        team_member=developer
    ).select_related('resource').order_by('-id')
    assignments = CustomerDeveloperAssignment.objects.filter(
        developer=developer
    ).select_related('customer').order_by('-assigned_at')
    from onboarding.models import TechnologySkill
    tech_skills = TechnologySkill.objects.filter(team_member=developer).order_by('technology')
    skills_dict = {skill.technology: skill for skill in tech_skills}
    all_types = TeamMemberType.objects.all().order_by('label')
    total_assessments = quiz_answers.values('question__quiz').distinct().count()

    context = {
        'developer': developer,
        'quiz_answers': quiz_answers,
        'mc_score': mc_score,
        'essay_score': essay_score,
        'overall_score': overall_score,
        'resources': resources,
        'assignments': assignments,
        'total_assessments': total_assessments,
        'total_answers': total_answers,
        'mc_total': mc_total,
        'essay_total': essay_total,
        'tech_skills': tech_skills,
        'skills_dict': skills_dict,
        'primary_techs': primary_techs,
        'all_types': all_types,
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


@user_passes_test(lambda u: u.is_superuser)
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


@user_passes_test(lambda u: u.is_superuser)
def admin_customer_delete(request, customer_id):
    """Delete a customer"""
    customer = get_object_or_404(Customer, id=customer_id)
    
    if request.method == 'POST':
        company_name = customer.company_name
        customer.delete()
        messages.success(request, f'Customer "{company_name}" deleted successfully!')
        return redirect('onboarding:admin_customers_list')
    
    return redirect('onboarding:admin_customer_detail', customer_id=customer_id)


# ==================== PHASE 1: CUSTOMER PORTAL VIEWS ====================

from django.http import JsonResponse, HttpResponse, FileResponse
from django.urls import reverse
from django.conf import settings
from .models import CompanyProfile, CompanyAdmin, Notification, LabsAccount
from .utils import (
    encrypt_token, decrypt_token, send_email,
    send_community_approval_email, send_team_approval_email,
    send_contract_ready_email, send_contract_signed_email,
    send_removal_request_email, generate_contract_pdf,
    generate_secure_token, get_client_ip
)
import requests
import json
from datetime import datetime, timedelta


# ==================== LABS AUTHENTICATION VIEWS ====================

@login_required
def labs_login(request):
    """Initiate Labs OAuth flow"""
    try:
        team_member = TeamMember.objects.get(user=request.user)
    except TeamMember.DoesNotExist:
        messages.error(request, 'Team member profile not found.')
        return redirect('onboarding:dashboard')
    
    # Build OAuth authorization URL
    labs_auth_url = settings.LABS_OAUTH_AUTHORIZE_URL
    client_id = settings.LABS_CLIENT_ID
    redirect_uri = request.build_absolute_uri(reverse('onboarding:labs_callback'))
    scope = 'profile projects'
    state = generate_secure_token()
    
    # Store state in session for verification
    request.session['labs_oauth_state'] = state
    request.session['labs_oauth_team_member_id'] = team_member.id
    
    auth_url = f"{labs_auth_url}?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope={scope}&state={state}"
    
    return redirect(auth_url)


@login_required
def labs_callback(request):
    """Handle Labs OAuth callback"""
    code = request.GET.get('code')
    state = request.GET.get('state')
    error = request.GET.get('error')
    
    if error:
        messages.error(request, f'Labs authentication failed: {error}')
        return redirect('onboarding:dashboard')
    
    # Verify state
    stored_state = request.session.get('labs_oauth_state')
    if not state or state != stored_state:
        messages.error(request, 'Invalid OAuth state. Please try again.')
        return redirect('onboarding:dashboard')
    
    # Exchange code for access token
    token_url = settings.LABS_OAUTH_TOKEN_URL
    client_id = settings.LABS_CLIENT_ID
    client_secret = settings.LABS_CLIENT_SECRET
    redirect_uri = request.build_absolute_uri(reverse('onboarding:labs_callback'))
    
    try:
        response = requests.post(token_url, data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
            'client_id': client_id,
            'client_secret': client_secret,
        })
        response.raise_for_status()
        token_data = response.json()
        access_token = token_data.get('access_token')
        
        if not access_token:
            raise Exception('No access token in response')
        
        # Get user profile from Labs
        profile_response = requests.get(
            f"{settings.LABS_API_BASE_URL}/api/me",
            headers={'Authorization': f'Bearer {access_token}'}
        )
        profile_response.raise_for_status()
        profile_data = profile_response.json()
        
        # Get team member
        team_member_id = request.session.get('labs_oauth_team_member_id')
        team_member = get_object_or_404(TeamMember, id=team_member_id, user=request.user)
        
        # Create or update LabsAccount
        labs_account, created = LabsAccount.objects.get_or_create(team_member=team_member)
        labs_account.labs_username = profile_data.get('username')
        labs_account.labs_email = profile_data.get('email')
        labs_account.labs_token = encrypt_token(access_token)
        labs_account.labs_user_id = profile_data.get('id')
        labs_account.buildly_profile_linked = True
        labs_account.save()
        
        # Update CompanyProfile if customer is Labs customer
        if hasattr(team_member, 'customer_assignments'):
            for assignment in team_member.customer_assignments.filter(is_active=True):
                customer = assignment.customer
                try:
                    profile = CompanyProfile.objects.get(customer=customer)
                    if not profile.is_labs_customer:
                        profile.is_labs_customer = True
                        profile.labs_account_email = profile_data.get('email')
                        profile.save()
                except CompanyProfile.DoesNotExist:
                    pass
        
        messages.success(request, 'Successfully linked your Buildly Labs account!')
        
        # Clean up session
        del request.session['labs_oauth_state']
        del request.session['labs_oauth_team_member_id']
        
    except Exception as e:
        messages.error(request, f'Failed to link Labs account: {str(e)}')
    
    return redirect('onboarding:dashboard')


@login_required
def labs_unlink(request):
    """Unlink Labs account"""
    if request.method != 'POST':
        return redirect('onboarding:dashboard')
    
    try:
        team_member = TeamMember.objects.get(user=request.user)
        labs_account = LabsAccount.objects.get(team_member=team_member)
        labs_account.delete()
        messages.success(request, 'Successfully unlinked your Labs account.')
    except (TeamMember.DoesNotExist, LabsAccount.DoesNotExist):
        messages.error(request, 'No Labs account found to unlink.')
    
    return redirect('onboarding:dashboard')


# ==================== APPROVAL WORKFLOW VIEWS ====================

@user_passes_test(lambda u: u.is_superuser)
def admin_approval_queue(request):
    """Admin view of developers - shows all with pending first"""
    developers = TeamMember.objects.filter(
        user__is_active=True
    ).select_related('user', 'agency').prefetch_related('tech_skills', 'types')
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        developers = developers.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(github_account__icontains=search_query) |
            Q(tech_skills__technology__icontains=search_query)
        ).distinct()
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter == 'pending':
        developers = developers.filter(approved=False)
    elif status_filter == 'approved':
        developers = developers.filter(approved=True)
    
    # Filter by type
    type_filter = request.GET.get('type', '')
    if type_filter:
        type_obj = TeamMemberType.objects.filter(key=type_filter).first()
        if type_obj:
            developers = developers.filter(types=type_obj)
    
    # Filter by experience
    exp_filter = request.GET.get('experience', '')
    if exp_filter == 'junior':
        developers = developers.filter(experience_years__lt=3)
    elif exp_filter == 'mid':
        developers = developers.filter(experience_years__gte=3, experience_years__lt=7)
    elif exp_filter == 'senior':
        developers = developers.filter(experience_years__gte=7)
    
    # Filter by independent/agency
    affiliation_filter = request.GET.get('affiliation', '')
    if affiliation_filter == 'independent':
        developers = developers.filter(is_independent=True)
    elif affiliation_filter == 'agency':
        developers = developers.filter(is_independent=False)
    
    # Sort with pending (not approved) first, then by name
    developers = developers.order_by('approved', 'last_name', 'first_name')
    
    # Count pending for banner
    pending_count = developers.filter(approved=False).count()
    
    # Get all types for approval dropdown (show all available types, not just pending ones)
    all_types = TeamMemberType.objects.all().order_by('label')
    
    return render(request, 'admin_approval_queue.html', {
        'developers': developers,
        'pending_count': pending_count,
        'search_query': search_query,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'exp_filter': exp_filter,
        'affiliation_filter': affiliation_filter,
        'all_types': all_types,
    })


@user_passes_test(lambda u: u.is_superuser)
def admin_approve_community(request, developer_id):
    """Approve developer for community"""
    if request.method != 'POST':
        return redirect('onboarding:admin_approval_queue')
    
    developer = get_object_or_404(TeamMember, id=developer_id)
    
    if developer.community_approval_date:
        messages.warning(request, f'{developer.first_name} {developer.last_name} is already approved.')
        return redirect('onboarding:admin_approval_queue')
    
    # Get profile type from form if provided (required)
    profile_type_key = request.POST.get('profile_type')
    if not profile_type_key:
        messages.error(request, 'Please select a profile type before approving.')
        return redirect('onboarding:admin_approval_queue')
    
    profile_type = TeamMemberType.objects.filter(key=profile_type_key).first()
    if not profile_type:
        messages.error(request, 'Invalid profile type selected.')
        return redirect('onboarding:admin_approval_queue')
    
    if profile_type not in developer.profile_types.all():
        developer.profile_types.add(profile_type)
    
    # Approve developer
    developer.community_approval_date = now()
    developer.community_approved_by = request.user
    developer.approved = True  # keep legacy flag in sync
    developer.save(update_fields=['community_approval_date', 'community_approved_by', 'approved'])
    
    # Send email notification
    send_community_approval_email(developer)
    
    # Create in-app notification
    Notification.objects.create(
        recipient=developer.user,
        notification_type='community_approved',
        title='Welcome to Buildly Open Source Community!',
        message=f'Your profile has been approved! You now have access to community trainings, certifications, and can be evaluated for job openings.',
        is_read=False
    )
    
    messages.success(request, f'{developer.first_name} {developer.last_name} approved successfully!')
    return redirect('onboarding:admin_approval_queue')


@login_required
def customer_portal_dashboard(request):
    """Customer admin dashboard"""
    # Determine customer context for company admins or staff
    company_admin = None
    customer = None
    
    # Company admin access
    try:
        company_admin = CompanyAdmin.objects.get(user=request.user, is_active=True)
        customer = company_admin.customer
    except CompanyAdmin.DoesNotExist:
        # Staff access: allow passing ?customer_id=
        if request.user.is_staff:
            customer_id = request.GET.get('customer_id')
            if not customer_id:
                messages.info(request, 'Select a customer to view their portal.')
                return redirect('onboarding:customer_portal_switcher')
            from .models import Customer
            customer = get_object_or_404(Customer, id=customer_id)
        else:
            messages.error(request, 'You do not have customer admin access.')
            return redirect('onboarding:dashboard')
    
    # Get company profile
    try:
        company_profile = CompanyProfile.objects.get(customer=customer)
    except CompanyProfile.DoesNotExist:
        # Create default profile
        company_profile = CompanyProfile.objects.create(
            customer=customer,
            industry='',
            website=''
        )
    
    # Get team members
    team_assignments = CustomerDeveloperAssignment.objects.filter(
        customer=customer,
        status='approved'
    ).select_related('developer').order_by('-assigned_at')
    
    # Get pending approvals (if user can approve)
    pending_approvals = []
    if company_admin and getattr(company_admin, 'can_approve_developers', False):
        pending_approvals = CustomerDeveloperAssignment.objects.filter(
            customer=customer,
            status='pending'
        ).select_related('developer')
    
    # Get contracts (use status field; 'signed' is a status choice)
    contracts = Contract.objects.filter(customer=customer).order_by('-created_at')
    unsigned_contracts = contracts.exclude(status='signed')
    
    # Get notifications (Notification uses recipient field)
    recent_notifications = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).order_by('-created_at')[:5]
    
    context = {
        'company_admin': company_admin,
        'customer': customer,
        'company_profile': company_profile,
        'team_assignments': team_assignments,
        'pending_approvals': pending_approvals,
        'contracts': contracts,
        'unsigned_contracts': unsigned_contracts,
        'recent_notifications': recent_notifications,
    }
    
    return render(request, 'customer_portal_dashboard.html', context)


@user_passes_test(lambda u: u.is_staff)
def customer_portal_switcher(request):
    """Staff-only: list customers to enter their portal dashboard"""
    from .models import Customer
    customers = Customer.objects.all().order_by('company_name')
    return render(request, 'customer_portal_switcher.html', {
        'customers': customers,
    })


@login_required
def customer_approve_developer(request, assignment_id):
    """Customer admin approves developer assignment"""
    if request.method != 'POST':
        return redirect('onboarding:customer_portal_dashboard')
    
    # Verify user is company admin
    try:
        company_admin = CompanyAdmin.objects.get(user=request.user, is_active=True)
    except CompanyAdmin.DoesNotExist:
        messages.error(request, 'You do not have customer admin access.')
        return redirect('onboarding:dashboard')
    
    # Check permission
    if not company_admin.can_approve_developers:
        messages.error(request, 'You do not have permission to approve developers.')
        return redirect('onboarding:customer_portal_dashboard')
    
    # Get assignment
    assignment = get_object_or_404(
        CustomerDeveloperAssignment,
        id=assignment_id,
        customer=company_admin.customer
    )
    
    if assignment.status == 'approved':
        messages.warning(request, 'This developer is already approved.')
        return redirect('onboarding:customer_portal_dashboard')
    
    # Approve assignment
    assignment.status = 'approved'
    assignment.reviewed_at = now()
    assignment.approved_by = company_admin
    assignment.save()
    
    # Send email notification
    send_team_approval_email(assignment)
    
    # Create in-app notification for developer
    Notification.objects.create(
        user=assignment.developer.user,
        notification_type='team_approved',
        title=f'Added to {company_admin.customer.company_name} Team',
        message=f'You have been approved to join the {company_admin.customer.company_name} team!',
        related_customer=company_admin.customer,
        is_read=False
    )
    
    messages.success(request, f'{assignment.developer.first_name} {assignment.developer.last_name} approved successfully!')
    return redirect('onboarding:customer_portal_dashboard')


@login_required
def request_developer_removal(request, assignment_id):
    """Customer admin requests removal of developer (30-day notice)"""
    if request.method != 'POST':
        return redirect('onboarding:customer_portal_dashboard')
    
    # Verify user is company admin
    try:
        company_admin = CompanyAdmin.objects.get(user=request.user, is_active=True)
    except CompanyAdmin.DoesNotExist:
        messages.error(request, 'You do not have customer admin access.')
        return redirect('onboarding:dashboard')
    
    # Get assignment
    assignment = get_object_or_404(
        CustomerDeveloperAssignment,
        id=assignment_id,
        customer=company_admin.customer
    )
    
    if assignment.status != 'approved':
        messages.warning(request, 'This developer is not currently active on your team.')
        return redirect('onboarding:customer_portal_dashboard')
    
    # Send email to admin staff
    send_removal_request_email(
        company_admin,
        assignment.developer,
        company_admin.customer
    )
    
    # Create notification for staff
    staff_users = User.objects.filter(is_staff=True)
    for staff_user in staff_users:
        Notification.objects.create(
            user=staff_user,
            notification_type='team_removal_requested',
            title=f'Removal Request: {assignment.developer.first_name} {assignment.developer.last_name}',
            message=f'{company_admin.customer.company_name} requested removal of {assignment.developer.first_name} {assignment.developer.last_name} (30-day notice)',
            related_customer=company_admin.customer,
            is_read=False
        )
    
    messages.success(request, f'Removal request submitted for {assignment.developer.first_name} {assignment.developer.last_name}. 30-day notice period applies.')
    return redirect('onboarding:customer_portal_dashboard')


# ==================== CONTRACT SIGNING VIEWS ====================

@login_required
def contract_sign_form(request, contract_id):
    """Display contract signing form"""
    contract = get_object_or_404(Contract, id=contract_id)
    
    # Verify user has access
    try:
        company_admin = CompanyAdmin.objects.get(
            user=request.user,
            customer=contract.customer,
            is_active=True
        )
    except CompanyAdmin.DoesNotExist:
        messages.error(request, 'You do not have access to this contract.')
        return redirect('onboarding:dashboard')
    
    # Check permission
    if not company_admin.can_sign_contracts:
        messages.error(request, 'You do not have permission to sign contracts.')
        return redirect('onboarding:customer_portal_dashboard')
    
    if contract.status == 'signed':
        messages.info(request, 'This contract is already signed.')
        return redirect('onboarding:customer_portal_dashboard')
    
    context = {
        'contract': contract,
        'company_admin': company_admin,
        'customer': contract.customer,
    }
    
    return render(request, 'contract_sign_form.html', context)


@login_required
def contract_sign_submit(request, contract_id):
    """Process contract signature"""
    if request.method != 'POST':
        return redirect('onboarding:customer_portal_dashboard')
    
    contract = get_object_or_404(Contract, id=contract_id)
    
    # Verify user has access
    try:
        company_admin = CompanyAdmin.objects.get(
            user=request.user,
            customer=contract.customer,
            is_active=True
        )
    except CompanyAdmin.DoesNotExist:
        messages.error(request, 'You do not have access to this contract.')
        return redirect('onboarding:dashboard')
    
    # Check permission
    if not company_admin.can_sign_contracts:
        messages.error(request, 'You do not have permission to sign contracts.')
        return redirect('onboarding:customer_portal_dashboard')
    
    if contract.status == 'signed':
        messages.warning(request, 'This contract is already signed.')
        return redirect('onboarding:customer_portal_dashboard')
    
    # Get signature data
    signature_data = request.POST.get('signature_data')  # Base64 signature image
    signed_by_name = request.POST.get('signed_by_name')
    agree_terms = request.POST.get('agree_terms')
    
    if not all([signed_by_name, agree_terms]):
        messages.error(request, 'Please fill in all required fields and sign the contract.')
        return redirect('onboarding:contract_sign_form', contract_id=contract_id)
    
    # Sign contract
    contract.status = 'signed'
    contract.signed_by = signed_by_name
    contract.signed_at = now()
    contract.signature_data = signature_data or ''
    contract.signature_ip = request.META.get('REMOTE_ADDR', '')
    contract.signature_timestamp = now()
    
    # Generate and store hash for verification
    contract.contract_hash = contract.generate_hash()
    
    contract.save()
    
    # Generate PDF and PNG documents
    from .document_generator import save_contract_documents
    try:
        save_contract_documents(contract)
    except Exception as e:
        # Log error but don't fail signing
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to generate contract documents: {e}")
    
    # Send confirmation email
    from .utils import send_contract_signed_confirmation
    try:
        send_contract_signed_confirmation(contract, company_admin.user)
    except Exception as e:
        # Log error but don't fail the signing
        pass
    
    # Create notification
    Notification.objects.create(
        recipient=company_admin.user,
        notification_type='contract_signed',
        title='Contract Signed Successfully',
        message=f'Contract "{contract.title}" has been signed.',
        related_contract=contract,
        related_customer=contract.customer,
        is_read=False
    )
    
    # Notify staff
    staff_users = User.objects.filter(is_staff=True)
    for staff_user in staff_users:
        Notification.objects.create(
            recipient=staff_user,
            notification_type='contract_signed',
            title=f'Contract Signed: {contract.customer.company_name}',
            message=f'{contract.customer.company_name} signed "{contract.title}"',
            related_contract=contract,
            related_customer=contract.customer,
            is_read=False
        )
    
    messages.success(
        request, 
        f'Contract signed successfully! Verification Hash: {contract.contract_hash[:16]}... A copy has been sent to your email.'
    )
    return redirect('onboarding:customer_portal_dashboard')


@login_required
def contract_pdf_download(request, contract_id):
    """Download signed contract PDF"""
    contract = get_object_or_404(Contract, id=contract_id)
    
    # Verify user has access
    try:
        company_admin = CompanyAdmin.objects.get(
            user=request.user,
            customer=contract.customer,
            is_active=True
        )
    except CompanyAdmin.DoesNotExist:
        # Check if staff
        if not request.user.is_staff:
            messages.error(request, 'You do not have access to this contract.')
            return redirect('onboarding:dashboard')
    
    if contract.status != 'signed':
        messages.error(request, 'This contract is not yet signed.')
        return redirect('onboarding:customer_portal_dashboard')
    
    # Check if PDF already exists
    if contract.pdf_file:
        # Serve existing file
        from django.http import FileResponse
        response = FileResponse(contract.pdf_file.open('rb'), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="contract_{contract.id}_signed.pdf"'
        return response
    else:
        # Generate PDF on-the-fly
        from .document_generator import generate_contract_pdf
        try:
            pdf_content = generate_contract_pdf(contract)
            
            # Return as download
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="contract_{contract.id}_signed.pdf"'
            return response
        except Exception as e:
            messages.error(request, f'Error generating PDF: {str(e)}')
            return redirect('onboarding:customer_portal_dashboard')


# ==================== NOTIFICATION VIEWS ====================

@login_required
def notification_center(request):
    """View all notifications"""
    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')
    
    # Mark as read if requested
    if request.GET.get('mark_read') == 'all':
        notifications.filter(is_read=False).update(is_read=True)
        messages.success(request, 'All notifications marked as read.')
        return redirect('onboarding:notification_center')
    
    context = {
        'notifications': notifications,
        'unread_count': notifications.filter(is_read=False).count()
    }
    
    return render(request, 'notification_center.html', context)


@login_required
def notification_mark_read(request, notification_id):
    """Mark single notification as read"""
    if request.method != 'POST':
        return redirect('onboarding:notification_center')
    
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    
    return JsonResponse({'success': True})


@login_required
def notification_unread_count(request):
    """API endpoint for unread notification count"""
    count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({'count': count})


# ==================== CERTIFICATE VIEWS ====================

@login_required
def developer_certificates(request):
    """View all certificates for a developer"""
    try:
        team_member = TeamMember.objects.get(user=request.user)
    except TeamMember.DoesNotExist:
        messages.error(request, 'You must be a registered developer to view certificates.')
        return redirect('onboarding:dashboard')
    
    from .models import DeveloperCertification
    certificates = DeveloperCertification.objects.filter(
        developer=team_member
    ).select_related('certification_level', 'issued_by')
    
    context = {
        'team_member': team_member,
        'certificates': certificates,
    }
    
    return render(request, 'developer_certificates.html', context)


@login_required
def certificate_download(request, cert_id):
    """Download a certificate PDF or PNG"""
    from .models import DeveloperCertification
    cert = get_object_or_404(DeveloperCertification, id=cert_id)
    
    # Verify access
    if cert.developer.user != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have access to this certificate.')
        return redirect('onboarding:dashboard')
    
    # Check if revoked
    if cert.is_revoked:
        messages.error(request, 'This certificate has been revoked.')
        return redirect('onboarding:developer_certificates')
    
    # Get format from query param
    file_format = request.GET.get('format', 'pdf')
    
    if file_format == 'png':
        if cert.png_file:
            from django.http import FileResponse
            response = FileResponse(cert.png_file.open('rb'), content_type='image/png')
            response['Content-Disposition'] = f'attachment; filename="certificate_{cert.certificate_number}.png"'
            return response
        else:
            # Generate on-the-fly
            from .document_generator import generate_certificate_png
            png_content = generate_certificate_png(cert)
            response = HttpResponse(png_content, content_type='image/png')
            response['Content-Disposition'] = f'attachment; filename="certificate_{cert.certificate_number}.png"'
            return response
    else:
        if cert.pdf_file:
            from django.http import FileResponse
            response = FileResponse(cert.pdf_file.open('rb'), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="certificate_{cert.certificate_number}.pdf"'
            return response
        else:
            # Generate on-the-fly
            from .document_generator import generate_certificate_pdf
            pdf_content = generate_certificate_pdf(cert)
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="certificate_{cert.certificate_number}.pdf"'
            return response


@user_passes_test(lambda u: u.is_superuser)
def admin_certification_levels(request):
    """Manage certification levels"""
    from .models import CertificationLevel
    levels = CertificationLevel.objects.all().order_by('level_type', 'name')
    
    context = {
        'levels': levels,
    }
    
    return render(request, 'admin_certification_levels.html', context)


@user_passes_test(lambda u: u.is_superuser)
def admin_certification_create(request):
    """Create a new certification level"""
    from .models import CertificationLevel, TeamTraining, TrainingSection, Quiz
    
    if request.method == 'POST':
        name = request.POST.get('name')
        level_type = request.POST.get('level_type', 'intermediate')
        description = request.POST.get('description')
        requirements = request.POST.get('requirements', '')
        skills = request.POST.get('skills', '')
        price = request.POST.get('price') or None
        badge_color = request.POST.get('badge_color', '#3B82F6')
        min_quiz_score = request.POST.get('min_quiz_score', 70)
        
        cert_level = CertificationLevel.objects.create(
            name=name,
            level_type=level_type,
            description=description,
            requirements=requirements,
            skills=skills,
            price=price,
            badge_color=badge_color,
            min_quiz_score=min_quiz_score,
            created_by=request.user
        )
        
        # Add required trainings
        training_ids = request.POST.getlist('required_trainings')
        if training_ids:
            cert_level.required_trainings.set(training_ids)
        
        # Add required sections
        section_ids = request.POST.getlist('required_sections')
        if section_ids:
            cert_level.required_sections.set(section_ids)
        
        # Add required quizzes
        quiz_ids = request.POST.getlist('required_quizzes')
        if quiz_ids:
            cert_level.required_quizzes.set(quiz_ids)
        
        messages.success(request, f'Certification level "{name}" created successfully!')
        return redirect('onboarding:admin_certification_levels')
    
    context = {
        'level_types': CertificationLevel.LEVEL_TYPES,
        'trainings': TeamTraining.objects.filter(is_active=True).select_related('customer'),
        'sections': TrainingSection.objects.filter(is_active=True).select_related('training', 'training__customer'),
        'quizzes': Quiz.objects.all().order_by('name'),
    }
    
    return render(request, 'admin_certification_create.html', context)


@user_passes_test(lambda u: u.is_superuser)
def admin_issue_certificate(request, developer_id):
    """Issue a certificate to a developer"""
    from .models import DeveloperCertification, CertificationLevel
    
    developer = get_object_or_404(TeamMember, id=developer_id)
    
    if request.method == 'POST':
        cert_level_id = request.POST.get('certification_level')
        score = request.POST.get('score') or None
        notes = request.POST.get('notes', '')
        expires_in_months = request.POST.get('expires_in_months') or None
        
        cert_level = get_object_or_404(CertificationLevel, id=cert_level_id)
        
        # Check if already certified
        existing = DeveloperCertification.objects.filter(
            developer=developer,
            certification_level=cert_level
        ).first()
        
        if existing:
            messages.warning(request, f'{developer.user.get_full_name()} already has this certification.')
            return redirect('onboarding:admin_issue_certificate', developer_id=developer_id)
        
        # Create certification
        cert = DeveloperCertification.objects.create(
            developer=developer,
            certification_level=cert_level,
            issued_by=request.user,
            score=score,
            notes=notes
        )
        
        # Set expiration
        if expires_in_months:
            from datetime import timedelta
            cert.expires_at = cert.issued_at + timedelta(days=int(expires_in_months) * 30)
        
        # Generate hash
        cert.certificate_hash = cert.generate_hash()
        cert.save()
        
        # Generate documents
        from .document_generator import save_certificate_documents
        try:
            save_certificate_documents(cert)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to generate certificate documents: {e}")
        
        messages.success(request, f'Certificate issued to {developer.user.get_full_name()}!')
        return redirect('onboarding:admin_customer_dashboard')
    
    from .models import CertificationLevel
    cert_levels = CertificationLevel.objects.filter(is_active=True)
    
    context = {
        'developer': developer,
        'cert_levels': cert_levels,
    }
    
    return render(request, 'admin_issue_certificate.html', context)


# ==================== VERIFICATION VIEWS (PUBLIC) ====================

def verification_home(request):
    """Public page for verifying contracts and certificates"""
    return render(request, 'verification_home.html')


def verify_contract(request, contract_hash):
    """Public endpoint to verify a contract by hash"""
    contract = get_object_or_404(Contract, contract_hash=contract_hash)
    
    # Verify hash
    is_valid = contract.verify_hash()
    
    context = {
        'contract': contract,
        'is_valid': is_valid,
        'verification_hash': contract_hash,
    }
    
    return render(request, 'verify_contract.html', context)


def verify_certificate(request, certificate_hash):
    """Public endpoint to verify a certificate by hash"""
    from .models import DeveloperCertification
    
    cert = get_object_or_404(DeveloperCertification, certificate_hash=certificate_hash)
    
    # Verify hash
    is_valid = cert.verify_hash()
    
    context = {
        'certificate': cert,
        'is_valid': is_valid,
        'verification_hash': certificate_hash,
    }
    
    return render(request, 'verify_certificate.html', context)


# ==================== DEVELOPER TEAMS & TRAININGS ====================

@login_required
def developer_teams(request):
    """Show logged-in developer the teams (customers) they are part of and assigned trainings."""
    try:
        team_member = TeamMember.objects.get(user=request.user)
    except TeamMember.DoesNotExist:
        return redirect('onboarding:register')

    assignments = (CustomerDeveloperAssignment.objects
                   .filter(developer=team_member, status='approved')
                   .select_related('customer'))

    # Precompute completed resources for this developer
    completed_resource_ids = set(
        TeamMemberResource.objects.filter(team_member=team_member, percentage_complete__gte=100)
        .values_list('resource_id', flat=True)
    )

    teams = []
    for assignment in assignments:
        trainings = TeamTraining.objects.filter(customer=assignment.customer, is_active=True)
        enrollments = {e.training_id: e for e in DeveloperTrainingEnrollment.objects.filter(developer=team_member, training__in=trainings)}
        team_entry = {
            'customer': assignment.customer,
            'trainings': [],
        }
        for tr in trainings:
            enr = enrollments.get(tr.id)
            progress = enr.progress_percent() if enr else 0
            team_entry['trainings'].append({
                'training': tr,
                'enrollment': enr,
                'progress': progress,
            })
        teams.append(team_entry)

    context = {
        'team_member': team_member,
        'teams': teams,
        'completed_resource_ids': completed_resource_ids,
    }
    return render(request, 'developer_teams.html', context)


@login_required
def mark_resource_complete(request, resource_id):
    """Mark a learning resource as complete for the current developer."""
    team_member = get_object_or_404(TeamMember, user=request.user)
    resource = get_object_or_404(Resource, id=resource_id)

    tm_res, _ = TeamMemberResource.objects.get_or_create(team_member=team_member, resource=resource)
    tm_res.percentage_complete = 100
    tm_res.save()
    messages.success(request, f'Marked "{resource.title}" as complete.')
    return redirect(request.META.get('HTTP_REFERER', 'onboarding:developer_teams'))


def _is_staff(user):
    return user.is_staff


@login_required
@user_passes_test(_is_staff)
def admin_training_list(request):
    qs = TeamTraining.objects.select_related('customer').all()
    customer_id = request.GET.get('customer')
    if customer_id:
        qs = qs.filter(customer_id=customer_id)
    return render(request, 'admin_training_list.html', {
        'trainings': qs,
    })


@login_required
@user_passes_test(_is_staff)
def admin_training_create(request):
    from django import forms

    class TeamTrainingForm(forms.ModelForm):
        class Meta:
            model = TeamTraining
            fields = ['customer', 'developer_team', 'name', 'description', 'resources', 'quiz', 'is_active']
            widgets = {
                'resources': forms.SelectMultiple(attrs={'size': 10}),
            }
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            if 'customer' in self.data:
                try:
                    customer_id = int(self.data.get('customer'))
                    self.fields['developer_team'].queryset = DeveloperTeam.objects.filter(customer_id=customer_id)
                except (ValueError, TypeError):
                    pass
            elif self.instance.pk and self.instance.customer:
                self.fields['developer_team'].queryset = DeveloperTeam.objects.filter(customer=self.instance.customer)
            else:
                self.fields['developer_team'].queryset = DeveloperTeam.objects.none()

    if request.method == 'POST':
        form = TeamTrainingForm(request.POST)
        if form.is_valid():
            training = form.save(commit=False)
            training.created_by = request.user
            training.save()
            form.save_m2m()
            
            # Auto-enroll team members if a team was selected
            if training.developer_team:
                enrolled_count = training.auto_enroll_team_members(assigned_by=request.user)
                if enrolled_count > 0:
                    messages.success(request, f'Training created and {enrolled_count} team members enrolled.')
                else:
                    messages.success(request, 'Training created.')
            else:
                messages.success(request, 'Training created.')
            return redirect('onboarding:admin_training_detail', training_id=training.id)
    else:
        form = TeamTrainingForm()

    return render(request, 'admin_training_form.html', {
        'form': form,
        'action': 'Create',
    })


@login_required
@user_passes_test(_is_staff)
def admin_training_edit(request, training_id):
    from django import forms
    training = get_object_or_404(TeamTraining, id=training_id)

    class TeamTrainingForm(forms.ModelForm):
        class Meta:
            model = TeamTraining
            fields = ['customer', 'developer_team', 'name', 'description', 'resources', 'quiz', 'is_active']
            widgets = {
                'resources': forms.SelectMultiple(attrs={'size': 10}),
            }
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            if 'customer' in self.data:
                try:
                    customer_id = int(self.data.get('customer'))
                    self.fields['developer_team'].queryset = DeveloperTeam.objects.filter(customer_id=customer_id)
                except (ValueError, TypeError):
                    pass
            elif self.instance.pk and self.instance.customer:
                self.fields['developer_team'].queryset = DeveloperTeam.objects.filter(customer=self.instance.customer)
            else:
                self.fields['developer_team'].queryset = DeveloperTeam.objects.none()

    if request.method == 'POST':
        form = TeamTrainingForm(request.POST, instance=training)
        if form.is_valid():
            old_team = training.developer_team
            form.save()
            
            # If team assignment changed, auto-enroll new team members
            if training.developer_team and training.developer_team != old_team:
                enrolled_count = training.auto_enroll_team_members(assigned_by=request.user)
                if enrolled_count > 0:
                    messages.success(request, f'Training updated and {enrolled_count} team members enrolled.')
                else:
                    messages.success(request, 'Training updated.')
            else:
                messages.success(request, 'Training updated.')
            return redirect('onboarding:admin_training_detail', training_id=training.id)
    else:
        form = TeamTrainingForm(instance=training)

    return render(request, 'admin_training_form.html', {
        'form': form,
        'action': 'Edit',
        'training': training,
    })


@login_required
@user_passes_test(_is_staff)
def admin_training_detail(request, training_id):
    training = get_object_or_404(TeamTraining.objects.select_related('customer', 'quiz'), id=training_id)

    # Get all approved community developers
    all_developers = TeamMember.objects.filter(
        community_approval_date__isnull=False
    ).order_by('first_name', 'last_name')

    # Check which ones are assigned to this customer
    assigned_to_customer = set(
        CustomerDeveloperAssignment.objects.filter(
            customer=training.customer,
            status='approved'
        ).values_list('developer_id', flat=True)
    )

    # Annotate developers with assignment status
    developers_with_status = []
    for dev in all_developers:
        developers_with_status.append({
            'developer': dev,
            'is_assigned_to_customer': dev.id in assigned_to_customer,
        })

    enrollments = DeveloperTrainingEnrollment.objects.filter(training=training).select_related('developer')
    
    # Get customer teams for team assignment dropdown
    customer_teams = DeveloperTeam.objects.filter(customer=training.customer, is_active=True).order_by('name')

    return render(request, 'admin_training_detail.html', {
        'training': training,
        'enrollments': enrollments,
        'developers_with_status': developers_with_status,
        'has_assigned_developers': len(assigned_to_customer) > 0,
        'customer_teams': customer_teams,
    })


@login_required
@user_passes_test(_is_staff)
def admin_training_enroll(request, training_id):
    if request.method != 'POST':
        return redirect('onboarding:admin_training_detail', training_id=training_id)

    training = get_object_or_404(TeamTraining, id=training_id)
    developer_id = request.POST.get('developer_id')
    developer = get_object_or_404(TeamMember, id=developer_id)

    # Check if developer is assigned to this customer
    is_assigned = CustomerDeveloperAssignment.objects.filter(
        customer=training.customer, 
        developer=developer, 
        status='approved'
    ).exists()
    
    if not is_assigned:
        # Auto-create the assignment if developer is approved for community
        if developer.community_approval_date:
            assignment, created = CustomerDeveloperAssignment.objects.get_or_create(
                customer=training.customer,
                developer=developer,
                defaults={'status': 'approved', 'reviewed_at': now()}
            )
            if created:
                messages.info(request, f'Developer automatically assigned to {training.customer.company_name} team.')
        else:
            messages.error(request, 'Developer must be community-approved first.')
            return redirect('onboarding:admin_training_detail', training_id=training.id)

    enrollment, created = DeveloperTrainingEnrollment.objects.get_or_create(
        developer=developer,
        training=training,
        defaults={'assigned_by': request.user}
    )
    if created:
        messages.success(request, f"Assigned {developer.first_name} {developer.last_name} to training.")
    else:
        messages.info(request, 'Developer is already assigned to this training.')
    return redirect('onboarding:admin_training_detail', training_id=training.id)


@login_required
@user_passes_test(_is_staff)
def admin_training_assign_team(request, training_id):
    """Assign an entire developer team to a training at once."""
    if request.method != 'POST':
        return redirect('onboarding:admin_training_detail', training_id=training_id)
    
    training = get_object_or_404(TeamTraining, id=training_id)
    team_id = request.POST.get('team_id')
    
    if team_id:
        team = get_object_or_404(DeveloperTeam, id=team_id, customer=training.customer)
        training.developer_team = team
        training.save()
        
        # Auto-enroll all team members
        enrolled_count = training.auto_enroll_team_members(assigned_by=request.user)
        messages.success(request, f'Training assigned to {team.name}. {enrolled_count} members enrolled.')
    else:
        # Unassign team
        training.developer_team = None
        training.save()
        messages.info(request, 'Training unassigned from team.')
    
    return redirect('onboarding:admin_training_detail', training_id=training.id)


# ==================== DEVELOPER TEAM MANAGEMENT ====================

@login_required
@user_passes_test(_is_staff)
def admin_team_list(request):
    """List all developer teams."""
    teams = DeveloperTeam.objects.select_related('customer', 'team_lead').all()
    customer_id = request.GET.get('customer')
    if customer_id:
        teams = teams.filter(customer_id=customer_id)
    
    customers = Customer.objects.all().order_by('company_name')
    
    return render(request, 'admin_team_list.html', {
        'teams': teams,
        'customers': customers,
    })


@login_required
@user_passes_test(_is_staff)
def admin_team_create(request):
    """Create a new developer team."""
    from django import forms
    
    class DeveloperTeamForm(forms.ModelForm):
        class Meta:
            model = DeveloperTeam
            fields = ['customer', 'name', 'description', 'team_lead', 'is_active']
    
    if request.method == 'POST':
        form = DeveloperTeamForm(request.POST)
        if form.is_valid():
            team = form.save(commit=False)
            team.created_by = request.user
            team.save()
            messages.success(request, f'Team "{team.name}" created.')
            return redirect('onboarding:admin_team_detail', team_id=team.id)
    else:
        form = DeveloperTeamForm()
    
    return render(request, 'admin_team_form.html', {
        'form': form,
        'action': 'Create',
    })


@login_required
@user_passes_test(_is_staff)
def admin_team_edit(request, team_id):
    """Edit a developer team."""
    from django import forms
    team = get_object_or_404(DeveloperTeam, id=team_id)
    
    class DeveloperTeamForm(forms.ModelForm):
        class Meta:
            model = DeveloperTeam
            fields = ['customer', 'name', 'description', 'team_lead', 'is_active']
    
    if request.method == 'POST':
        form = DeveloperTeamForm(request.POST, instance=team)
        if form.is_valid():
            form.save()
            messages.success(request, 'Team updated.')
            return redirect('onboarding:admin_team_detail', team_id=team.id)
    else:
        form = DeveloperTeamForm(instance=team)
    
    return render(request, 'admin_team_form.html', {
        'form': form,
        'action': 'Edit',
        'team': team,
    })


@login_required
@user_passes_test(_is_staff)
def admin_team_detail(request, team_id):
    """View team details and manage members."""
    team = get_object_or_404(DeveloperTeam.objects.select_related('customer', 'team_lead'), id=team_id)
    
    # Get potential members (approved for this customer)
    potential_members = TeamMember.objects.filter(
        id__in=CustomerDeveloperAssignment.objects.filter(
            customer=team.customer,
            status='approved'
        ).values_list('developer_id', flat=True)
    ).exclude(
        id__in=team.members.values_list('id', flat=True)
    ).order_by('first_name', 'last_name')
    
    # Get trainings for this team
    trainings = TeamTraining.objects.filter(developer_team=team)
    
    return render(request, 'admin_team_detail.html', {
        'team': team,
        'potential_members': potential_members,
        'trainings': trainings,
    })


# ==================== API ENDPOINTS ====================

@login_required
@user_passes_test(_is_staff)
def api_teams_list(request):
    """API endpoint to get teams filtered by customer (for AJAX)."""
    from django.http import JsonResponse
    
    customer_id = request.GET.get('customer')
    if not customer_id:
        return JsonResponse({'teams': []})
    
    teams = DeveloperTeam.objects.filter(
        customer_id=customer_id,
        is_active=True
    ).values('id', 'name')
    
    # Add member count to each team
    teams_list = []
    for team_data in teams:
        team = DeveloperTeam.objects.get(id=team_data['id'])
        teams_list.append({
            'id': team_data['id'],
            'name': team_data['name'],
            'member_count': team.member_count()
        })
    
    return JsonResponse(teams_list, safe=False)


@login_required
@user_passes_test(_is_staff)
def admin_team_add_member(request, team_id):
    """Add a member to a team."""
    if request.method != 'POST':
        return redirect('onboarding:admin_team_detail', team_id=team_id)
    
    team = get_object_or_404(DeveloperTeam, id=team_id)
    member_id = request.POST.get('member_id')
    member = get_object_or_404(TeamMember, id=member_id)
    
    # Verify member is assigned to this customer
    is_assigned = CustomerDeveloperAssignment.objects.filter(
        customer=team.customer,
        developer=member,
        status='approved'
    ).exists()
    
    if not is_assigned:
        messages.error(request, 'Developer must be assigned to this customer first.')
        return redirect('onboarding:admin_team_detail', team_id=team.id)
    
    team.members.add(member)
    messages.success(request, f'Added {member.first_name} {member.last_name} to team.')
    return redirect('onboarding:admin_team_detail', team_id=team.id)


@login_required
@user_passes_test(_is_staff)
def admin_team_remove_member(request, team_id, member_id):
    """Remove a member from a team."""
    team = get_object_or_404(DeveloperTeam, id=team_id)
    member = get_object_or_404(TeamMember, id=member_id)
    
    team.members.remove(member)
    messages.success(request, f'Removed {member.first_name} {member.last_name} from team.')
    return redirect('onboarding:admin_team_detail', team_id=team.id)
