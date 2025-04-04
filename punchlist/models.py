from datetime import timedelta
from decimal import Decimal
import uuid
import datetime

from enum import Enum

from django.db import models
from django.contrib import admin
from django.utils import timezone
from django.contrib.auth.models import User

from .util import evaluate_product_idea



class Level(Enum):
    INTERN = 'Intern'
    JUNIOR = 'Junior'
    MIDLEVEL = 'Midlevel'
    SENIOR = 'Senior'
    CTO = 'CTO'

LEVEL_CHOICES = (
    (Level.INTERN.value, 'Intern'),
    (Level.JUNIOR.value, 'Junior'),
    (Level.MIDLEVEL.value, 'Mid-Level'),
    (Level.SENIOR.value, 'Senior'),
    (Level.CTO.value, 'CTO'),
)

class Complexity(Enum):
    LOW = 'Low'
    MEDIUM = 'Medium'
    HIGH = 'High'
    EXTREME = 'Extreme'

COMPLEXITY_CHOICES = (
    (Complexity.LOW.value, 'Low'),
    (Complexity.MEDIUM.value, 'Medium'),
    (Complexity.HIGH.value, 'High'),
    (Complexity.EXTREME.value, 'Extreme'),
)

class Status(Enum):
    DRAFT = 'Draft'
    PLANNED = 'Planned'
    STARTED = 'Started'
    FOUND = 'Found'
    CANCELED = 'CANCELED'

STATUS_CHOICES = (
    (Status.DRAFT.value, 'Draft'),
    (Status.PLANNED.value, 'Planned'),
    (Status.STARTED.value, 'Started'),
    (Status.FOUND.value, 'Found'),
    (Status.CANCELED.value, 'CANCELED'),
)

class AMOUNT(Enum):
    SMALL = 'Small'
    MEDIUM = 'Medium'
    LARGE = 'Large'
    XL = 'XL'
    XXL = 'XXL'

AMOUNT_CHOICES = (
    (AMOUNT.SMALL.value, '$25'),
    (AMOUNT.MEDIUM.value, '$40'),
    (AMOUNT.LARGE.value, '$75'),
    (AMOUNT.XL.value, '$100'),
    (AMOUNT.XXL.value, '$200'),
)

class Product(models.Model):
    name = models.CharField(max_length=255,null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    product_info = models.TextField(null=True, blank=True)
    dev_url = models.CharField(max_length=255,null=True, blank=True)
    prod_url = models.CharField(max_length=255,null=True, blank=True)
    repository_url = models.CharField(max_length=255,null=True, blank=True)
    product_uuid = models.UUIDField(unique=True,null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    organization_uuid = models.UUIDField(null=True, blank=True)  # Add this field for organization UUID
    product_team = models.UUIDField(null=True, blank=True)  # Add this field for product team UUID
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=255, blank=True, choices=STATUS_CHOICES, help_text="Status of your Product", default="DRAFT")
    
    # Evaluation fields
    originality_score = models.TextField(null=True, blank=True)
    marketability_score = models.TextField(null=True, blank=True)
    feasibility_score = models.TextField(null=True, blank=True)
    completeness_score = models.TextField(null=True, blank=True)
    summary = models.TextField(blank=True, null=True)
    gemini_completeness_score = models.TextField(null=True, blank=True)
    gemini_originality_score = models.TextField(null=True, blank=True)
    gemini_marketability_score = models.TextField(null=True, blank=True)
    gemini_feasibility_score = models.TextField(null=True, blank=True)
    gemini_summary = models.TextField(blank=True, null=True)

    # Override the save method to include evaluation logic
    def save(self, *args, **kwargs):
        # Convert the instance to a dictionary suitable for analysis
        application_data = {
            'name': self.name,
            'description': self.description,
            'product_info': self.product_info,
            # Include other relevant fields as needed
        }

        # Assume `analyze_ai_response` is imported and ready to use
        # and it now accepts a dictionary and returns a dictionary with scores and summary
        evaluation_results = evaluate_product_idea(application_data)
        # review_text, originality_score, marketability_score, feasibility_score, completeness_score
        # Update the instance with evaluation results
        self.summary = evaluation_results[0]
        self.originality_score = evaluation_results[1]
        self.marketability_score = evaluation_results[2]
        self.feasibility_score = evaluation_results[3]
        self.completeness_score = evaluation_results[4]
        self.gemini_summary = evaluation_results[5]
        self.gemini_originality_score = evaluation_results[6]
        self.gemini_marketability_score = evaluation_results[7]
        self.gemini_feasibility_score = evaluation_results[8]
        self.gemini_completeness_score = evaluation_results[9]

        super().save(*args, **kwargs)  # Call the "real" save() method.

    def __str__(self):
        return self.name

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name','product_uuid')
    search_fields = ('name','product_uuid')
    list_filter = ('name','product_uuid')
    display = 'Products'

class Position(models.Model):
    name = models.CharField(max_length=255, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # onsave add create date or update edit date
        if self.create_date == None:
            self.create_date = timezone.now()
        self.edit_date = timezone.now()
        super(Position, self).save(*args, **kwargs)


class PositionAdmin(admin.ModelAdmin):
    list_display = ('name','create_date','edit_date')
    search_fields = ('name',)
    list_filter = ('name',)
    display = 'Positions'


class Bug(models.Model):
    SEVERITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]

    url = models.URLField()
    notes = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    title = models.CharField(blank=True, max_length=255)
    app_name = models.CharField(blank=True, max_length=255)
    version = models.CharField( blank=True, max_length=255)
    name = models.CharField(blank=True, max_length=255)
    email = models.EmailField( blank=True)
    description = models.TextField(blank=True)
    expected_behaviour = models.TextField(blank=True)
    steps_to_reproduce = models.TextField(blank=True)
    screenshots = models.ImageField(upload_to='bug_screenshots', blank=True)
    is_user_submitted = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    is_tracked = models.BooleanField(default=False)
    tracked_url = models.URLField(blank=True)
    punchlist = models.ForeignKey("Punchlist", blank=True, on_delete=models.CASCADE, related_name="bug_punchlist", null=True)

    def __str__(self):
        return self.url


class BugAdmin(admin.ModelAdmin):
    list_display = ('url','name')
    search_fields = ('url','name')
    list_filter = ('url','name')
    display = 'User Submitted Bugs'

class Punchlist(models.Model):
    CATAGORY_CHOICES = (
        ('Bug', 'Bug'),
        ('Feature', 'Feature'),
        ('Puchlist', 'Punchlist'),
        ('Release', 'Release'),
    )
    title = models.CharField(max_length=255, blank=True, help_text="Name your punchlist, i.e. Fix Registration Error")
    catagory = models.CharField(choices=CATAGORY_CHOICES, max_length=255, blank=True, help_text="If it is new or it works but you want to change it somehow it's a feature, otherwise it's a bug.  A Punchlist is a list of bug in a release, and a release is collection of bugs and features")
    is_public = models.BooleanField(default=False, help_text="Make this public for anyone to work on")
    skills = models.CharField(max_length=255, blank=True, help_text="Skills Required to Fix your Issue")
    level = models.CharField(max_length=255, blank=True, choices=LEVEL_CHOICES, help_text="Skill level - Select One")
    description = models.TextField(blank=True, help_text="Describe in detail the issue of person you are looking for")
    certification = models.TextField(blank=True, help_text="Certifications required if any")
    brief = models.FileField(null=True, blank=True, help_text="Document Upload")
    amount = models.CharField(max_length=255, blank=True, choices=AMOUNT_CHOICES, help_text="How Much in USD to get the work done.")
    owner = models.ForeignKey('auth.User',blank=True, null=True, on_delete=models.CASCADE)
    issue_id = models.CharField(max_length=255, blank=True, null=True, help_text="GitHub ID")
    complexity_estimate = models.CharField(max_length=255, blank=True, null=True, choices=COMPLEXITY_CHOICES, help_text="Difficult or Easy or not sure")
    url = models.CharField(max_length=255, null=True, blank=True, help_text="Your GitHub Repository URL")
    status = models.CharField(max_length=255, blank=True, choices=STATUS_CHOICES, help_text="Acitivate the Hunt", default="DRAFT")
    repo_owner = models.CharField(max_length=100, help_text="Github Organization Name")
    repo = models.CharField(max_length=100, help_text="GitHub Repository i.e. myorg/myrepo")
    repo_access_token = models.CharField(max_length=100,help_text="Learn how to get your GitHub Token here https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens")
    tags = models.CharField(max_length=255, blank=True, help_text="Comma Seperated Tags")
    hosting = models.CharField(max_length=255, blank=True, help_text="Hosting provider if known")
    labs_organization_uuid = models.UUIDField(unique=True, default=uuid.uuid4, help_text="Organization UUID from Buildly Insights API")
    labs_product_name = models.CharField(max_length=255, blank=True, null=True, help_text="Product Name from Buildly Insights API")
    labs_product_id = models.CharField(max_length=255, blank=True, null=True, help_text="Product ID from Buildly Insights API")
    labs_release_id = models.JSONField(max_length=255, blank=True, null=True, help_text="Release IDs from Buildly Insights API for Product") 
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='punchlists', null=True, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        # onsave add create date or update edit date
        if self.create_date == None:
            self.create_date = timezone.now()
        self.edit_date = timezone.now()
        super(Punchlist, self).save(*args, **kwargs)
    
    def get_num_submissions(self):
        return self.submissions.count()


class PunchlistAdmin(admin.ModelAdmin):
    list_display = ('title','level','skills','status','create_date','edit_date')
    search_fields = ('title','owner','status')
    list_filter = ('title',)
    display = 'Punchlist'


class PunchlistSetter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)
    
    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        # onsave add create date or update edit date
        if self.create_date == None:
            self.create_date = timezone.now()
        self.edit_date = timezone.now()
        super(PunchlistSetter, self).save(*args, **kwargs)


class PunchlistSetterAdmin(admin.ModelAdmin):
    list_display = ('user','create_date','edit_date')
    display = 'Punchlist Setters'  
    

class PunchlistHunter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    agency = models.ForeignKey('DevelopmentAgency', on_delete=models.CASCADE, blank=True, null=True) # Add this field for Development Agency
    approved = models.BooleanField(default=False)
    github_profile = models.URLField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=255, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        # onsave add create date or update edit date
        if self.create_date == None:
            self.create_date = timezone.now()
        self.edit_date = timezone.now()
        super(PunchlistHunter, self).save(*args, **kwargs)


class PunchlistHunterAdmin(admin.ModelAdmin):
    list_display = ('github_profile','status','create_date','edit_date')
    search_fields = ('github_profile','status')
    list_filter = ('github_profile','status')
    display = 'Punchlist Hunters'
    
    def email(self, obj):
        return obj.user.email
    email.short_description = 'Email'

    def username(self, obj):
        return obj.user.username
    username.short_description = 'Username'


class PunchlistSubmission(models.Model):
    punchlist = models.ForeignKey(Punchlist, on_delete=models.CASCADE)
    punchlist_hunter = models.ForeignKey(User, on_delete=models.CASCADE)
    profile_url = models.URLField(max_length=200)
    notes = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.punchlist.title}'

class Plan(models.Model):
    punchlist = models.ForeignKey(Punchlist, null=False, on_delete=models.CASCADE)
    is_paid = models.BooleanField(default=False)
    plan = models.CharField(max_length=255, blank=True)
    expriation_date = models.DateTimeField(null=True, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        # onsave add create date or update edit date
        if self.create_date == None:
            self.create_date = timezone.now()
        self.edit_date = timezone.now()
        super(Plan, self).save(*args, **kwargs)


class PlanAdmin(admin.ModelAdmin):
    list_display = ('punchlist','is_paid','plan','create_date','edit_date')
    search_fields = ('punchlist__name','is_paid')
    list_filter = ('punchlist__name','is_paid')
    display = 'Payment Plans'



class Issue(models.Model):
    title = models.CharField(default="None", max_length=200)
    description = models.TextField(default="None")
    issue_number = models.CharField(null=True, blank=True, max_length=200)
    issue_url = models.CharField(null=True, blank=True, max_length=500)
    priority = models.IntegerField(default=1)
    complexity_estimate = models.IntegerField(default=1)
    language = models.CharField(null=True, blank=True, max_length=50)
    framework = models.CharField(null=True, blank=True, max_length=50)
    hosting_environment = models.CharField(null=True, blank=True, max_length=100)
    screenshot = models.ImageField(null=True, blank=True, upload_to='bug_screenshots')
    tags = models.CharField(null=True, blank=True, max_length=100)
    is_fixed = models.BooleanField(default=False)
    is_tracked = models.BooleanField(default=False)
    tracked_url = models.URLField(blank=True)
    punchlist = models.ForeignKey(Punchlist, on_delete=models.CASCADE)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        # onsave add create date or update edit date
        if self.create_date == None:
            self.create_date = timezone.now()
        self.edit_date = timezone.now()
        super(Issue, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

class IssueAdmin(admin.ModelAdmin):
    list_display = ('title','priority')
    search_fields = ('punchlist__title','title')
    list_filter = ('punchlist__title','title')
    display = 'Issues'
    

from django.core.validators import MinValueValidator, MaxValueValidator


class AcceptedPunchlist(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accepted_bounties_owned')
    punchlist_hunter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accepted_bounties_hunted')
    punchlist = models.ForeignKey(Punchlist, on_delete=models.CASCADE)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.punchlist} - {self.owner.username} - {self.punchlist_hunter.username}"


class Contract(models.Model):
    punchlist = models.ForeignKey(Punchlist, on_delete=models.CASCADE)
    accepted_punchlist = models.ForeignKey(AcceptedPunchlist, on_delete=models.CASCADE)
    owner_signature = models.ImageField(upload_to='contracts', null=True, blank=True)
    punchlist_hunter_signature = models.ImageField(upload_to='contracts', null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(validators=[MinValueValidator(limit_value=models.F('start_date') + datetime.timedelta(days=30)),
                                            MaxValueValidator(limit_value=models.F('start_date') + datetime.timedelta(days=365))])

    def __str__(self):
        return f"{self.punchlist} - {self.accepted_punchlist.owner.username} - {self.accepted_punchlist.punchlist_hunter.username}"


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
        # Add more industry choices as needed
    ]

    agency_name = models.CharField(max_length=255, unique=True)
    agency_type = models.CharField(max_length=255, choices=AGENCY_TYPE,null=True, blank=True)
    certified = models.BooleanField(default=False)
    team_size = models.PositiveIntegerField(help_text="How many employees in your organization")
    skills = models.TextField(null=True, blank=True, help_text="If your a service, list the skills your team uses to complete the service")
    background = models.TextField(help_text="How long have you been in business, where are you based details to help startups know who you are.")
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2)
    project_rate = models.DecimalField(max_digits=10, decimal_places=2)
    industries_worked = models.CharField(max_length=255, choices=INDUSTRY_CHOICES, help_text="Primary Industries you serve or have worked with")
    github_repository = models.URLField(null=True, blank=True)
    client_reviews = models.TextField(max_length=255, null=True, blank=True,help_text="Profile Links to Clutch, Capterra, G2 Crowd, and GoodFirms: Links to the company's profiles on these review platforms.")
    contact_name = models.CharField(max_length=255)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    linkedin_url = models.URLField(null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    how_they_found_us = models.TextField()
    logo = models.ImageField(upload_to='agency-logo', null=True, blank=True)

    def __str__(self):
        return self.agency_name

class DevelopmentAgencyAdmin(admin.ModelAdmin):
    list_display = ('agency_name','contact_email')
    search_fields = ('agency_name','contact_email')
    list_filter = ('agency_name','contact_email')
    display = 'Agencies'
    

class InsightsUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Assuming you have a User model
    insightsuser_id = models.CharField(null=True, blank=True,max_length=255,unique=True)
    insightsorganization_id = models.CharField(null=True, blank=True,max_length=255, unique=True)  # Store organization ID for authentication sharing

    def __str__(self):
        return self.user.username


class InsightsUserAdmin(admin.ModelAdmin):
    list_display = ('user','insightsorganization_id')
    search_fields = ('user','insightsorganization_id')
    list_filter = ('user','insightsorganization_id')
    display = 'Insights User'


class AgencyReview(models.Model):
    agency = models.ForeignKey(DevelopmentAgency, on_delete=models.CASCADE)
    platform = models.CharField(max_length=100)  # e.g., Google, Yelp, etc.
    platfrom_url = models.URLField(blank=True, null=True)  # Link to platform profile
    rating = models.FloatField()
    review_text = models.TextField(blank=True, null=True)
    review_link = models.URLField(blank=True, null=True)  # Link to review page
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.agency.name} - {self.platform}: {self.rating}"

class AgencyReviewAdmin(admin.ModelAdmin):
    list_display = ('agency','platform','rating','timestamp')
    search_fields = ('agency','platform','rating')
    list_filter = ('agency','platform','rating')
    display = 'Agency Reviews'

class AgencyAggregate(models.Model):
    agency = models.OneToOneField(DevelopmentAgency, on_delete=models.CASCADE)
    average_rating = models.FloatField()
    review_count = models.IntegerField()
    last_checked = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.agency.name}: {self.average_rating} ({self.review_count} reviews)"
    
class AgencyAggregateAdmin(admin.ModelAdmin):
    list_display = ('agency','average_rating','review_count','last_checked')
    search_fields = ('agency','average_rating','review_count')
    list_filter = ('agency','average_rating','review_count')
    display = 'Agency Aggregates'

