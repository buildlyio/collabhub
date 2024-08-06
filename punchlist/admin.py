from .models import *
from django.contrib import admin

from import_export.admin import ImportExportModelAdmin
from import_export import resources

class DevelopmentAgencyResource(resources.ModelResource):

    class Meta:
        model = DevelopmentAgency

class DevelopmentAgencyAdmin(ImportExportModelAdmin):
    resource_classes = [DevelopmentAgencyResource]


admin.site.register(Punchlist, PunchlistAdmin)
admin.site.register(PunchlistHunter, PunchlistHunterAdmin)
admin.site.register(PunchlistSetter, PunchlistSetterAdmin)
admin.site.register(Issue, IssueAdmin)
admin.site.register(Bug, BugAdmin)
admin.site.register(DevelopmentAgency, DevelopmentAgencyAdmin)
admin.site.register(InsightsUser, InsightsUserAdmin)