from django.urls import path
from . import views

app_name = 'onboarding'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('upload_resource/', views.upload_resource, name='upload_resource'),
    path('resources/', views.resource_list, name='resource_list'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('quizzes/', views.quiz_list, name='quiz_list'),
    path('quiz/<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('quiz/<int:quiz_id>/submit/', views.submit_answers, name='submit_answers'),
    
    # Agency URLs
    path('agency_add/', views.DevelopmentAgencyCreateView.as_view(), name='agency_add'),
    path('agencies/', views.showcase_agencies, name='agency_list'),
    
    # Assessment URLs
    path('assessment/', views.assessment_landing, name='assessment_landing'),
    path('assessment/quiz/', views.take_assessment, name='take_assessment'),
    path('assessment/complete/', views.assessment_complete, name='assessment_complete'),
]

