from datetime import timedelta
from decimal import Decimal
import uuid

from enum import Enum

from django.db import models
from django.contrib import admin
from django.utils import timezone

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

class Hunter(models.Model):
    name = models.CharField(max_length=255, blank=True, help_text="Name your hunt, i.e. The Search for Ops Commander")
    position_title = models.ForeignKey(Position, blank=True, on_delete=models.CASCADE, help_text="Title, (CTO, Front End, Back End etc.)")
    position_pay = models.CharField(max_length=255, blank=True, help_text="Pay Range")
    skills = models.CharField(max_length=255, blank=True, help_text="Top Skills")
    level = models.CharField(max_length=255, blank=True, choices=LEVEL_CHOICES, help_text="Skill level - Select One")
    description = models.TextField(blank=True, help_text="Describe in detail the type of person you are looking for")
    certification = models.TextField(blank=True, help_text="Certifications required if any")
    brief = models.FileField(null=True, blank=True, help_text="Document Upload")
    owner = models.ForeignKey('auth.User',blank=True, null=True, on_delete=models.CASCADE)
    url = models.CharField(max_length=255, null=True, blank=True, help_text="Your GitHub Profile URL")
    linkedin_url = models.CharField(max_length=255, null=True, blank=True, help_text="Your LinkedIn Profile URL")
    status = models.CharField(max_length=255, blank=True, choices=STATUS_CHOICES, help_text="Acitivate the Hunt", default="DRAFT")
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        # onsave add create date or update edit date
        if self.create_date == None:
            self.create_date = timezone.now()
        self.edit_date = timezone.now()
        super(Hunter, self).save(*args, **kwargs)


class HunterAdmin(admin.ModelAdmin):
    list_display = ('name','owner','url','status','create_date','edit_date')
    search_fields = ('name','owner','status')
    list_filter = ('name',)
    display = 'Hunter'


class HunterEntry(models.Model):
    hunter = models.ForeignKey(Hunter, null=False, on_delete=models.CASCADE)
    candidate_name = models.CharField(max_length=255, blank=True)
    candidate_profile = models.CharField(max_length=255, blank=True)
    candidate_certification = models.CharField(max_length=255, blank=True)
    candidate_resume = models.CharField(max_length=255, blank=True)
    candidate_skills = models.CharField(max_length=255, blank=True)
    candidate_level = models.CharField(max_length=255, blank=True)
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
        super(HunterEntry, self).save(*args, **kwargs)


class HunterEntryAdmin(admin.ModelAdmin):
    list_display = ('candidate_name','status','create_date','edit_date')
    search_fields = ('hunter__name','status')
    list_filter = ('hunter__name','status')
    display = 'Montior Site Entries'


class Plan(models.Model):
    hunter = models.ForeignKey(Hunter, null=False, on_delete=models.CASCADE)
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
    list_display = ('hunter','is_paid','plan','create_date','edit_date')
    search_fields = ('hunter__name','is_paid')
    list_filter = ('hunter__name','is_paid')
    display = 'Payment Plans'
