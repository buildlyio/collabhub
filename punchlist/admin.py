from .models import *
from django.contrib import admin

from import_export.admin import ImportExportModelAdmin
from import_export import resources


admin.site.register(Punchlist, PunchlistAdmin)
admin.site.register(PunchlistHunter, PunchlistHunterAdmin)
admin.site.register(PunchlistSetter, PunchlistSetterAdmin)
admin.site.register(Issue, IssueAdmin)
admin.site.register(Bug, BugAdmin)
admin.site.register(DevelopmentAgency, DevelopmentAgencyAdmin)
admin.site.register(InsightsUser, InsightsUserAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(AgencyReview, AgencyReviewAdmin)    
admin.site.register(AgencyAggregate, AgencyAggregateAdmin)  