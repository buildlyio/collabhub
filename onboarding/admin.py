from .models import *
from django.contrib import admin

from import_export.admin import ImportExportModelAdmin
from import_export import resources

admin.site.register(TeamMember, TeamMemberAdmin)
admin.site.register(Resource, ResourceAdmin)
admin.site.register(TeamMemberResource, TeamMemberResourceAdmin)
admin.site.register(CertificationExam, CertificationExamAdmin)

admin.site.register(Quiz, QuizAdmin)
admin.site.register(QuizQuestion, QuizQuestionAdmin)
admin.site.register(QuizAnswer, QuizAnswerAdmin)

# Register DevelopmentAgency
admin.site.register(DevelopmentAgency, DevelopmentAgencyAdmin)

# Register Customer and Contract
admin.site.register(Customer, CustomerAdmin)
admin.site.register(CustomerDeveloperAssignment, CustomerDeveloperAssignmentAdmin)
admin.site.register(Contract, ContractAdmin)
admin.site.register(CustomerIntakeRequest, CustomerIntakeRequestAdmin)

# Register Phase 1 Portal Models
admin.site.register(CompanyProfile)
admin.site.register(CompanyAdmin)
admin.site.register(Notification)
admin.site.register(LabsAccount)

# Team Training Management
admin.site.register(DeveloperTeam, DeveloperTeamAdmin)
admin.site.register(TeamTraining, TeamTrainingAdmin)
admin.site.register(DeveloperTrainingEnrollment, DeveloperTrainingEnrollmentAdmin)