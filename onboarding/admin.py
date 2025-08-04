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