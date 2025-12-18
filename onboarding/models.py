# onboarding/models.py

from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin

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


class TeamMember(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    team_member_type = models.CharField(max_length=50, choices=TEAM_MEMBER_TYPES)  # Keep for backward compatibility
    profile_types = models.ManyToManyField(TeamMemberType, blank=True, related_name='team_members', help_text="Multiple profile types")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    bio = models.TextField(blank=True)
    linkedin = models.URLField(blank=True)
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
            'fields': ('bio', 'linkedin', 'experience_years', 'github_account', 'google_account_link', 'google_calendar_embed_code')
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
    readonly_fields = ('submitted_at', 'ai_detection_score', 'ai_detection_analysis')
    
    fieldsets = (
        ('Answer Details', {
            'fields': ('question', 'team_member', 'answer', 'submitted_at')
        }),
        ('AI Detection', {
            'fields': ('ai_detection_score', 'ai_detection_analysis'),
            'classes': ('collapse',)
        }),
        ('Human Evaluation', {
            'fields': ('evaluator_score', 'evaluator_notes', 'evaluated_by', 'evaluated_at')
        }),
    )
    
    def answer_preview(self, obj):
        return obj.answer[:100] + '...' if len(obj.answer) > 100 else obj.answer
    answer_preview.short_description = 'Answer Preview'
    
    actions = ['run_ai_detection']
    
    def run_ai_detection(self, request, queryset):
        """Run AI detection on selected essay answers"""
        from .ai_detection import detect_ai_usage
        
        essay_answers = queryset.filter(question__question_type='essay')
        if not essay_answers:
            self.message_user(request, "No essay answers selected. AI detection only works on essay questions.", level='WARNING')
            return
        
        detected_count = 0
        for answer in essay_answers:
            try:
                score, analysis = detect_ai_usage(answer.answer)
                answer.ai_detection_score = score
                answer.ai_detection_analysis = analysis
                answer.save(update_fields=['ai_detection_score', 'ai_detection_analysis'])
                detected_count += 1
            except Exception as e:
                self.message_user(request, f"Error detecting AI for answer {answer.id}: {str(e)}", level='ERROR')
        
        self.message_user(request, f"AI detection completed for {detected_count} answers.")
    run_ai_detection.short_description = "Run AI detection on essay answers"


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
    
    name = models.CharField(max_length=255, help_text="e.g., Frontend React Specialist, Python Backend Expert")
    level_type = models.CharField(max_length=20, choices=LEVEL_TYPES, default='intermediate')
    description = models.TextField(help_text="What this certification demonstrates")
    requirements = models.TextField(help_text="Skills and experience required", blank=True)
    
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