from .models import *
from django.contrib import admin

from import_export.admin import ImportExportModelAdmin
from import_export import resources

admin.site.register(Submission, SubmissionAdmin)
admin.site.register(SubmissionLink, SubmissionLinkAdmin)
