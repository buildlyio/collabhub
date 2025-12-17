from django.urls import path
from . import views

app_name = 'onboarding'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('upload_resource/', views.upload_resource, name='upload_resource'),
    path('resources/', views.resource_list, name='resource_list'),
    path('resources/create/', views.resource_create, name='resource_create'),
    path('resources/<int:resource_id>/edit/', views.resource_edit, name='resource_edit'),
    path('resources/<int:resource_id>/delete/', views.resource_delete, name='resource_delete'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('quizzes/', views.quiz_list, name='quiz_list'),
    path('quiz/<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('quiz/<int:quiz_id>/submit/', views.submit_answers, name='submit_answers'),
    
    # Agency URLs
    path('agency_add/', views.DevelopmentAgencyCreateView.as_view(), name='agency_add'),
    path('agencies/', views.showcase_agencies, name='agency_list'),
    path('agency/login/', views.agency_login, name='agency_login'),
    path('agency/register/', views.agency_register, name='agency_register'),
    path('agency/dashboard/', views.agency_dashboard, name='agency_dashboard'),
    path('agency/edit-profile/', views.agency_edit_profile, name='agency_edit_profile'),
    path('agency/logout/', views.agency_logout, name='agency_logout'),
    
    # Assessment URLs
    path('assessment/', views.assessment_landing, name='assessment_landing'),
    path('assessment/quiz/', views.take_assessment, name='take_assessment'),
    path('assessment/complete/', views.assessment_complete, name='assessment_complete'),
    
    # Admin URLs (Assessment Dashboard)
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-assessments/', views.admin_assessment_reports, name='admin_assessment_reports'),
    
    # Admin URLs (Customer Management Dashboard)
    path('admin-customers-dashboard/', views.admin_customer_dashboard, name='admin_customer_dashboard'),
    path('admin-assessment/<int:team_member_id>/review/', views.admin_assessment_review, name='admin_assessment_review'),
    path('admin-quizzes/', views.admin_quiz_list, name='admin_quiz_list'),
    path('admin-quiz/create/', views.admin_quiz_create, name='admin_quiz_create'),
    path('admin-quiz/<int:quiz_id>/edit/', views.admin_quiz_edit, name='admin_quiz_edit'),
    path('admin-quiz/<int:quiz_id>/delete/', views.admin_quiz_delete, name='admin_quiz_delete'),
    path('admin-quiz/<int:quiz_id>/questions/', views.admin_quiz_questions, name='admin_quiz_questions'),
    path('admin-quiz/<int:quiz_id>/question/add/', views.admin_question_create, name='admin_question_create'),
    path('admin-question/<int:question_id>/edit/', views.admin_question_edit, name='admin_question_edit'),
    path('admin-question/<int:question_id>/delete/', views.admin_question_delete, name='admin_question_delete'),
    
    # Customer Portal URLs
    path('client/login/', views.customer_login, name='customer_login'),
    path('client/logout/', views.customer_logout, name='customer_logout'),
    path('client/dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('client/developer/<int:developer_id>/', views.customer_developer_detail, name='customer_developer_detail'),
    path('client/contract/<int:contract_id>/', views.customer_contract_view, name='customer_contract_view'),
    path('client/contract/<int:contract_id>/sign/', views.customer_contract_sign, name='customer_contract_sign'),
    
    # Shareable Token-Based URLs
    path('client/shared/<str:token>/', views.customer_shared_view, name='customer_shared_view'),
    path('client/shared/<str:token>/developer/<int:developer_id>/', views.customer_shared_developer_detail, name='customer_shared_developer_detail'),
    path('client/shared/<str:token>/developer/<int:developer_id>/approve/', views.customer_shared_approve_developer, name='customer_shared_approve_developer'),
    path('client/shared/<str:token>/developer/<int:developer_id>/reject/', views.customer_shared_reject_developer, name='customer_shared_reject_developer'),
    path('client/shared/<str:token>/contract/<int:contract_id>/sign/', views.customer_shared_contract_sign, name='customer_shared_contract_sign'),
    
    # Custom Admin Dashboard URLs (Staff Only)
    path('admin/customers/', views.admin_customers_list, name='admin_customers_list'),
    path('admin/customers/new/', views.admin_customer_create, name='admin_customer_create'),
    path('admin/customers/<int:customer_id>/', views.admin_customer_detail, name='admin_customer_detail'),
    path('admin/customers/<int:customer_id>/delete/', views.admin_customer_delete, name='admin_customer_delete'),
    path('admin/developers/', views.admin_developers_list, name='admin_developers_list'),
    path('admin/developers/<int:developer_id>/', views.admin_developer_profile, name='admin_developer_profile'),
    path('admin/developers/<int:developer_id>/sync-github/', views.sync_github_skills, name='sync_github_skills'),
]

