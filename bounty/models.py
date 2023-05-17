from datetime import timedelta
from decimal import Decimal
import uuid
import datetime

from enum import Enum

from django.db import models
from django.contrib import admin
from django.utils import timezone
from django.contrib.auth.models import User

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


class Bounty(models.Model):
    title = models.CharField(max_length=255, blank=True, help_text="Name your bounty, i.e. Fix Registration Error")
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
    repo_owner = models.CharField(max_length=100)
    repo = models.CharField(max_length=100)
    repo_access_token = models.CharField(max_length=100)
    tags = models.CharField(max_length=255, blank=True, help_text="Comma Seperated Tags")
    hosting = models.CharField(max_length=255, blank=True, help_text="Hosting provider if known")
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        # onsave add create date or update edit date
        if self.create_date == None:
            self.create_date = timezone.now()
        self.edit_date = timezone.now()
        super(Bounty, self).save(*args, **kwargs)
    
    def get_num_submissions(self):
        return self.submissions.count()


class BountyAdmin(admin.ModelAdmin):
    list_display = ('title','level','skills','status','create_date','edit_date')
    search_fields = ('title','owner','status')
    list_filter = ('title',)
    display = 'Bounty'


class BountySetter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True) 
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)
    
    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        # onsave add create date or update edit date
        if self.create_date == None:
            self.create_date = timezone.now()
        self.edit_date = timezone.now()
        super(BountySetter, self).save(*args, **kwargs)


class BountySetterAdmin(admin.ModelAdmin):
    list_display = ('full_name','email','create_date','edit_date')
    search_fields = ('full_name','email')
    list_filter = ('full_name','email')
    display = 'Bounty Setters'

class BountyHunter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
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
        super(BountyHunter, self).save(*args, **kwargs)


class BountyHunterAdmin(admin.ModelAdmin):
    list_display = ('full_name','status','create_date','edit_date')
    search_fields = ('full_name','status')
    list_filter = ('full_name','status')
    display = 'Bounty Hunters'


class BountySubmission(models.Model):
    bounty = models.ForeignKey(Bounty, on_delete=models.CASCADE)
    bounty_hunter = models.ForeignKey(User, on_delete=models.CASCADE)
    profile_url = models.URLField(max_length=200)
    notes = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.hunter.username} - {self.bounty.title}'

class Plan(models.Model):
    bounty = models.ForeignKey(Bounty, null=False, on_delete=models.CASCADE)
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
    list_display = ('bounty','is_paid','plan','create_date','edit_date')
    search_fields = ('bounty__name','is_paid')
    list_filter = ('bounty__name','is_paid')
    display = 'Payment Plans'


import requests
import json

from django.db import models

class Issue(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    issue_number = models.CharField(null=True, blank=True, max_length=200)
    issue_url = models.CharField(null=True, blank=True, max_length=500)
    priority = models.IntegerField()
    complexity_estimate = models.IntegerField()
    language = models.CharField(null=True, blank=True, max_length=50)
    framework = models.CharField(null=True, blank=True, max_length=50)
    hosting_environment = models.CharField(null=True, blank=True, max_length=100)
    screenshot = models.ImageField(null=True, blank=True, upload_to='bug_screenshots')
    tags = models.CharField(null=True, blank=True, max_length=100)
    is_fixed = models.BooleanField(default=False)
    bounty = models.ForeignKey(Bounty, on_delete=models.CASCADE)
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

    def __str__(self):
        return self.title

class IssueAdmin(admin.ModelAdmin):
    list_display = ('title','priority')
    search_fields = ('bounty__title','title')
    list_filter = ('bounty__title','title')
    display = 'Issues'
    

from django.core.validators import MinValueValidator, MaxValueValidator


class AcceptedBounty(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accepted_bounties_owned')
    bounty_hunter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accepted_bounties_hunted')
    bounty = models.ForeignKey(Bounty, on_delete=models.CASCADE)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.bounty} - {self.owner.username} - {self.bounty_hunter.username}"


class Contract(models.Model):
    bounty = models.ForeignKey(Bounty, on_delete=models.CASCADE)
    accepted_bounty = models.ForeignKey(AcceptedBounty, on_delete=models.CASCADE)
    owner_signature = models.ImageField(upload_to='contracts', null=True, blank=True)
    bounty_hunter_signature = models.ImageField(upload_to='contracts', null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(validators=[MinValueValidator(limit_value=models.F('start_date') + datetime.timedelta(days=30)),
                                            MaxValueValidator(limit_value=models.F('start_date') + datetime.timedelta(days=365))])

    def __str__(self):
        return f"{self.bounty} - {self.accepted_bounty.owner.username} - {self.accepted_bounty.bounty_hunter.username}"
