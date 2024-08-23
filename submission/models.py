from datetime import timedelta
from decimal import Decimal
import uuid
import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from django.contrib import admin
from django.utils import timezone

class SubmissionLink(models.Model):
    admin_user = models.ForeignKey(User, on_delete=models.CASCADE)
    unique_url = models.URLField(max_length=255, unique=True)
    qr_code = models.CharField(max_length=1000, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)
    

    def save(self, *args, **kwargs):
        # onsave add create date or update edit date
        if self.create_date == None:
            self.create_date = timezone.now()
        self.edit_date = timezone.now()
        if not self.unique_url:
            self.unique_url = get_random_string(32)  # Generates a random URL string
        super().save(*args, **kwargs)


class SubmissionLinkAdmin(admin.ModelAdmin):
    list_display = ('admin_user','unique_url','create_date','edit_date')
    display = 'Submission Link Admin'  

class Submission(models.Model):
    submission_link = models.ForeignKey(SubmissionLink, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    description = models.TextField()
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        # onsave add create date or update edit date
        if self.create_date == None:
            self.create_date = timezone.now()
        self.edit_date = timezone.now()
        super(Submission, self).save(*args, **kwargs)
    

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('submission_link','name','email','create_date','edit_date')
    display = 'Submission Admin'  