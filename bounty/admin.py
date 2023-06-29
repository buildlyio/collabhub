from .models import *
from django.contrib import admin

admin.site.register(Bounty, BountyAdmin)
admin.site.register(BountyHunter, BountyHunterAdmin)
admin.site.register(BountySetter, BountySetterAdmin)
admin.site.register(Issue, IssueAdmin)
admin.site.register(Bug, BugAdmin)
admin.site.register(DevelopmentAgency, DevelopmentAgencyAdmin)
