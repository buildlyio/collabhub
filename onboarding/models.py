# onboarding/models.py

from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from django.utils import timezone

TEAM_MEMBER_TYPES = [
    ('all', 'Everyone'),
    ('buildly-hire-frontend', 'Buildly Hire Frontend'),
    ('buildly-hire-backend', 'Buildly Hire Backend'),
    ('buildly-hire-ai', 'Buildly Hire AI'),
    ('buildly-hire-marketing', 'Buildly Hire Marketing'),
    ('buildly-hire-product', 'Buildly Hire Product'),
    ('buildly-hire-marketing-intern', 'Buildly Hire Marketing Intern'),
    ('community-member-generic', 'Generic Community Member'),
    ('community-frontend', 'Community Member Frontend'),
    ('community-backend', 'Community Member Backend'),
    ('community-product', 'Community Member Product'),
    ('community-ai', 'Community Member AI'),
    ('community-ui-designer', 'Community Member UI Designer'),
    ('community-ux', 'Community Member UX'),
    ('community-advisor', 'Community Member Advisor'),
    ('community-software-agency', 'Community Member Software Agency'),
    ('community-marketing-agency', 'Community Member Marketing Agency'),
    ('community-design-agency', 'Community Member Design Agency'),
]

class TeamMemberType(models.Model):
    """Model to store profile types for many-to-many relationship"""
    key = models.CharField(max_length=50, unique=True)
    label = models.CharField(max_length=100)
    
    def __str__(self):
        return self.label
    

    class Meta:
        ordering = ['label']


# Register TeamMemberType in Django admin
class TeamMemberTypeAdmin(admin.ModelAdmin):
    list_display = ('key', 'label')
    search_fields = ('key', 'label')

admin.site.register(TeamMemberType, TeamMemberTypeAdmin)


class TeamMember(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    team_member_type = models.CharField(max_length=50, choices=TEAM_MEMBER_TYPES)  # Keep for backward compatibility
    profile_types = models.ManyToManyField(TeamMemberType, blank=True, related_name='team_members', help_text="Multiple profile types")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    bio = models.TextField(blank=True)
    linkedin = models.URLField(blank=True)
    wellfound_profile = models.URLField(blank=True, help_text="Wellfound (AngelList) profile URL, e.g. https://wellfound.com/u/username")
    experience_years = models.PositiveIntegerField(blank=True, null=True)
    github_account = models.URLField(blank=True)
    google_account_link = models.URLField(blank=True)
    google_calendar_embed_code = models.TextField(blank=True)  # Stores the embed code
    approved = models.BooleanField(default=False)
    
    # Agency relationship
    is_independent = models.BooleanField(default=True, help_text="Is this an independent developer?")
    agency = models.ForeignKey('DevelopmentAgency', on_delete=models.SET_NULL, null=True, blank=True, related_name='team_members', help_text="Associated agency if not registered on platform")
    agency_name_text = models.CharField(max_length=255, blank=True, help_text="Agency name if not registered on platform")
    
    # Assessment tracking
    has_completed_assessment = models.BooleanField(default=False, help_text="Has completed Developer Level Assessment")
    assessment_completed_at = models.DateTimeField(null=True, blank=True, help_text="When assessment was completed")
    assessment_reminder_count = models.IntegerField(default=0, help_text="Number of times reminded to complete assessment")
    assessment_last_reminded = models.DateTimeField(null=True, blank=True, help_text="Last time reminded about assessment")
    
    # Community approval (Phase 1)
    community_approval_date = models.DateTimeField(null=True, blank=True, help_text="When approved to Buildly community")
    community_approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='community_approvals', help_text="Staff member who approved")
    community_approval_notification_sent = models.BooleanField(default=False, help_text="Notification sent to developer")
    
    # Availability & Capacity Settings
    AVAILABILITY_START_CHOICES = [
        ('immediate', 'Immediately Available'),
        ('1_week', '1 Week from Now'),
        ('2_weeks', '2 Weeks from Now'),
        ('1_month', '1 Month from Now'),
        ('custom', 'Custom Date'),
    ]
    
    available_for_public_projects = models.BooleanField(default=False, help_text="Available to work on public/open source Forge projects")
    available_for_customer_work = models.BooleanField(default=False, help_text="Available to work for Buildly customers")
    availability_start = models.CharField(max_length=20, choices=AVAILABILITY_START_CHOICES, default='immediate', blank=True)
    availability_start_date = models.DateField(null=True, blank=True, help_text="Custom start date if 'Custom Date' selected")
    hours_per_week = models.PositiveIntegerField(default=0, help_text="Hours per week available for work")
    availability_notes = models.TextField(blank=True, help_text="Additional notes about availability")
    availability_updated_at = models.DateTimeField(null=True, blank=True, help_text="When availability was last updated")

    @property
    def types(self):
        """Alias for profile_types for backward compatibility"""
        try:
            return self.profile_types
        except:
            # Fallback if field doesn't exist yet (during migration)
            from django.db.models import ManyToManyField
            return self.profile_types
    
    def __str__(self):
        try:
            type_names = ', '.join([t.label for t in self.profile_types.all()])
        except:
            type_names = ''
        return f'{self.first_name} {self.last_name} - {type_names if type_names else "Team Member"}'
    
    def get_profile_types_display(self):
        """Get comma-separated list of profile types"""
        try:
            types = self.profile_types.all()
            if types:
                return ', '.join([t.label for t in types])
        except:
            pass
        return 'Team Member'
    
    def get_github_username(self):
        """Extract GitHub username from github_account URL"""
        if self.github_account:
            return self.github_account.rstrip('/').split('/')[-1]
        return None


class TechnologySkill(models.Model):
    """Model to store developer's skill levels in various technologies"""
    SKILL_LEVEL_CHOICES = [
        (1, '1 - Beginner'),
        (2, '2 - Elementary'),
        (3, '3 - Intermediate'),
        (4, '4 - Advanced'),
        (5, '5 - Expert'),
    ]
    
    TECHNOLOGY_CHOICES = [
        ('javascript', 'JavaScript'),
        ('python', 'Python'),
        ('typescript', 'TypeScript'),
        ('nodejs', 'Node.js'),
        ('kubernetes', 'Kubernetes'),
        ('git', 'Git'),
        ('bash', 'Bash/Shell'),
        ('react', 'React'),
        ('vue', 'Vue.js'),
        ('angular', 'Angular'),
        ('django', 'Django'),
        ('flask', 'Flask'),
        ('docker', 'Docker'),
        ('aws', 'AWS'),
        ('azure', 'Azure'),
        ('gcp', 'Google Cloud'),
    ]
    
    team_member = models.ForeignKey(TeamMember, on_delete=models.CASCADE, related_name='tech_skills')
    technology = models.CharField(max_length=50, choices=TECHNOLOGY_CHOICES)
    skill_level = models.IntegerField(choices=SKILL_LEVEL_CHOICES, default=1)
    github_calculated_level = models.IntegerField(null=True, blank=True, help_text="Skill level calculated from GitHub data")
    github_repos_count = models.IntegerField(default=0, help_text="Number of repos using this technology")
    github_lines_count = models.IntegerField(default=0, help_text="Approximate lines of code in this technology")
    last_github_sync = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, help_text="Additional notes about experience")
    
    class Meta:
        unique_together = ['team_member', 'technology']
        ordering = ['-skill_level', 'technology']
    
    def __str__(self):
        return f'{self.team_member.first_name} {self.team_member.last_name} - {self.get_technology_display()}: {self.skill_level}'


class TechnologySkillAdmin(admin.ModelAdmin):
    list_display = ('team_member', 'technology', 'skill_level', 'github_calculated_level', 'github_repos_count', 'last_github_sync')
    list_filter = ('technology', 'skill_level')
    search_fields = ('team_member__first_name', 'team_member__last_name')


class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'team_member_type', 'approved', 'has_completed_assessment', 'user')
    list_filter = ('approved', 'team_member_type', 'has_completed_assessment')
    search_fields = ('first_name', 'last_name', 'email', 'user__username')
    list_editable = ('approved',)
    readonly_fields = ('assessment_completed_at', 'assessment_reminder_count', 'assessment_last_reminded')
    actions = ['approve_users', 'unapprove_users']
    display = 'Team Member Admin'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'team_member_type', 'first_name', 'last_name', 'email', 'approved')
        }),
        ('Profile', {
            'fields': ('bio', 'linkedin', 'wellfound_profile', 'experience_years', 'github_account', 'google_account_link', 'google_calendar_embed_code')
        }),
        ('Assessment Status', {
            'fields': ('has_completed_assessment', 'assessment_completed_at', 'assessment_reminder_count', 'assessment_last_reminded'),
            'classes': ('collapse',)
        }),
    )
    
    def approve_users(self, request, queryset):
        updated = queryset.update(approved=True)
        self.message_user(request, f'{updated} team members approved.')
    approve_users.short_description = "Approve selected team members"
    
    def unapprove_users(self, request, queryset):
        updated = queryset.update(approved=False)
        self.message_user(request, f'{updated} team members unapproved.')
    unapprove_users.short_description = "Unapprove selected team members"  
    

class CertificationExam(models.Model):
    team_member = models.ForeignKey(TeamMember, on_delete=models.CASCADE)
    team_member_type = models.CharField(max_length=50, choices=TEAM_MEMBER_TYPES)
    exam_link = models.URLField()
    score = models.PositiveIntegerField(default=0)
    quiz = models.ForeignKey('Quiz', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'{self.team_member} - {self.team_member_type} - {self.score}'

class CertificationExamAdmin(admin.ModelAdmin):
    list_display = ('team_member', 'team_member_type', 'score', 'exam_link')
    display = 'Certification Exam Admin'


class Resource(models.Model):
    team_member_type = models.CharField(max_length=50, choices=TEAM_MEMBER_TYPES)
    title = models.CharField(max_length=200)
    link = models.URLField(blank=True)
    descr = models.TextField(blank=True)    
    document = models.FileField(upload_to='resources/', blank=True)

    def __str__(self):
        return f'{self.title} - {self.team_member_type}'

class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'team_member_type', 'link', 'has_document')
    list_filter = ('team_member_type',)
    search_fields = ('title', 'descr', 'link')
    list_per_page = 50
    ordering = ('team_member_type', 'title')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('team_member_type', 'title')
        }),
        ('Content', {
            'fields': ('descr', 'link', 'document')
        }),
    )
    
    def has_document(self, obj):
        return bool(obj.document)
    has_document.boolean = True
    has_document.short_description = 'Has Document'
    
    actions = ['duplicate_resources']
    
    def duplicate_resources(self, request, queryset):
        """Duplicate selected resources"""
        count = 0
        for resource in queryset:
            resource.pk = None
            resource.title = f"{resource.title} (Copy)"
            resource.save()
            count += 1
        self.message_user(request, f'{count} resource(s) duplicated successfully.')
    duplicate_resources.short_description = "Duplicate selected resources"  


class TeamMemberResource(models.Model):
    team_member = models.ForeignKey(TeamMember, on_delete=models.CASCADE)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    percentage_complete = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.team_member} - {self.resource} - {self.percentage_complete}%'

class TeamMemberResourceAdmin(admin.ModelAdmin):
    list_display = ('team_member', 'resource', 'percentage_complete')
    display = 'Team Member Resource Admin'


# Quiz Model
class Quiz(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    available_date = models.DateField()
    url = models.URLField(unique=True)
    resources = models.ManyToManyField(Resource, blank=True, related_name='quizzes', help_text="Learning resources associated with this quiz")

    def __str__(self):
        return self.name

class QuizAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'available_date', 'url')
    search_fields = ('name', 'owner__username')

# Question Model
class QuizQuestion(models.Model):
    QUESTION_TYPES = [
        ('multiple_choice', 'Multiple Choice'),
        ('essay', 'Essay'),
    ]

    team_member_type = models.CharField(max_length=50, choices=TEAM_MEMBER_TYPES)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    question = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)

    def __str__(self):
        return f'{self.quiz.name} - {self.question}'

class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'team_member_type', 'question', 'question_type')
    search_fields = ('question',)

# Answer Model
class QuizAnswer(models.Model):
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, related_name="answers")
    team_member = models.ForeignKey("onboarding.TeamMember", on_delete=models.CASCADE)
    answer = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True, null=True)
    
    # AI Detection fields
    ai_detection_score = models.FloatField(null=True, blank=True, help_text="0-100 score indicating likelihood of AI usage")
    ai_detection_analysis = models.TextField(blank=True, help_text="Detailed AI detection analysis")
    
    # Evaluation fields
    evaluator_score = models.IntegerField(null=True, blank=True, help_text="Score given by human evaluator (e.g., 1-4 for A-D)")
    evaluator_notes = models.TextField(blank=True, help_text="Notes from human evaluator")
    evaluated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="evaluated_answers")
    evaluated_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['question', 'team_member']

    def __str__(self):
        return f'Answer by {self.team_member} to {self.question}'

class QuizAnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'team_member', 'answer_preview', 'ai_detection_score', 'evaluator_score', 'submitted_at')
    list_filter = ('question__quiz', 'evaluated_at', 'submitted_at')
    search_fields = ('team_member__first_name', 'team_member__last_name', 'answer')

    def answer_preview(self, obj):
        return obj.answer[:100] + '...' if len(obj.answer) > 100 else obj.answer
    answer_preview.short_description = 'Answer Preview'


# Developer Teams (groups within a customer)
class DeveloperTeam(models.Model):
    """A team/group of developers within a customer organization."""
    customer = models.ForeignKey('onboarding.Customer', on_delete=models.CASCADE, related_name='developer_teams')
    name = models.CharField(max_length=200, help_text="Team name (e.g., 'Frontend Team', 'Mobile Squad')")
    description = models.TextField(blank=True)
    members = models.ManyToManyField('onboarding.TeamMember', blank=True, related_name='developer_teams')
    team_lead = models.ForeignKey('onboarding.TeamMember', null=True, blank=True, on_delete=models.SET_NULL, related_name='teams_led', help_text="Optional team lead")
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='developer_teams_created')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.company_name} - {self.name}"

    def member_count(self):
        return self.members.count()

    class Meta:
        ordering = ['-created_at']
        unique_together = ('customer', 'name')


class DeveloperTeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'customer', 'member_count', 'team_lead', 'is_active', 'created_at')
    list_filter = ('is_active', 'customer')
    search_fields = ('name', 'customer__company_name')
    readonly_fields = ('created_at',)
    filter_horizontal = ('members',)


# Team Trainings (per customer/team)
class TeamTraining(models.Model):
    """A training program scoped to a customer/team, grouping resources and an optional quiz."""
    customer = models.ForeignKey('onboarding.Customer', on_delete=models.CASCADE, related_name='team_trainings')
    developer_team = models.ForeignKey('onboarding.DeveloperTeam', null=True, blank=True, on_delete=models.SET_NULL, related_name='trainings', help_text="Optional: assign to specific team within customer")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    resources = models.ManyToManyField('onboarding.Resource', blank=True, related_name='team_trainings')
    quiz = models.ForeignKey('onboarding.Quiz', null=True, blank=True, on_delete=models.SET_NULL, related_name='team_trainings')
    
    # Date fields for training schedule
    start_date = models.DateField(null=True, blank=True, help_text="When this training becomes available")
    end_date = models.DateField(null=True, blank=True, help_text="When this training closes/expires")
    due_date = models.DateField(null=True, blank=True, help_text="Complete by date for this training")
    
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='team_trainings_created')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        team_part = f" ({self.developer_team.name})" if self.developer_team else ""
        return f"{self.customer.company_name}{team_part} - {self.name}"

    def total_resources(self):
        return self.resources.count()
    
    def auto_enroll_team_members(self, assigned_by=None):
        """Automatically enroll all members of the assigned developer team."""
        if not self.developer_team:
            return 0
        
        enrolled_count = 0
        for member in self.developer_team.members.all():
            enrollment, created = DeveloperTrainingEnrollment.objects.get_or_create(
                developer=member,
                training=self,
                defaults={'assigned_by': assigned_by}
            )
            if created:
                enrolled_count += 1
        return enrolled_count

    class Meta:
        ordering = ['-created_at']


class TeamTrainingAdmin(admin.ModelAdmin):
    list_display = ('name', 'customer', 'developer_team', 'is_active', 'total_resources', 'created_at')
    list_filter = ('is_active', 'customer', 'developer_team')
    search_fields = ('name', 'customer__company_name', 'developer_team__name')
    readonly_fields = ('created_at',)


class TrainingProject(models.Model):
    """
    A project assignment within a training that students must complete and submit.
    """
    training = models.ForeignKey(TeamTraining, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    description = models.TextField(help_text="Detailed description of the project requirements")
    order = models.PositiveIntegerField(default=0, help_text="Order of this project within the training")
    
    # Optional requirements
    requirements = models.TextField(blank=True, help_text="Specific requirements or acceptance criteria")
    resources_hint = models.TextField(blank=True, help_text="Helpful resources or hints for completing the project")
    
    # Grading
    max_score = models.PositiveIntegerField(default=10, help_text="Maximum score (default 1-10)")
    passing_score = models.PositiveIntegerField(default=7, help_text="Minimum score to pass")
    
    # Due date
    due_date = models.DateField(null=True, blank=True, help_text="Due date for this project")
    
    is_required = models.BooleanField(default=True, help_text="Is this project required to complete the training?")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['training', 'order']
        unique_together = ('training', 'order')
    
    def __str__(self):
        return f"{self.training.name} - Project: {self.title}"


class TrainingProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'training', 'order', 'max_score', 'passing_score', 'due_date', 'is_required', 'is_active')
    list_filter = ('is_active', 'is_required', 'training__customer')
    search_fields = ('title', 'training__name', 'description')
    readonly_fields = ('created_at', 'updated_at')


class ProjectSubmission(models.Model):
    """
    A student's submission for a training project.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('in_review', 'In Review'),
        ('revision_requested', 'Revision Requested'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    project = models.ForeignKey(TrainingProject, on_delete=models.CASCADE, related_name='submissions')
    developer = models.ForeignKey('onboarding.TeamMember', on_delete=models.CASCADE, related_name='project_submissions')
    enrollment = models.ForeignKey('onboarding.DeveloperTrainingEnrollment', on_delete=models.CASCADE, related_name='project_submissions', null=True, blank=True)
    
    # Student submission
    github_url = models.URLField(help_text="GitHub repository URL for the project")
    student_description = models.TextField(blank=True, help_text="Student's description of their submission")
    student_notes = models.TextField(blank=True, help_text="Additional notes from the student")
    
    # Submission status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    submitted_at = models.DateTimeField(null=True, blank=True)
    
    # Teacher/Admin review
    score = models.PositiveIntegerField(null=True, blank=True, help_text="Score from 1-10 (or up to max_score)")
    teacher_notes = models.TextField(blank=True, help_text="Feedback and notes from the reviewer")
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_submissions')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-submitted_at', '-created_at']
        unique_together = ('project', 'developer')
    
    def __str__(self):
        return f"{self.developer} - {self.project.title}"
    
    def is_passing(self):
        """Check if the submission has a passing score"""
        if self.score is None:
            return False
        return self.score >= self.project.passing_score
    
    def submit(self):
        """Mark the submission as submitted"""
        from django.utils import timezone
        self.status = 'submitted'
        self.submitted_at = timezone.now()
        self.save()
    
    def approve(self, reviewer, score, notes=''):
        """Approve the submission with a score"""
        from django.utils import timezone
        self.status = 'approved'
        self.score = score
        if notes:
            self.teacher_notes = notes
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.save()
    
    def request_revision(self, reviewer, notes=''):
        """Request revision from the student"""
        from django.utils import timezone
        self.status = 'revision_requested'
        if notes:
            self.teacher_notes = notes
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.save()
    
    def reject(self, reviewer, notes=''):
        """Reject the submission"""
        from django.utils import timezone
        self.status = 'rejected'
        if notes:
            self.teacher_notes = notes
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.save()


class ProjectSubmissionAdmin(admin.ModelAdmin):
    list_display = ('developer', 'project', 'status', 'score', 'submitted_at', 'reviewed_at')
    list_filter = ('status', 'project__training__customer', 'project__training')
    search_fields = ('developer__first_name', 'developer__last_name', 'project__title', 'github_url')
    readonly_fields = ('created_at', 'updated_at', 'submitted_at', 'reviewed_at')


class TrainingSection(models.Model):
    """
    A section within a team training with start/end dates.
    Each section can have multiple resources and quizzes.
    """
    training = models.ForeignKey(TeamTraining, on_delete=models.CASCADE, related_name='sections')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0, help_text="Order of this section within the training")
    
    # Date constraints for the section
    start_date = models.DateField(null=True, blank=True, help_text="When this section becomes available")
    end_date = models.DateField(null=True, blank=True, help_text="Complete by date for this section")
    
    # Quizzes for this section (can have multiple)
    quizzes = models.ManyToManyField('onboarding.Quiz', blank=True, related_name='training_sections', help_text="Quizzes to complete at the end of this section")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['training', 'order', 'start_date']
        unique_together = ('training', 'order')
    
    def __str__(self):
        return f"{self.training.name} - Section {self.order}: {self.name}"
    
    def total_resources(self):
        return self.section_resources.count()
    
    def is_available(self):
        """Check if the section is currently available based on dates"""
        from django.utils import timezone
        today = timezone.now().date()
        if self.start_date and today < self.start_date:
            return False
        return True
    
    def is_overdue(self):
        """Check if the section is past its end date"""
        from django.utils import timezone
        today = timezone.now().date()
        if self.end_date and today > self.end_date:
            return True
        return False
    
    def days_until_due(self):
        """Calculate days remaining until due date"""
        from django.utils import timezone
        today = timezone.now().date()
        if self.end_date:
            delta = self.end_date - today
            return delta.days
        return None


class TrainingSectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'training', 'order', 'start_date', 'end_date', 'is_active', 'total_resources', 'status_display')
    list_filter = ('is_active', 'training', 'training__customer')
    search_fields = ('name', 'description', 'training__name', 'training__customer__company_name')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('quizzes',)
    ordering = ('training', 'order')
    
    def status_display(self, obj):
        from django.utils.html import format_html
        if obj.is_overdue():
            return format_html('<span style="color: red;">⚠️ Overdue</span>')
        elif obj.is_available():
            days = obj.days_until_due()
            if days is not None and days <= 7:
                return format_html('<span style="color: orange;">⏰ {} days left</span>', days)
            return format_html('<span style="color: green;">✅ Available</span>')
        else:
            return format_html('<span style="color: gray;">🔒 Not yet available</span>')
    status_display.short_description = 'Status'
    
    fieldsets = (
        ('Section Information', {
            'fields': ('training', 'name', 'description', 'order', 'is_active')
        }),
        ('Schedule', {
            'fields': ('start_date', 'end_date'),
            'description': 'Set when this section becomes available and when it should be completed by.'
        }),
        ('Quizzes', {
            'fields': ('quizzes',),
            'description': 'Select quizzes that must be completed at the end of this section.'
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class SectionResource(models.Model):
    """
    A resource within a training section, with support for video embeds.
    """
    VIDEO_SOURCE_CHOICES = [
        ('none', 'No Video'),
        ('youtube', 'YouTube'),
        ('cloudflare', 'CloudFlare Stream'),
        ('mp4', 'Direct MP4 URL'),
        ('vimeo', 'Vimeo'),
    ]
    
    section = models.ForeignKey(TrainingSection, on_delete=models.CASCADE, related_name='section_resources')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0, help_text="Order of this resource within the section")
    
    # Standard resource fields
    link = models.URLField(blank=True, help_text="URL to external resource")
    document = models.FileField(upload_to='section_resources/', blank=True, help_text="Upload a document or file")
    
    # Video embed fields
    video_source = models.CharField(max_length=20, choices=VIDEO_SOURCE_CHOICES, default='none')
    video_url = models.URLField(blank=True, help_text="Video URL (YouTube, CloudFlare, Vimeo link, or direct MP4 URL)")
    video_embed_code = models.TextField(blank=True, help_text="Custom embed code if needed (optional - auto-generated for YouTube/CloudFlare/Vimeo)")
    video_duration_minutes = models.PositiveIntegerField(null=True, blank=True, help_text="Estimated video duration in minutes")
    
    # Estimated time to complete this resource
    estimated_time_minutes = models.PositiveIntegerField(null=True, blank=True, help_text="Estimated time to complete this resource in minutes")
    
    is_required = models.BooleanField(default=True, help_text="Is this resource required to complete the section?")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['section', 'order']
        unique_together = ('section', 'order')
    
    def __str__(self):
        return f"{self.section.name} - {self.title}"
    
    def get_video_embed_html(self):
        """Generate embed HTML based on video source"""
        if self.video_embed_code:
            return self.video_embed_code
        
        if not self.video_url:
            return ''
        
        if self.video_source == 'youtube':
            # Extract video ID from various YouTube URL formats
            video_id = self._extract_youtube_id()
            if video_id:
                return f'<iframe width="560" height="315" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'
        
        elif self.video_source == 'cloudflare':
            # CloudFlare Stream embed
            # URL format: https://watch.cloudflarestream.com/{video_id}
            # or: https://customer-{code}.cloudflarestream.com/{video_id}/iframe
            video_id = self._extract_cloudflare_id()
            if video_id:
                return f'<iframe src="https://iframe.cloudflarestream.com/{video_id}" style="border: none;" allow="accelerometer; gyroscope; autoplay; encrypted-media; picture-in-picture;" allowfullscreen="true" width="560" height="315"></iframe>'
        
        elif self.video_source == 'vimeo':
            # Extract Vimeo video ID
            video_id = self._extract_vimeo_id()
            if video_id:
                return f'<iframe src="https://player.vimeo.com/video/{video_id}" width="560" height="315" frameborder="0" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe>'
        
        elif self.video_source == 'mp4':
            return f'<video width="560" height="315" controls><source src="{self.video_url}" type="video/mp4">Your browser does not support the video tag.</video>'
        
        return ''
    
    def _extract_youtube_id(self):
        """Extract YouTube video ID from URL"""
        import re
        if not self.video_url:
            return None
        # Match various YouTube URL formats
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})',
        ]
        for pattern in patterns:
            match = re.search(pattern, self.video_url)
            if match:
                return match.group(1)
        return None
    
    def _extract_cloudflare_id(self):
        """Extract CloudFlare Stream video ID from URL"""
        import re
        if not self.video_url:
            return None
        # Match CloudFlare stream URLs
        patterns = [
            r'cloudflarestream\.com\/([a-zA-Z0-9]+)',
            r'videodelivery\.net\/([a-zA-Z0-9]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, self.video_url)
            if match:
                return match.group(1)
        return None
    
    def _extract_vimeo_id(self):
        """Extract Vimeo video ID from URL"""
        import re
        if not self.video_url:
            return None
        # Match Vimeo URLs
        pattern = r'vimeo\.com\/(?:video\/)?(\d+)'
        match = re.search(pattern, self.video_url)
        if match:
            return match.group(1)
        return None
    
    def has_video(self):
        return self.video_source != 'none' and bool(self.video_url)


class SectionResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'order', 'video_source', 'is_required', 'estimated_time_minutes', 'is_active')
    list_filter = ('is_active', 'is_required', 'video_source', 'section__training', 'section__training__customer')
    search_fields = ('title', 'description', 'section__name', 'section__training__name')
    readonly_fields = ('created_at', 'updated_at', 'video_preview')
    ordering = ('section', 'order')
    
    def video_preview(self, obj):
        from django.utils.html import format_html
        if obj.has_video():
            embed = obj.get_video_embed_html()
            if embed:
                return format_html('<div style="max-width: 400px;">{}</div>', embed)
        return '-'
    video_preview.short_description = 'Video Preview'
    
    fieldsets = (
        ('Resource Information', {
            'fields': ('section', 'title', 'description', 'order', 'is_required', 'is_active')
        }),
        ('Content', {
            'fields': ('link', 'document', 'estimated_time_minutes')
        }),
        ('Video Embed', {
            'fields': ('video_source', 'video_url', 'video_embed_code', 'video_duration_minutes', 'video_preview'),
            'description': 'Add a video from YouTube, CloudFlare Stream, Vimeo, or a direct MP4 URL. The embed code will be auto-generated, or you can provide custom embed code.'
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class SectionProgress(models.Model):
    """
    Tracks a developer's progress through a training section.
    """
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    enrollment = models.ForeignKey('DeveloperTrainingEnrollment', on_delete=models.CASCADE, related_name='section_progress')
    section = models.ForeignKey(TrainingSection, on_delete=models.CASCADE, related_name='progress_records')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('enrollment', 'section')
        ordering = ['section__order']
    
    def __str__(self):
        return f"{self.enrollment.developer} - {self.section.name} ({self.status})"
    
    def resources_completed(self):
        """Count resources completed in this section"""
        return self.resource_progress.filter(is_completed=True).count()
    
    def resources_total(self):
        """Total resources in this section"""
        return self.section.section_resources.filter(is_active=True, is_required=True).count()
    
    def progress_percent(self):
        """Calculate completion percentage"""
        total = self.resources_total()
        if total == 0:
            return 100 if self.status == 'completed' else 0
        return int((self.resources_completed() / total) * 100)
    
    def quizzes_passed(self):
        """Check if all section quizzes have been passed"""
        from django.db.models import Q
        required_quizzes = self.section.quizzes.all()
        if not required_quizzes.exists():
            return True
        # Check quiz answers for this developer
        passed_count = QuizAnswer.objects.filter(
            team_member=self.enrollment.developer,
            question__quiz__in=required_quizzes,
            evaluator_score__gte=3  # Assuming 3+ is passing
        ).values('question__quiz').distinct().count()
        return passed_count >= required_quizzes.count()


class SectionProgressAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'section', 'status', 'progress_percent', 'started_at', 'completed_at')
    list_filter = ('status', 'section__training', 'section__training__customer')
    search_fields = ('enrollment__developer__first_name', 'enrollment__developer__last_name', 'section__name')
    readonly_fields = ('started_at', 'completed_at')


class ResourceProgress(models.Model):
    """
    Tracks a developer's progress on individual resources within a section.
    """
    section_progress = models.ForeignKey(SectionProgress, on_delete=models.CASCADE, related_name='resource_progress')
    resource = models.ForeignKey(SectionResource, on_delete=models.CASCADE, related_name='progress_records')
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_spent_minutes = models.PositiveIntegerField(default=0, help_text="Time spent on this resource in minutes")
    notes = models.TextField(blank=True, help_text="Developer notes on this resource")
    
    class Meta:
        unique_together = ('section_progress', 'resource')
    
    def __str__(self):
        status = "✓" if self.is_completed else "○"
        return f"{status} {self.section_progress.enrollment.developer} - {self.resource.title}"


class ResourceProgressAdmin(admin.ModelAdmin):
    list_display = ('section_progress', 'resource', 'is_completed', 'time_spent_minutes', 'completed_at')
    list_filter = ('is_completed', 'resource__section__training')
    search_fields = ('section_progress__enrollment__developer__first_name', 'resource__title')
    readonly_fields = ('completed_at',)


class DeveloperTrainingEnrollment(models.Model):
    """Enrollment of a developer into a specific team training."""
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    developer = models.ForeignKey('onboarding.TeamMember', on_delete=models.CASCADE, related_name='training_enrollments')
    training = models.ForeignKey(TeamTraining, on_delete=models.CASCADE, related_name='enrollments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='trainings_assigned')
    assigned_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.developer} → {self.training} ({self.status})"

    def progress_percent(self):
        """Compute percent of training resources marked complete by this developer."""
        total = self.training.resources.count()
        if total == 0:
            return 0
        from django.db.models import Q
        completed = TeamMemberResource.objects.filter(
            team_member=self.developer,
            resource__in=self.training.resources.all(),
            percentage_complete__gte=100,
        ).count()
        return int((completed / total) * 100)

    class Meta:
        unique_together = ('developer', 'training')
        ordering = ['-assigned_at']


class DeveloperTrainingEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('developer', 'training', 'status', 'assigned_at', 'progress_percent')
    list_filter = ('status', 'assigned_at', 'training__customer')
    search_fields = ('developer__first_name', 'developer__last_name', 'training__name', 'training__customer__company_name')
    readonly_fields = ('assigned_at',)


class DevelopmentAgency(models.Model):
    INDUSTRY_CHOICES = [
        ('Technology', 'Technology'),
        ('Finance', 'Finance'),
        ('Healthcare', 'Healthcare'),
        ('Government', 'Government'),
        ('Non/Profit-NGO', 'Non/Profit-NGO'),
        ('Manufacturing', 'Manufacturing'),
        ('Agriculture', 'Agriculture'),
        ('Climate Tech', 'Climate Tech'),
        # Add more industry choices as needed
    ]
    
    AGENCY_TYPE = [
        ('Marketing', 'Marketing'),
        ('Software Development', 'Software Development'),
        ('Finance', 'Finance'),
        ('Investment Fund', 'Investment Fund'),
        ('Legal', 'Legal'),
        ('Accounting/Taxes', 'Accounting/Taxes'),
        ('Accelerator/Incubator', 'Accelerator/Incubator'),
    ]
    
    # User account for agency login
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, help_text="User account for agency login")
    
    agency_name = models.CharField(max_length=255)
    team_size = models.CharField(max_length=100, blank=True)
    skills = models.TextField(blank=True)
    background = models.TextField(blank=True)
    hourly_rate = models.CharField(max_length=100, blank=True)
    project_rate = models.CharField(max_length=100, blank=True)
    industries_worked = models.CharField(max_length=100, choices=INDUSTRY_CHOICES, blank=True)
    agency_type = models.CharField(max_length=100, choices=AGENCY_TYPE, blank=True)
    github_repository = models.URLField(blank=True)
    contact_name = models.CharField(max_length=255)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20, blank=True)
    linkedin_url = models.URLField(blank=True)
    how_they_found_us = models.CharField(max_length=255, blank=True)
    logo = models.ImageField(upload_to='agency-logo', null=True, blank=True)
    is_approved = models.BooleanField(default=False, help_text="Agency approved to access portal")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    def __str__(self):
        return self.agency_name
    
    def get_developers(self):
        """Get all developers associated with this agency"""
        return self.team_members.all()
    
    def get_assignments(self):
        """Get all customer assignments for this agency's developers"""
        from onboarding.models import CustomerDeveloperAssignment
        return CustomerDeveloperAssignment.objects.filter(developer__agency=self)


class DevelopmentAgencyAdmin(admin.ModelAdmin):
    list_display = ('agency_name','contact_email', 'agency_type')
    search_fields = ('agency_name','contact_email')
    list_filter = ('agency_type', 'industries_worked')
    display = 'Development Agencies'


# Customer Model for Client Portal
class Customer(models.Model):
    """
    Represents a client/customer who can view assigned developer profiles
    and sign engagement contracts
    """
    company_name = models.CharField(max_length=255)
    contact_name = models.CharField(max_length=255)
    contact_email = models.EmailField(unique=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    
    # Authentication (simple username/password)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=255, help_text="Plain text password (will be hashed)")
    
    # Shareable token for passwordless access
    share_token = models.CharField(max_length=64, unique=True, blank=True, help_text="Unique token for shareable URL")
    
    # Assigned developers
    assigned_developers = models.ManyToManyField(
        TeamMember, 
        through='CustomerDeveloperAssignment',
        related_name='assigned_to_customers'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, help_text="Internal notes about this customer")
    
    def __str__(self):
        return f"{self.company_name} ({self.contact_name})"
    
    def check_password(self, password):
        """Simple password check (should use hashing in production)"""
        return self.password == password
    
    def generate_share_token(self):
        """Generate a unique share token for passwordless access"""
        import secrets
        # Try to generate a unique token (with collision retry)
        max_attempts = 10
        for _ in range(max_attempts):
            token = secrets.token_urlsafe(48)
            # Check if token is unique
            if not Customer.objects.filter(share_token=token).exists():
                self.share_token = token
                self.save()
                return self.share_token
        # If all attempts fail (extremely unlikely), raise error
        raise ValueError("Unable to generate unique share token after multiple attempts")
    
    def get_share_url(self, request=None):
        """Get the shareable URL for this customer"""
        if not self.share_token:
            self.generate_share_token()
        if request:
            from django.urls import reverse
            return request.build_absolute_uri(reverse('onboarding:customer_shared_view', kwargs={'token': self.share_token}))
        return f"/onboarding/client/shared/{self.share_token}/"
    
    class Meta:
        ordering = ['-created_at']


# Through model for Customer-Developer relationship with approval status
class CustomerDeveloperAssignment(models.Model):
    """
    Tracks which developers are assigned to which customers
    and whether the customer has approved/rejected them
    """
    APPROVAL_STATUS = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    developer = models.ForeignKey(TeamMember, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=APPROVAL_STATUS, default='pending')
    assigned_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, help_text="Customer notes about this developer")
    
    # Phase 1: Approval tracking
    approved_by = models.ForeignKey('CompanyAdmin', on_delete=models.SET_NULL, null=True, blank=True, related_name='developer_approvals', help_text="Company admin who approved")
    notification_sent = models.BooleanField(default=False, help_text="Notification sent to developer")
    
    def __str__(self):
        return f"{self.customer.company_name} - {self.developer.first_name} {self.developer.last_name} ({self.status})"
    
    class Meta:
        unique_together = ('customer', 'developer')
        ordering = ['-assigned_at']


class CustomerDeveloperAssignmentAdmin(admin.ModelAdmin):
    list_display = ('customer', 'developer', 'status', 'assigned_at', 'reviewed_at')
    list_filter = ('status', 'assigned_at')
    search_fields = ('customer__company_name', 'developer__first_name', 'developer__last_name')
    readonly_fields = ('assigned_at', 'reviewed_at')


class CustomerDeveloperAssignmentInline(admin.TabularInline):
    """Inline admin for managing developer assignments within Customer admin"""
    model = CustomerDeveloperAssignment
    extra = 1
    fields = ('developer', 'developer_profile_link', 'status', 'assigned_at', 'reviewed_at', 'notes')
    readonly_fields = ('developer_profile_link', 'assigned_at', 'reviewed_at')
    
    def developer_profile_link(self, obj):
        if obj.developer:
            from django.urls import reverse
            from django.utils.html import format_html
            url = reverse('admin:onboarding_teammember_change', args=[obj.developer.id])
            return format_html(
                '<a href="{}" target="_blank">📋 View Full Profile</a>',
                url
            )
        return '-'
    developer_profile_link.short_description = 'Profile'


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'contact_name', 'contact_email', 'username', 'has_share_token', 'developer_count', 'is_active', 'created_at')
    search_fields = ('company_name', 'contact_name', 'contact_email', 'username', 'share_token')
    list_filter = ('is_active', 'created_at')
    readonly_fields = ('created_at', 'last_login', 'share_url_display')
    actions = ['generate_share_tokens', 'regenerate_share_tokens']
    inlines = [CustomerDeveloperAssignmentInline]
    
    def has_share_token(self, obj):
        return bool(obj.share_token)
    has_share_token.boolean = True
    has_share_token.short_description = 'Has Token'
    
    def developer_count(self, obj):
        count = obj.assigned_developers.count()
        if count == 0:
            return '-'
        approved = CustomerDeveloperAssignment.objects.filter(customer=obj, status='approved').count()
        pending = CustomerDeveloperAssignment.objects.filter(customer=obj, status='pending').count()
        rejected = CustomerDeveloperAssignment.objects.filter(customer=obj, status='rejected').count()
        return f'{count} total (✓{approved} ⏳{pending} ✗{rejected})'
    developer_count.short_description = 'Developers'
    
    def share_url_display(self, obj):
        from django.utils.html import format_html
        if obj.share_token:
            url = obj.get_share_url()
            return format_html(
                '<div style="margin: 10px 0;">'
                '<strong>Shareable Link:</strong><br>'
                '<a href="{}" target="_blank" style="color: #0066cc; font-size: 14px;">{}</a><br>'
                '<small style="color: #666;">Send this link to the customer - no login required</small>'
                '</div>',
                url, url
            )
        return format_html(
            '<span style="color: #cc6600;">⚠️ No token yet - use "Generate share token" action below</span>'
        )
    share_url_display.short_description = 'Shareable URL'
    
    def generate_share_tokens(self, request, queryset):
        """Generate tokens for customers that don't have one"""
        count = 0
        for customer in queryset:
            if not customer.share_token:
                customer.generate_share_token()
                count += 1
        if count > 0:
            self.message_user(request, f'✅ Generated share tokens for {count} customer(s).')
        else:
            self.message_user(request, 'All selected customers already have share tokens.', level='warning')
    generate_share_tokens.short_description = '🔗 Generate share token (for customers without one)'
    
    def regenerate_share_tokens(self, request, queryset):
        """Regenerate tokens for all selected customers (invalidates old links)"""
        count = 0
        for customer in queryset:
            customer.generate_share_token()
            count += 1
        self.message_user(request, f'🔄 Regenerated share tokens for {count} customer(s). Old links are now invalid.')
    regenerate_share_tokens.short_description = '🔄 Regenerate share token (invalidates old link)'
    
    fieldsets = (
        ('Company Information', {
            'fields': ('company_name', 'contact_name', 'contact_email', 'contact_phone')
        }),
        ('Authentication', {
            'fields': ('username', 'password', 'is_active')
        }),
        ('Shareable Access', {
            'fields': ('share_url_display',),
            'description': 'Use the action dropdown below to generate or regenerate a shareable link. '
                          'The customer can click this link to view assigned developers, approve/reject them, '
                          'and sign contracts - no login required.'
        }),
        ('Metadata', {
            'fields': ('notes', 'created_at', 'last_login'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Auto-generate share token on first save if not exists"""
        super().save_model(request, obj, form, change)
        if not obj.share_token:
            obj.generate_share_token()


class CustomerIntakeRequestAdmin(admin.ModelAdmin):
    list_display = ('company', 'name', 'email', 'status', 'timeline', 'assigned_to', 'has_customer', 'created_at')
    list_filter = ('status', 'timeline', 'created_at', 'assigned_to')
    search_fields = ('company', 'name', 'email', 'products', 'preferences')
    readonly_fields = ('created_at', 'updated_at', 'responded_at', 'products_display', 'customer_link')
    actions = ['mark_as_in_review', 'mark_as_contacted', 'convert_to_customers']
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'company')
        }),
        ('Request Details', {
            'fields': ('products_display', 'timeline', 'preferences')
        }),
        ('Workflow', {
            'fields': ('status', 'assigned_to', 'customer_link', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'responded_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_customer(self, obj):
        return obj.customer is not None
    has_customer.boolean = True
    has_customer.short_description = 'Converted'
    
    def products_display(self, obj):
        from django.utils.html import format_html
        products = obj.get_products_list()
        if not products:
            return '-'
        items = ''.join([f'<li>{p}</li>' for p in products])
        return format_html(f'<ul style="margin: 0; padding-left: 20px;">{items}</ul>')
    products_display.short_description = 'Requested Products'
    
    def customer_link(self, obj):
        from django.utils.html import format_html
        from django.urls import reverse
        if obj.customer:
            url = reverse('admin:onboarding_customer_change', args=[obj.customer.pk])
            return format_html(
                '<a href="{}" target="_blank">📋 {} ({})</a>',
                url, obj.customer.company_name, obj.customer.username
            )
        return '-'
    customer_link.short_description = 'Linked Customer'
    
    def mark_as_in_review(self, request, queryset):
        updated = queryset.filter(status='new').update(status='in_review', assigned_to=request.user)
        self.message_user(request, f'✅ Marked {updated} request(s) as in review.')
    mark_as_in_review.short_description = '📋 Mark as In Review (assign to me)'
    
    def mark_as_contacted(self, request, queryset):
        count = 0
        for obj in queryset:
            if obj.status in ['new', 'in_review']:
                obj.mark_contacted(request.user)
                count += 1
        self.message_user(request, f'✅ Marked {count} request(s) as contacted.')
    mark_as_contacted.short_description = '📞 Mark as Contacted'
    
    def convert_to_customers(self, request, queryset):
        converted = []
        errors = []
        for obj in queryset:
            if obj.can_convert_to_customer():
                customer = obj.convert_to_customer()
                if customer:
                    converted.append(obj.company)
            else:
                errors.append(obj.company)
        
        if converted:
            self.message_user(request, f'✅ Converted {len(converted)} request(s) to customers: {", ".join(converted)}')
        if errors:
            self.message_user(request, f'⚠️ Could not convert {len(errors)} request(s): {", ".join(errors)} (already converted or invalid status)', level='warning')
    convert_to_customers.short_description = '🎯 Convert to Customer Records'


# Contract Model for Engagement Agreements
class Contract(models.Model):
    """
    Represents an engagement contract between Buildly and a customer
    for specific developers
    """
    CONTRACT_STATUS = [
        ('draft', 'Draft'),
        ('pending', 'Pending Signature'),
        ('signed', 'Signed'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]
    
    CONTRACT_TYPE = [
        ('onboarding', 'Onboarding'),
        ('engagement', 'Engagement'),
        ('maintenance', 'Maintenance'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='contracts')
    developers = models.ManyToManyField(TeamMember, related_name='contracts')
    
    # Contract details
    title = models.CharField(max_length=255)
    contract_text = models.TextField(help_text="Full contract text")
    contract_type = models.CharField(max_length=20, choices=CONTRACT_TYPE, default='engagement')
    start_date = models.DateField()
    end_date = models.DateField()
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    project_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Signature (Phase 1)
    status = models.CharField(max_length=20, choices=CONTRACT_STATUS, default='draft')
    signature_data = models.TextField(blank=True, help_text="Base64 encoded signature image")
    signed_by = models.CharField(max_length=255, blank=True, help_text="Full name of person who signed")
    signed_at = models.DateTimeField(null=True, blank=True)
    signature_ip = models.GenericIPAddressField(null=True, blank=True, help_text="IP address of signer")
    signature_timestamp = models.DateTimeField(null=True, blank=True, help_text="Server timestamp of signature")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    contract_hash = models.CharField(max_length=64, blank=True, help_text="SHA256 hash for contract verification and tamper detection")
    
    # Generated files
    pdf_file = models.FileField(upload_to='contracts/pdf/', blank=True, null=True, help_text="Generated PDF of signed contract")
    png_file = models.FileField(upload_to='contracts/png/', blank=True, null=True, help_text="Generated PNG image of signed contract")
    
    # Billing (Phase 4)
    billing_enabled = models.BooleanField(default=False, help_text="Enable billing for this contract")
    billing_enabled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='contracts_billing_enabled')
    billing_enabled_at = models.DateTimeField(null=True, blank=True)
    billing_start_date = models.DateField(null=True, blank=True)
    billing_end_date = models.DateField(null=True, blank=True)
    billing_frequency = models.CharField(max_length=20, choices=[('monthly', 'Monthly'), ('quarterly', 'Quarterly'), ('custom', 'Custom')], default='monthly')
    auto_renew = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='contracts_created')
    
    def __str__(self):
        return f"{self.title} - {self.customer.company_name}"
    
    def generate_hash(self):
        """Generate SHA256 hash of contract for verification"""
        import hashlib
        hash_content = f"{self.contract_text}{self.signature_data}{self.signed_by}{self.signed_at}"
        return hashlib.sha256(hash_content.encode('utf-8')).hexdigest()
    
    def verify_hash(self):
        """Verify that stored hash matches current contract content"""
        if not self.contract_hash:
            return False
        return self.contract_hash == self.generate_hash()
    
    @property
    def total_amount(self):
        """Calculate total amount from all line items"""
        return sum(item.total for item in self.line_items.all())
    
    class Meta:
        ordering = ['-created_at']


class ContractLineItem(models.Model):
    """Dynamic line items for contract services and fees"""
    SERVICE_TYPES = [
        ('team', 'Team Services'),
        ('hosting', 'Hosting Fees'),
        ('product_mgmt', 'Product Management'),
        ('training', 'Developer Training & Onboarding'),
        ('architecture', 'Software Architecture'),
        ('other', 'Other Services'),
    ]
    
    BILLING_FREQUENCY = [
        ('one_time', 'One-Time'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annually', 'Annually'),
    ]
    
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='line_items')
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES)
    description = models.CharField(max_length=255, help_text="Service description")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1, help_text="Quantity or hours")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price per unit")
    billing_frequency = models.CharField(max_length=20, choices=BILLING_FREQUENCY, default='monthly')
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Discount %")
    notes = models.TextField(blank=True, help_text="Additional notes or conditions")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def subtotal(self):
        return self.quantity * self.unit_price
    
    @property
    def discount_amount(self):
        return (self.subtotal * self.discount_percentage) / 100
    
    @property
    def total(self):
        return self.subtotal - self.discount_amount
    
    def __str__(self):
        return f"{self.get_service_type_display()}: {self.description} - ${self.total}"
    
    class Meta:
        ordering = ['service_type', 'created_at']


class CertificationLevel(models.Model):
    """Dynamic certification levels/types that can be assigned to developers"""
    LEVEL_TYPES = [
        ('junior', 'Junior'),
        ('intermediate', 'Intermediate'),
        ('senior', 'Senior'),
        ('expert', 'Expert'),
        ('specialty', 'Specialty'),
    ]
    
    TRACK_CHOICES = [
        ('frontend', 'Frontend Developer'),
        ('backend', 'Backend Developer'),
        ('product_manager', 'Product Manager'),
        ('ai', 'AI/ML Developer'),
        ('general', 'General'),
    ]
    
    name = models.CharField(max_length=255, help_text="e.g., Frontend React Specialist, Python Backend Expert")
    level_type = models.CharField(max_length=20, choices=LEVEL_TYPES, default='intermediate')
    track = models.CharField(max_length=50, choices=TRACK_CHOICES, default='general', help_text="Certification track")
    description = models.TextField(help_text="What this certification demonstrates")
    requirements = models.TextField(help_text="Skills and experience required", blank=True)
    
    # Required trainings and sections to complete for this certification
    required_trainings = models.ManyToManyField('TeamTraining', blank=True, related_name='certifications', help_text="Trainings that must be completed for this certification")
    required_sections = models.ManyToManyField('TrainingSection', blank=True, related_name='certifications', help_text="Specific training sections required for this certification")
    required_quizzes = models.ManyToManyField('Quiz', blank=True, related_name='certifications', help_text="Quizzes that must be passed for this certification")
    
    # Minimum quiz score required (percentage)
    min_quiz_score = models.PositiveIntegerField(default=70, help_text="Minimum passing score percentage for quizzes")
    
    # Optional pricing if certification requires payment
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Cost to obtain certification")
    
    # Skills covered
    skills = models.TextField(help_text="Comma-separated list of skills", blank=True)
    
    # Template customization
    badge_color = models.CharField(max_length=7, default='#3B82F6', help_text="Hex color for badge")
    certificate_template = models.CharField(max_length=50, default='default', help_text="Template name for certificate design")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='certifications_created')
    
    def __str__(self):
        return f"{self.name} ({self.get_level_type_display()})"
    
    def total_required_items(self):
        """Count total required trainings, sections, and quizzes"""
        return (
            self.required_trainings.count() + 
            self.required_sections.count() + 
            self.required_quizzes.count()
        )
    
    def check_developer_eligibility(self, developer):
        """Check if a developer meets all requirements for this certification"""
        # Check trainings
        for training in self.required_trainings.all():
            enrollment = DeveloperTrainingEnrollment.objects.filter(
                developer=developer,
                training=training,
                status='completed'
            ).first()
            if not enrollment:
                return False, f"Training '{training.name}' not completed"
        
        # Check sections
        for section in self.required_sections.all():
            progress = SectionProgress.objects.filter(
                enrollment__developer=developer,
                section=section,
                status='completed'
            ).first()
            if not progress:
                return False, f"Section '{section.name}' not completed"
        
        # Check quizzes
        for quiz in self.required_quizzes.all():
            # Check if developer has answered all questions with passing score
            total_questions = quiz.questions.count()
            if total_questions == 0:
                continue
            
            passed_answers = QuizAnswer.objects.filter(
                team_member=developer,
                question__quiz=quiz,
                evaluator_score__gte=3  # Assuming 3+ out of 4 is passing
            ).count()
            
            if passed_answers < total_questions:
                return False, f"Quiz '{quiz.name}' not passed"
        
        return True, "All requirements met"
    
    class Meta:
        ordering = ['level_type', 'name']


class DeveloperCertification(models.Model):
    """Tracks certifications earned by developers with hash verification"""
    developer = models.ForeignKey(TeamMember, on_delete=models.CASCADE, related_name='certifications_earned')
    certification_level = models.ForeignKey(CertificationLevel, on_delete=models.CASCADE, related_name='awarded_to')
    
    # Certification details
    issued_at = models.DateTimeField(auto_now_add=True)
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='certifications_issued')
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Certification expiration date")
    
    # Score/completion data
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Exam score or completion percentage")
    notes = models.TextField(blank=True, help_text="Additional notes about certification")
    
    # Verification
    certificate_hash = models.CharField(max_length=64, blank=True, help_text="SHA256 hash for certificate verification")
    certificate_number = models.CharField(max_length=50, unique=True, help_text="Unique certificate ID")
    
    # Generated files
    pdf_file = models.FileField(upload_to='certificates/pdf/', blank=True, null=True)
    png_file = models.FileField(upload_to='certificates/png/', blank=True, null=True)
    
    is_revoked = models.BooleanField(default=False, help_text="Revoke if certification is no longer valid")
    revoked_at = models.DateTimeField(null=True, blank=True)
    revoked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='certifications_revoked')
    revoked_reason = models.TextField(blank=True)
    
    def save(self, *args, **kwargs):
        if not self.certificate_number:
            # Generate unique certificate number
            import uuid
            self.certificate_number = f"CERT-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)
    
    def generate_hash(self):
        """Generate SHA256 hash for certificate verification"""
        import hashlib
        hash_content = f"{self.certificate_number}{self.developer.id}{self.certification_level.id}{self.issued_at}{self.score}"
        return hashlib.sha256(hash_content.encode('utf-8')).hexdigest()
    
    def verify_hash(self):
        """Verify certificate hasn't been tampered with"""
        if not self.certificate_hash:
            return False
        return self.certificate_hash == self.generate_hash()
    
    @property
    def is_expired(self):
        if not self.expires_at:
            return False
        from django.utils import timezone
        return timezone.now() > self.expires_at
    
    @property
    def is_valid(self):
        return not self.is_revoked and not self.is_expired
    
    def __str__(self):
        return f"{self.developer.user.get_full_name()} - {self.certification_level.name}"
    
    class Meta:
        ordering = ['-issued_at']
        unique_together = ['developer', 'certification_level']


class ContractAdmin(admin.ModelAdmin):
    list_display = ('title', 'customer', 'status', 'start_date', 'end_date', 'signed_at', 'created_at')
    search_fields = ('title', 'customer__company_name', 'signed_by')
    list_filter = ('status', 'start_date', 'signed_at')
    filter_horizontal = ('developers',)
    readonly_fields = ('signed_at', 'created_at', 'ip_address')
    
    fieldsets = (
        ('Contract Information', {
            'fields': ('customer', 'title', 'contract_text', 'developers')
        }),
        ('Terms', {
            'fields': ('start_date', 'end_date', 'hourly_rate', 'project_rate')
        }),
        ('Signature', {
            'fields': ('status', 'signature_data', 'signed_by', 'signed_at', 'ip_address')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )

# ===== Phase 1: Customer Portal Models =====

class CompanyProfile(models.Model):
    """Extended profile for Customer companies"""
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='company_profile')
    industry = models.CharField(max_length=100, blank=True)
    company_size = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to='company-logos/', null=True, blank=True)
    billing_address = models.TextField(blank=True)
    tax_id = models.CharField(max_length=50, blank=True)
    is_labs_customer = models.BooleanField(default=False)
    labs_account_email = models.EmailField(blank=True)
    labs_discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.customer.company_name} Profile"


class CompanyAdmin(models.Model):
    """Company admin users with specific roles and permissions"""
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Administrator'),
        ('billing', 'Billing Only'),
        ('viewer', 'Viewer'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='admins')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='company_admin_roles')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')
    can_approve_developers = models.BooleanField(default=False)
    can_sign_contracts = models.BooleanField(default=False)
    can_manage_billing = models.BooleanField(default=False)
    invited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='company_admin_invitations')
    invited_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('customer', 'user')
        ordering = ['-accepted_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.customer.company_name} ({self.role})"
    
    def set_permissions_for_role(self):
        """Auto-set permissions based on role"""
        if self.role == 'owner':
            self.can_approve_developers = True
            self.can_sign_contracts = True
            self.can_manage_billing = True
        elif self.role == 'admin':
            self.can_approve_developers = True
            self.can_sign_contracts = True
            self.can_manage_billing = False
        elif self.role == 'billing':
            self.can_approve_developers = False
            self.can_sign_contracts = False
            self.can_manage_billing = True
        else:  # viewer
            self.can_approve_developers = False
            self.can_sign_contracts = False
            self.can_manage_billing = False


class Notification(models.Model):
    """In-app notifications for users"""
    NOTIFICATION_TYPES = [
        ('community_approved', 'Community Approval'),
        ('team_approved', 'Team Approval'),
        ('team_removal_requested', 'Removal Request'),
        ('team_removal_30day', '30-Day Removal Notice'),
        ('contract_ready', 'Contract Ready to Sign'),
        ('contract_signed', 'Contract Signed'),
        ('billing_enabled', 'Billing Enabled'),
        ('custom', 'Custom Message'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    link_url = models.URLField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    related_customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    related_contract = models.ForeignKey(Contract, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.recipient.get_full_name()}"


class LabsAccount(models.Model):
    """Labs platform account linked to Buildly TeamMember"""
    team_member = models.OneToOneField(TeamMember, on_delete=models.CASCADE, related_name='labs_account')
    labs_username = models.CharField(max_length=255)
    labs_email = models.EmailField()
    labs_token = models.TextField(help_text="Encrypted API token for Labs")  # Will be encrypted in utils
    labs_user_id = models.CharField(max_length=255, unique=True)
    buildly_profile_linked = models.BooleanField(default=True, help_text="One unified Buildly profile")
    linked_at = models.DateTimeField(auto_now_add=True)
    last_sync = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.team_member.first_name} {self.team_member.last_name} - Labs: {self.labs_username}"
    
    class Meta:
        ordering = ['-linked_at']


class CustomerIntakeRequest(models.Model):
    """Tracks customer intake form submissions for admin review and conversion"""
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_review', 'In Review'),
        ('contacted', 'Contacted'),
        ('converted', 'Converted to Customer'),
        ('rejected', 'Rejected'),
    ]
    
    # Form data
    name = models.CharField(max_length=255)
    email = models.EmailField()
    company = models.CharField(max_length=255)
    products = models.TextField(help_text="Comma-separated list of selected products")
    timeline = models.CharField(max_length=100)
    preferences = models.TextField(blank=True)
    
    # Workflow tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                    related_name='assigned_intake_requests')
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='intake_requests', 
                                help_text="Linked Customer record if converted")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    
    # Admin notes
    admin_notes = models.TextField(blank=True, help_text="Internal notes for tracking")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Customer Intake Request'
        verbose_name_plural = 'Customer Intake Requests'
    
    def __str__(self):
        return f"{self.company} - {self.name} ({self.get_status_display()})"
    
    def get_products_list(self):
        """Return list of product names"""
        if self.products:
            return [p.strip() for p in self.products.split(',')]
        return []
    
    def can_convert_to_customer(self):
        """Check if request can be converted to Customer"""
        return self.status in ['new', 'in_review', 'contacted'] and self.customer is None
    
    def mark_contacted(self, user=None):
        """Mark request as contacted"""
        self.status = 'contacted'
        self.responded_at = timezone.now()
        if user and not self.assigned_to:
            self.assigned_to = user
        self.save()
    
    def convert_to_customer(self, username=None):
        """Convert intake request to Customer record"""
        if not self.can_convert_to_customer():
            return None
        
        # Check if customer already exists with this email
        existing_customer = Customer.objects.filter(contact_email=self.email).first()
        if existing_customer:
            self.customer = existing_customer
            self.status = 'converted'
            self.save()
            return existing_customer
        
        # Create new customer
        customer = Customer.objects.create(
            company_name=self.company,
            contact_name=self.name,
            contact_email=self.email,
            username=username or self.email.split('@')[0],
            notes=f"Converted from intake request. Products: {self.products}. Timeline: {self.timeline}. Preferences: {self.preferences}"
        )
        customer.generate_share_token()
        
        self.customer = customer
        self.status = 'converted'
        self.save()
        
        return customer


# ==================== FORGE PROJECT REQUESTS ====================

class ForgeProjectRequest(models.Model):
    """Developer request to start or contribute to a Forge project"""
    
    REQUEST_TYPE_CHOICES = [
        ('start_new', 'Start a New Project'),
        ('fork_existing', 'Fork an Existing Project'),
        ('contribute', 'Contribute to Existing Project'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]
    
    TEAM_SIZE_CHOICES = [
        ('solo', 'Solo (Just me)'),
        ('small', 'Small (2-3 people)'),
        ('medium', 'Medium (4-6 people)'),
        ('large', 'Large (7+ people)'),
    ]
    
    # Core request info
    developer = models.ForeignKey(TeamMember, on_delete=models.CASCADE, related_name='forge_project_requests')
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPE_CHOICES, default='start_new')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Project details
    project_name = models.CharField(max_length=200, help_text="Proposed project name")
    project_description = models.TextField(help_text="Describe the project, its goals, and intended features")
    target_category = models.CharField(max_length=100, blank=True, help_text="Target category (e.g., AI, Analytics, CRM)")
    technologies = models.TextField(blank=True, help_text="Technologies you plan to use")
    github_repo_url = models.URLField(blank=True, help_text="GitHub repo URL (if forking or contributing)")
    
    # Existing Forge app reference (for fork/contribute)
    existing_forge_app = models.ForeignKey('forge.ForgeApp', on_delete=models.SET_NULL, null=True, blank=True,
                                           related_name='fork_requests', help_text="Existing Forge app to fork/contribute to")
    
    # Team recruitment
    needs_team = models.BooleanField(default=False, help_text="Looking for team members to help")
    team_size = models.CharField(max_length=20, choices=TEAM_SIZE_CHOICES, default='solo', blank=True)
    roles_needed = models.TextField(blank=True, help_text="Roles/skills you're looking for (e.g., Frontend, Backend, DevOps)")
    team_description = models.TextField(blank=True, help_text="Describe the team and collaboration expectations")
    
    # Recruited team members
    team_members = models.ManyToManyField(TeamMember, blank=True, related_name='forge_project_teams',
                                          help_text="Developers who joined this project")
    
    # Timeline
    estimated_duration = models.CharField(max_length=100, blank=True, help_text="Estimated project duration")
    planned_start_date = models.DateField(null=True, blank=True, help_text="When you plan to start")
    
    # Admin review
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='reviewed_forge_requests')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True, help_text="Admin notes/feedback")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Forge Project Request'
        verbose_name_plural = 'Forge Project Requests'
    
    def __str__(self):
        return f"{self.project_name} by {self.developer.first_name} {self.developer.last_name}"
    
    def submit(self):
        """Submit the request for review"""
        self.status = 'submitted'
        self.submitted_at = timezone.now()
        self.save()
    
    def approve(self, reviewer):
        """Approve the project request"""
        self.status = 'approved'
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.save()
    
    def reject(self, reviewer, notes=''):
        """Reject the project request"""
        self.status = 'rejected'
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        if notes:
            self.review_notes = notes
        self.save()
    
    def start_project(self):
        """Mark project as in progress"""
        self.status = 'in_progress'
        self.save()
    
    def complete_project(self):
        """Mark project as completed"""
        self.status = 'completed'
        self.save()


class ForgeProjectRequestAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'developer', 'request_type', 'status', 'needs_team', 'created_at')
    list_filter = ('status', 'request_type', 'needs_team')
    search_fields = ('project_name', 'developer__first_name', 'developer__last_name', 'project_description')
    readonly_fields = ('created_at', 'updated_at', 'submitted_at', 'reviewed_at')
    filter_horizontal = ('team_members',)

admin.site.register(ForgeProjectRequest, ForgeProjectRequestAdmin)


class ForgeTeamApplication(models.Model):
    """Application from a developer to join a Forge project team"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    project_request = models.ForeignKey(ForgeProjectRequest, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(TeamMember, on_delete=models.CASCADE, related_name='forge_team_applications')
    
    # Application details
    message = models.TextField(help_text="Why do you want to join this project?")
    skills_offered = models.TextField(help_text="What skills/experience can you contribute?")
    hours_available = models.PositiveIntegerField(default=10, help_text="Hours per week you can contribute")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    response_message = models.TextField(blank=True, help_text="Response from project lead")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['project_request', 'applicant']
        verbose_name = 'Forge Team Application'
        verbose_name_plural = 'Forge Team Applications'
    
    def __str__(self):
        return f"{self.applicant.first_name} applying to {self.project_request.project_name}"
    
    def accept(self, response=''):
        """Accept the application"""
        self.status = 'accepted'
        self.response_message = response
        self.responded_at = timezone.now()
        self.save()
        # Add applicant to project team
        self.project_request.team_members.add(self.applicant)
    
    def reject(self, response=''):
        """Reject the application"""
        self.status = 'rejected'
        self.response_message = response
        self.responded_at = timezone.now()
        self.save()
    
    def withdraw(self):
        """Withdraw the application"""
        self.status = 'withdrawn'
        self.responded_at = timezone.now()
        self.save()


class ForgeTeamApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'project_request', 'status', 'hours_available', 'created_at')
    list_filter = ('status',)
    search_fields = ('applicant__first_name', 'applicant__last_name', 'project_request__project_name')
    readonly_fields = ('created_at', 'responded_at')

admin.site.register(ForgeTeamApplication, ForgeTeamApplicationAdmin)


class CommunityNewsletter(models.Model):
    """Track community newsletters sent to all approved developers"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sending', 'Sending'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
    ]
    
    subject = models.CharField(max_length=255)
    custom_message = models.TextField(help_text="Custom message to include at the top of the newsletter")
    
    # Stats snapshot at time of sending
    total_customers = models.PositiveIntegerField(default=0)
    total_developers = models.PositiveIntegerField(default=0)
    new_customers_this_month = models.PositiveIntegerField(default=0)
    new_developers_this_month = models.PositiveIntegerField(default=0)
    active_opportunities = models.PositiveIntegerField(default=0)
    open_source_projects = models.PositiveIntegerField(default=0)
    
    # Tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    recipient_count = models.PositiveIntegerField(default=0, help_text="Number of developers who received the email")
    failed_count = models.PositiveIntegerField(default=0, help_text="Number of failed email sends")
    pending_count = models.PositiveIntegerField(default=0, help_text="Number of pending email sends")
    sent_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='newsletters_sent')
    sent_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-sent_at']
        verbose_name = 'Community Newsletter'
        verbose_name_plural = 'Community Newsletters'
    
    def __str__(self):
        return f"Newsletter: {self.subject} ({self.sent_at.strftime('%Y-%m-%d')})"
    
    def update_counts(self):
        """Update recipient counts from actual recipient records"""
        self.recipient_count = self.recipients.filter(status='sent').count()
        self.failed_count = self.recipients.filter(status='failed').count()
        self.pending_count = self.recipients.filter(status='pending').count()
        if self.pending_count == 0 and self.status == 'sending':
            self.status = 'completed'
        self.save()
    
    @classmethod
    def get_newsletter_sent_this_month(cls):
        """Check if a newsletter has been sent this month"""
        from django.utils import timezone
        today = timezone.now().date()
        first_day_of_month = today.replace(day=1)
        return cls.objects.filter(sent_at__date__gte=first_day_of_month).exists()
    
    @classmethod
    def should_show_reminder(cls):
        """Check if we should show a reminder to send the newsletter"""
        from django.utils import timezone
        import calendar
        today = timezone.now().date()
        _, last_day = calendar.monthrange(today.year, today.month)
        days_until_end = last_day - today.day
        
        # Show reminder if newsletter not sent this month AND within last 7 days of month
        if not cls.get_newsletter_sent_this_month() and days_until_end <= 7:
            return True
        return False


class NewsletterRecipient(models.Model):
    """Track individual newsletter recipients and their delivery status"""
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ]
    
    newsletter = models.ForeignKey(CommunityNewsletter, on_delete=models.CASCADE, related_name='recipients')
    developer = models.ForeignKey(TeamMember, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField()  # Store email in case developer is deleted
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['status', 'email']
        unique_together = ['newsletter', 'email']
    
    def __str__(self):
        return f"{self.email} - {self.status}"


class CommunityNewsletterAdmin(admin.ModelAdmin):
    list_display = ('subject', 'sent_by', 'sent_at', 'recipient_count', 'failed_count', 'total_developers')
    list_filter = ('sent_at',)
    search_fields = ('subject', 'custom_message')
    readonly_fields = ('sent_at', 'recipient_count', 'failed_count', 'total_customers', 'total_developers', 
                      'new_customers_this_month', 'new_developers_this_month',
                      'active_opportunities', 'open_source_projects')

admin.site.register(CommunityNewsletter, CommunityNewsletterAdmin)


# ==================== API Key Model ====================

class APIKey(models.Model):
    """Model for storing API keys for partner integrations"""
    import secrets
    import hashlib
    
    KEY_TYPES = [
        ('inbound', 'Inbound (Partner → CollabHub)'),
        ('outbound', 'Outbound (CollabHub → Partner)'),
    ]
    
    PARTNERS = [
        ('labs', 'Buildly Labs'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=100)
    partner = models.CharField(max_length=50, choices=PARTNERS, default='labs')
    key_type = models.CharField(max_length=20, choices=KEY_TYPES)
    key_prefix = models.CharField(max_length=20, help_text="First 12 chars of key for identification")
    key_hash = models.CharField(max_length=64, help_text="SHA-256 hash of the full key")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    last_used = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "API Key"
        verbose_name_plural = "API Keys"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_key_type_display()}) - {self.key_prefix}..."
    
    @classmethod
    def generate_key(cls, prefix="collabhub"):
        """Generate a new API key with prefix"""
        import secrets
        random_part = secrets.token_urlsafe(32)
        return f"{prefix}_{random_part}"
    
    @classmethod
    def hash_key(cls, key):
        """Create SHA-256 hash of key for storage"""
        import hashlib
        return hashlib.sha256(key.encode()).hexdigest()
    
    @classmethod
    def create_inbound_key(cls, name, partner='labs', created_by=None, notes=''):
        """Create a new inbound API key (for partners to call CollabHub)"""
        full_key = cls.generate_key(prefix="collabhub")
        
        api_key = cls.objects.create(
            name=name,
            partner=partner,
            key_type='inbound',
            key_prefix=full_key[:12],
            key_hash=cls.hash_key(full_key),
            created_by=created_by,
            notes=notes,
        )
        
        # Return both the model and the full key (only shown once)
        return api_key, full_key
    
    @classmethod
    def verify_key(cls, key):
        """Verify an incoming API key and return the APIKey object if valid"""
        from django.utils.timezone import now
        if not key:
            return None
        
        key_hash = cls.hash_key(key)
        try:
            api_key = cls.objects.get(
                key_hash=key_hash,
                key_type='inbound',
                is_active=True
            )
            # Update last used timestamp
            api_key.last_used = now()
            api_key.save(update_fields=['last_used'])
            return api_key
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def store_outbound_key(cls, name, key, partner='labs', created_by=None, notes=''):
        """Store an outbound API key (provided by partner for CollabHub to use)"""
        return cls.objects.create(
            name=name,
            partner=partner,
            key_type='outbound',
            key_prefix=key[:12] if len(key) > 12 else key[:4],
            key_hash=cls.hash_key(key),
            created_by=created_by,
            notes=notes,
        )


class APIKeyAdmin(admin.ModelAdmin):
    list_display = ('name', 'partner', 'key_type', 'key_prefix', 'is_active', 'created_at', 'last_used')
    list_filter = ('partner', 'key_type', 'is_active')
    search_fields = ('name', 'key_prefix')
    readonly_fields = ('key_prefix', 'key_hash', 'created_at', 'last_used')

admin.site.register(APIKey, APIKeyAdmin)


# ==================== Community Certification System ====================

class CertificationTrack(models.Model):
    """Defines certification tracks (Frontend, Backend, Product Manager)"""
    TRACK_CHOICES = [
        ('frontend', 'Frontend Developer'),
        ('backend', 'Backend Developer'),
        ('product_manager', 'Product Manager'),
    ]
    
    key = models.CharField(max_length=50, unique=True, choices=TRACK_CHOICES)
    name = models.CharField(max_length=100)
    description = models.TextField(help_text="Description of this certification track")
    icon = models.CharField(max_length=50, default='code', help_text="Icon name for display")
    color = models.CharField(max_length=7, default='#3B82F6', help_text="Hex color for track branding")
    
    # Track-specific settings
    focus_methodology = models.CharField(max_length=100, blank=True, help_text="e.g., 'RAD Process' for Product Manager")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    
    class Meta:
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class CertificationTrackAdmin(admin.ModelAdmin):
    list_display = ('name', 'key', 'color', 'is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    ordering = ('order',)

admin.site.register(CertificationTrack, CertificationTrackAdmin)


class CommunityCertificationLevel(models.Model):
    """
    Community certification levels (Level 1, Level 2, Level 3/Senior) for each track.
    Extends the base CertificationLevel concept with community-specific features.
    """
    LEVEL_CHOICES = [
        (1, 'Level 1 - Foundation'),
        (2, 'Level 2 - Practitioner'),
        (3, 'Level 3 - Senior'),
    ]
    
    track = models.ForeignKey(CertificationTrack, on_delete=models.CASCADE, related_name='levels')
    level = models.PositiveIntegerField(choices=LEVEL_CHOICES)
    name = models.CharField(max_length=255, help_text="e.g., 'Frontend Developer Level 1'")
    description = models.TextField(help_text="What this level demonstrates")
    
    # Requirements
    required_resources_count = models.PositiveIntegerField(default=6, help_text="Min resources to complete")
    required_quizzes_count = models.PositiveIntegerField(default=3, help_text="Number of quizzes required")
    required_projects_count = models.PositiveIntegerField(default=2, help_text="Projects requiring review")
    min_quiz_score = models.PositiveIntegerField(default=70, help_text="Minimum passing score %")
    
    # Linked certification level for issuing certificates
    certification_level = models.OneToOneField(
        CertificationLevel, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='community_level',
        help_text="Linked CertificationLevel for certificate generation"
    )
    
    # Resources and quizzes linked to this level
    resources = models.ManyToManyField('Resource', blank=True, related_name='community_cert_levels')
    quizzes = models.ManyToManyField('Quiz', blank=True, related_name='community_cert_levels')
    
    # Badge customization
    badge_icon = models.CharField(max_length=100, blank=True, help_text="Badge icon URL or emoji")
    badge_color = models.CharField(max_length=7, default='#3B82F6')
    
    # Reviewer requirements
    min_reviewer_level = models.PositiveIntegerField(default=2, help_text="Min level required to review projects for this cert")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['track', 'level']
        unique_together = ['track', 'level']
    
    def __str__(self):
        return f"{self.track.name} - Level {self.level}"
    
    def get_level_display_name(self):
        """Return display name like 'Level 1 - Foundation'"""
        return dict(self.LEVEL_CHOICES).get(self.level, f'Level {self.level}')


class CommunityCertificationLevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'track', 'level', 'required_resources_count', 'required_quizzes_count', 
                   'required_projects_count', 'is_active')
    list_filter = ('track', 'level', 'is_active')
    search_fields = ('name', 'description')
    filter_horizontal = ('resources', 'quizzes')

admin.site.register(CommunityCertificationLevel, CommunityCertificationLevelAdmin)


class CommunityBadge(models.Model):
    """
    Defines community achievement badges (First Contribution, Active Contributor, etc.)
    Separate from certification badges - these are for community participation.
    """
    BADGE_TYPES = [
        ('contribution', 'Contribution Badge'),
        ('achievement', 'Achievement Badge'),
        ('leadership', 'Leadership Badge'),
        ('special', 'Special Badge'),
    ]
    
    key = models.CharField(max_length=50, unique=True, help_text="Unique identifier, e.g., 'first_contribution'")
    name = models.CharField(max_length=100)
    description = models.TextField(help_text="What this badge represents")
    badge_type = models.CharField(max_length=20, choices=BADGE_TYPES, default='achievement')
    
    # Visual
    icon = models.CharField(max_length=50, default='🌟', help_text="Emoji or icon class")
    color = models.CharField(max_length=7, default='#FCD34D', help_text="Badge background color")
    
    # Earning criteria (for automatic awarding)
    auto_award = models.BooleanField(default=False, help_text="Can be automatically awarded based on criteria")
    criteria_type = models.CharField(max_length=50, blank=True, help_text="e.g., 'github_commits', 'quiz_completed'")
    criteria_threshold = models.PositiveIntegerField(null=True, blank=True, help_text="Threshold value for auto-award")
    
    # Ordering/display
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'name']
    
    def __str__(self):
        return f"{self.icon} {self.name}"


class CommunityBadgeAdmin(admin.ModelAdmin):
    list_display = ('icon', 'name', 'badge_type', 'auto_award', 'is_active', 'order')
    list_filter = ('badge_type', 'auto_award', 'is_active')
    search_fields = ('name', 'description', 'key')
    ordering = ('order',)

admin.site.register(CommunityBadge, CommunityBadgeAdmin)


class DeveloperBadge(models.Model):
    """Tracks badges earned by developers"""
    developer = models.ForeignKey(TeamMember, on_delete=models.CASCADE, related_name='community_badges')
    badge = models.ForeignKey(CommunityBadge, on_delete=models.CASCADE, related_name='awarded_to')
    
    awarded_at = models.DateTimeField(auto_now_add=True)
    awarded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                   help_text="Admin who awarded, null if auto-awarded")
    notes = models.TextField(blank=True, help_text="Why badge was awarded")
    
    # For verification
    verification_hash = models.CharField(max_length=64, blank=True)
    
    class Meta:
        ordering = ['-awarded_at']
        unique_together = ['developer', 'badge']
    
    def __str__(self):
        return f"{self.developer.first_name} {self.developer.last_name} - {self.badge.name}"
    
    def save(self, *args, **kwargs):
        if not self.verification_hash:
            import hashlib
            content = f"{self.developer.id}-{self.badge.id}-{self.awarded_at}"
            self.verification_hash = hashlib.sha256(content.encode()).hexdigest()
        super().save(*args, **kwargs)


class DeveloperBadgeAdmin(admin.ModelAdmin):
    list_display = ('developer', 'badge', 'awarded_at', 'awarded_by')
    list_filter = ('badge', 'awarded_at')
    search_fields = ('developer__first_name', 'developer__last_name', 'badge__name')
    raw_id_fields = ('developer',)

admin.site.register(DeveloperBadge, DeveloperBadgeAdmin)


class CertificationProject(models.Model):
    """
    Defines project requirements for certification levels.
    Projects are reviewed by senior members before certification can be granted.
    """
    PROJECT_TYPES = [
        ('small', 'Small Project'),
        ('medium', 'Medium Project'),
        ('complex', 'Complex Project'),
        ('document', 'Document/PRD'),
    ]
    
    certification_level = models.ForeignKey(
        CommunityCertificationLevel, 
        on_delete=models.CASCADE, 
        related_name='required_projects'
    )
    
    name = models.CharField(max_length=255, help_text="e.g., 'Build a REST API with Authentication'")
    description = models.TextField(help_text="Detailed project requirements")
    project_type = models.CharField(max_length=20, choices=PROJECT_TYPES, default='medium')
    
    # Requirements
    requirements_checklist = models.TextField(
        help_text="JSON list of requirements, e.g., ['Has README', 'Includes tests', 'Deployed']",
        blank=True,
        default='[]'
    )
    
    # Resources/examples
    example_repo = models.URLField(blank=True, help_text="Link to example project")
    rubric_document = models.FileField(upload_to='certification_projects/', blank=True, null=True)
    
    # Scoring
    max_score = models.PositiveIntegerField(default=100)
    passing_score = models.PositiveIntegerField(default=70)
    
    order = models.PositiveIntegerField(default=0, help_text="Order within certification level")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['certification_level', 'order']
    
    def __str__(self):
        return f"{self.certification_level} - {self.name}"
    
    def get_requirements_list(self):
        """Parse requirements_checklist JSON into list"""
        import json
        try:
            return json.loads(self.requirements_checklist)
        except:
            return []


class CertificationProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'certification_level', 'project_type', 'passing_score', 'is_active')
    list_filter = ('certification_level__track', 'project_type', 'is_active')
    search_fields = ('name', 'description')
    ordering = ('certification_level', 'order')

admin.site.register(CertificationProject, CertificationProjectAdmin)


class CertificationProjectSubmission(models.Model):
    """Tracks developer project submissions for community certification"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted for Review'),
        ('under_review', 'Under Review'),
        ('revisions_needed', 'Revisions Needed'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    developer = models.ForeignKey(TeamMember, on_delete=models.CASCADE, related_name='cert_project_submissions')
    project = models.ForeignKey(CertificationProject, on_delete=models.CASCADE, related_name='cert_submissions')
    
    # Submission details
    title = models.CharField(max_length=255, help_text="Project title")
    description = models.TextField(help_text="Brief description of what was built")
    repository_url = models.URLField(help_text="GitHub/GitLab repository URL")
    live_url = models.URLField(blank=True, help_text="Live demo URL if applicable")
    
    # Additional files
    documentation = models.FileField(upload_to='certification_submissions/', blank=True, null=True)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    submitted_at = models.DateTimeField(null=True, blank=True)
    
    # Scoring
    final_score = models.PositiveIntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['developer', 'project']
        verbose_name = "Certification Project Submission"
        verbose_name_plural = "Certification Project Submissions"
    
    def __str__(self):
        return f"{self.developer.first_name} - {self.project.name} ({self.status})"
    
    @property
    def is_passing(self):
        if self.final_score is None:
            return False
        return self.final_score >= self.project.passing_score


class CertificationProjectSubmissionAdmin(admin.ModelAdmin):
    list_display = ('developer', 'project', 'status', 'final_score', 'submitted_at', 'created_at')
    list_filter = ('status', 'project__certification_level__track')
    search_fields = ('developer__first_name', 'developer__last_name', 'title')
    raw_id_fields = ('developer',)
    readonly_fields = ('created_at', 'updated_at')

admin.site.register(CertificationProjectSubmission, CertificationProjectSubmissionAdmin)


class CertificationProjectReview(models.Model):
    """Reviews of certification project submissions by senior/certified members"""
    RUBRIC_SCORES = [
        (0, '0 - Not Present'),
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Excellent'),
    ]
    
    submission = models.ForeignKey(CertificationProjectSubmission, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(TeamMember, on_delete=models.CASCADE, related_name='cert_project_reviews_given')
    
    # Review scores (each out of 25, totaling 100)
    code_quality_score = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(26)], default=0,
                                                      help_text="Code quality and best practices (0-25)")
    functionality_score = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(26)], default=0,
                                                       help_text="Functionality and correctness (0-25)")
    documentation_score = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(26)], default=0,
                                                       help_text="README, comments, docs (0-25)")
    creativity_score = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(26)], default=0,
                                                    help_text="Problem-solving and innovation (0-25)")
    
    # Feedback
    overall_feedback = models.TextField(help_text="Overall feedback for the developer")
    strengths = models.TextField(blank=True, help_text="What was done well")
    improvements = models.TextField(blank=True, help_text="Areas for improvement")
    
    # Status
    is_complete = models.BooleanField(default=False)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['submission', 'reviewer']
        verbose_name = "Certification Project Review"
        verbose_name_plural = "Certification Project Reviews"
    
    def __str__(self):
        return f"Review by {self.reviewer.first_name} for {self.submission.title}"
    
    @property
    def total_score(self):
        return (self.code_quality_score + self.functionality_score + 
                self.documentation_score + self.creativity_score)
    
    def save(self, *args, **kwargs):
        if self.is_complete and not self.reviewed_at:
            self.reviewed_at = timezone.now()
        super().save(*args, **kwargs)


class CertificationProjectReviewAdmin(admin.ModelAdmin):
    list_display = ('submission', 'reviewer', 'total_score', 'is_complete', 'reviewed_at')
    list_filter = ('is_complete', 'submission__project__certification_level__track')
    search_fields = ('submission__title', 'reviewer__first_name', 'reviewer__last_name')
    raw_id_fields = ('reviewer', 'submission')
    readonly_fields = ('created_at',)

admin.site.register(CertificationProjectReview, CertificationProjectReviewAdmin)


class DeveloperCertificationProgress(models.Model):
    """
    Tracks a developer's progress toward a community certification level.
    This is the main tracking model for the certification journey.
    """
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('pending_review', 'Pending Project Review'),
        ('completed', 'Completed'),
    ]
    
    developer = models.ForeignKey(TeamMember, on_delete=models.CASCADE, related_name='certification_progress')
    certification_level = models.ForeignKey(CommunityCertificationLevel, on_delete=models.CASCADE, 
                                            related_name='developer_progress')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    
    # Progress tracking
    resources_completed = models.ManyToManyField('Resource', blank=True, related_name='completed_by_progress')
    quizzes_passed = models.ManyToManyField('Quiz', blank=True, related_name='passed_by_progress')
    
    # Scores
    average_quiz_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Timestamps
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Issued certificate (once completed)
    issued_certificate = models.ForeignKey(
        DeveloperCertification, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='certification_progress'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['certification_level__track', 'certification_level__level']
        unique_together = ['developer', 'certification_level']
        verbose_name_plural = "Developer Certification Progress"
    
    def __str__(self):
        return f"{self.developer.first_name} - {self.certification_level} ({self.status})"
    
    @property
    def resources_progress_percent(self):
        """Calculate percentage of required resources completed"""
        required = self.certification_level.required_resources_count
        completed = self.resources_completed.count()
        if required == 0:
            return 100
        return min(100, int((completed / required) * 100))
    
    @property
    def quizzes_progress_percent(self):
        """Calculate percentage of required quizzes passed"""
        required = self.certification_level.required_quizzes_count
        passed = self.quizzes_passed.count()
        if required == 0:
            return 100
        return min(100, int((passed / required) * 100))
    
    @property
    def projects_progress_percent(self):
        """Calculate percentage of required projects approved"""
        required = self.certification_level.required_projects_count
        approved = CertificationProjectSubmission.objects.filter(
            developer=self.developer,
            project__certification_level=self.certification_level,
            status='approved'
        ).count()
        if required == 0:
            return 100
        return min(100, int((approved / required) * 100))
    
    @property
    def overall_progress_percent(self):
        """Calculate overall progress (weighted average)"""
        return int((self.resources_progress_percent + self.quizzes_progress_percent + 
                   self.projects_progress_percent) / 3)
    
    def check_completion(self):
        """Check if all requirements are met for certification"""
        # Check resources
        if self.resources_completed.count() < self.certification_level.required_resources_count:
            return False, "More resources need to be completed"
        
        # Check quizzes
        if self.quizzes_passed.count() < self.certification_level.required_quizzes_count:
            return False, "More quizzes need to be passed"
        
        # Check quiz score average
        if self.average_quiz_score and self.average_quiz_score < self.certification_level.min_quiz_score:
            return False, f"Average quiz score ({self.average_quiz_score}%) is below minimum ({self.certification_level.min_quiz_score}%)"
        
        # Check projects
        approved_projects = CertificationProjectSubmission.objects.filter(
            developer=self.developer,
            project__certification_level=self.certification_level,
            status='approved'
        ).count()
        
        if approved_projects < self.certification_level.required_projects_count:
            return False, "More project submissions need to be approved"
        
        return True, "All requirements met"


class DeveloperCertificationProgressAdmin(admin.ModelAdmin):
    list_display = ('developer', 'certification_level', 'status', 'overall_progress_percent', 
                   'started_at', 'completed_at')
    list_filter = ('status', 'certification_level__track', 'certification_level__level')
    search_fields = ('developer__first_name', 'developer__last_name')
    raw_id_fields = ('developer', 'issued_certificate')
    filter_horizontal = ('resources_completed', 'quizzes_passed')
    readonly_fields = ('created_at', 'updated_at')

admin.site.register(DeveloperCertificationProgress, DeveloperCertificationProgressAdmin)


class CertifiedReviewer(models.Model):
    """
    Tracks which developers are certified to review project submissions.
    Initially seeded with senior members, expanded as more reach Level 2+.
    """
    developer = models.OneToOneField(TeamMember, on_delete=models.CASCADE, related_name='reviewer_status')
    
    # Reviewer level (determines what they can review)
    reviewer_level = models.PositiveIntegerField(default=2, help_text="1=L1 only, 2=L1+L2, 3=All levels")
    
    # Tracks they can review
    can_review_frontend = models.BooleanField(default=False)
    can_review_backend = models.BooleanField(default=False)
    can_review_product = models.BooleanField(default=False)
    
    # Stats
    total_reviews_completed = models.PositiveIntegerField(default=0)
    average_review_time_days = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='approved_reviewers')
    approved_at = models.DateTimeField(auto_now_add=True)
    
    notes = models.TextField(blank=True, help_text="Admin notes about this reviewer")
    
    class Meta:
        ordering = ['-reviewer_level', 'developer__first_name']
    
    def __str__(self):
        tracks = []
        if self.can_review_frontend:
            tracks.append('FE')
        if self.can_review_backend:
            tracks.append('BE')
        if self.can_review_product:
            tracks.append('PM')
        return f"{self.developer.first_name} {self.developer.last_name} (L{self.reviewer_level}) - {', '.join(tracks)}"
    
    def can_review_level(self, target_level):
        """Check if reviewer can review submissions for a given certification level"""
        # Level 3 reviewers can review all levels
        # Level 2 reviewers can review Level 1 and 2
        # Level 1 reviewers can only review Level 1
        return self.reviewer_level >= target_level


class CertifiedReviewerAdmin(admin.ModelAdmin):
    list_display = ('developer', 'reviewer_level', 'can_review_frontend', 'can_review_backend', 
                   'can_review_product', 'total_reviews_completed', 'is_active')
    list_filter = ('reviewer_level', 'can_review_frontend', 'can_review_backend', 
                  'can_review_product', 'is_active')
    search_fields = ('developer__first_name', 'developer__last_name', 'developer__email')
    raw_id_fields = ('developer',)

admin.site.register(CertifiedReviewer, CertifiedReviewerAdmin)


class DeveloperPublicProfile(models.Model):
    """
    Extended public profile settings for developers.
    Controls what's visible on public profile pages and integrates with open.build.
    """
    developer = models.OneToOneField(TeamMember, on_delete=models.CASCADE, related_name='public_profile')
    
    # Profile visibility
    is_public = models.BooleanField(default=True, help_text="Show profile on public pages")
    show_email = models.BooleanField(default=False)
    show_github_stats = models.BooleanField(default=True)
    show_certifications = models.BooleanField(default=True)
    show_badges = models.BooleanField(default=True)
    show_projects = models.BooleanField(default=True)
    show_skills = models.BooleanField(default=True)
    
    # Custom profile fields
    headline = models.CharField(max_length=255, blank=True, help_text="e.g., 'Full-Stack Developer & Open Source Enthusiast'")
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    twitter = models.CharField(max_length=100, blank=True, help_text="Twitter/X username")
    
    # Open.build profile link
    openbuild_profile_url = models.URLField(blank=True, help_text="Your open.build profile URL")
    
    # Featured content
    featured_project_url = models.URLField(blank=True, help_text="GitHub URL of featured repo")
    featured_project_description = models.CharField(max_length=255, blank=True)
    
    # GitHub OAuth integration
    github_access_token = models.CharField(max_length=255, blank=True, help_text="GitHub OAuth access token for API calls")
    github_token_updated = models.DateTimeField(null=True, blank=True)
    
    # GitHub stats (cached)
    github_commits = models.PositiveIntegerField(default=0)
    github_repos = models.PositiveIntegerField(default=0)
    github_prs = models.PositiveIntegerField(default=0)
    github_followers = models.PositiveIntegerField(default=0)
    github_stars = models.PositiveIntegerField(default=0)
    github_stats_updated = models.DateTimeField(null=True, blank=True)
    
    # Profile slug for URL
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    
    # open.build integration
    openbuild_synced = models.BooleanField(default=False)
    openbuild_sync_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Developer Public Profile"
        verbose_name_plural = "Developer Public Profiles"
    
    def __str__(self):
        return f"Profile: {self.developer.first_name} {self.developer.last_name}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            # Generate slug from username or name
            from django.utils.text import slugify
            base_slug = slugify(f"{self.developer.first_name}-{self.developer.last_name}")
            self.slug = base_slug
            
            # Handle duplicates
            counter = 1
            while DeveloperPublicProfile.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return f"/profile/{self.slug}/"


class DeveloperPublicProfileAdmin(admin.ModelAdmin):
    list_display = ('developer', 'slug', 'headline', 'is_public', 'show_github_stats', 
                   'github_commits', 'github_repos', 'github_followers')
    list_filter = ('is_public', 'show_github_stats', 'show_certifications', 'openbuild_synced')
    search_fields = ('developer__first_name', 'developer__last_name', 'headline', 'slug')
    raw_id_fields = ('developer',)
    prepopulated_fields = {'slug': ('developer',)}
    readonly_fields = ('created_at', 'updated_at', 'github_stats_updated', 'github_token_updated')

admin.site.register(DeveloperPublicProfile, DeveloperPublicProfileAdmin)


class CertificationInvitation(models.Model):
    """
    Tracks certification invitations sent by admins to developers.
    Allows superusers to invite developers to start their certification journey.
    """
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('opened', 'Opened'),
        ('started', 'Started'),
        ('expired', 'Expired'),
    ]
    
    developer = models.ForeignKey(TeamMember, on_delete=models.CASCADE, related_name='certification_invitations')
    invited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sent_cert_invitations')
    
    # Optional: specific track/level to recommend
    suggested_track = models.ForeignKey(CertificationTrack, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Personal message from admin
    personal_message = models.TextField(blank=True, help_text="Personal message to include in the invitation email")
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sent')
    
    # Timestamps
    sent_at = models.DateTimeField(auto_now_add=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    
    # Email tracking
    email_sent = models.BooleanField(default=False)
    email_error = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"Invite to {self.developer.first_name} {self.developer.last_name} ({self.status})"


class CertificationInvitationAdmin(admin.ModelAdmin):
    list_display = ('developer', 'invited_by', 'suggested_track', 'status', 'sent_at', 'email_sent')
    list_filter = ('status', 'email_sent', 'suggested_track')
    search_fields = ('developer__first_name', 'developer__last_name', 'developer__email')
    raw_id_fields = ('developer',)
    readonly_fields = ('sent_at', 'opened_at', 'started_at')

admin.site.register(CertificationInvitation, CertificationInvitationAdmin)