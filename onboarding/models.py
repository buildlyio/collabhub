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

class TeamMember(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    team_member_type = models.CharField(max_length=50, choices=TEAM_MEMBER_TYPES)
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

    def __str__(self):
        return f'{self.first_name} {self.last_name} - {self.team_member_type}'


class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'team_member_type', 'approved', 'user')
    list_filter = ('approved', 'team_member_type')
    search_fields = ('first_name', 'last_name', 'email', 'user__username')
    list_editable = ('approved',)
    actions = ['approve_users', 'unapprove_users']
    display = 'Team Member Admin'
    
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
    list_display = ('title','team_member_type')
    display = 'Resource Admin'  


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

    def __str__(self):
        return f'Answer by {self.team_member} to {self.question}'

class QuizAnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'team_member', 'answer')
    search_fields = ('team_member__first_name', 'team_member__last_name')


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
    
    def __str__(self):
        return self.agency_name


class DevelopmentAgencyAdmin(admin.ModelAdmin):
    list_display = ('agency_name','contact_email', 'agency_type')
    search_fields = ('agency_name','contact_email')
    list_filter = ('agency_type', 'industries_worked')
    display = 'Development Agencies'
