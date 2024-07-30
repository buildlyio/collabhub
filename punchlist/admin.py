from .models import *
from django.contrib import admin

admin.site.register(Punchlist, PunchlistAdmin)
admin.site.register(PunchlistHunter, PunchlistHunterAdmin)
admin.site.register(PunchlistSetter, PunchlistSetterAdmin)
admin.site.register(Issue, IssueAdmin)
admin.site.register(Bug, BugAdmin)
admin.site.register(DevelopmentAgency, DevelopmentAgencyAdmin)
admin.site.register(InsightsUser, InsightsUserAdmin)