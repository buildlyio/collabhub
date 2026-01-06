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
    path('client/shared/<str:token>/training/<int:training_id>/', views.customer_shared_training_preview, name='customer_shared_training_preview'),
    path('client/shared/<str:token>/quiz/<int:quiz_id>/', views.customer_shared_quiz_preview, name='customer_shared_quiz_preview'),
    
    # Custom Admin Dashboard URLs (Staff Only)
    path('admin/customers/', views.admin_customers_list, name='admin_customers_list'),
    path('admin/customers/new/', views.admin_customer_create, name='admin_customer_create'),
    path('admin/customers/<int:customer_id>/', views.admin_customer_detail, name='admin_customer_detail'),
    path('admin/customers/<int:customer_id>/delete/', views.admin_customer_delete, name='admin_customer_delete'),
    path('admin/customers/<int:customer_id>/contracts/new/', views.admin_contract_create, name='admin_contract_create'),
    path('admin/intake-requests/', views.admin_intake_requests, name='admin_intake_requests'),
    path('admin/intake-requests/<int:intake_id>/', views.admin_intake_request_detail, name='admin_intake_request_detail'),
    path('admin/contracts/<int:contract_id>/edit/', views.admin_contract_edit, name='admin_contract_edit'),
    path('admin/contracts/<int:contract_id>/delete/', views.admin_contract_delete, name='admin_contract_delete'),
    path('admin/developers/', views.admin_developers_list, name='admin_developers_list'),
    path('admin/developers/<int:developer_id>/', views.admin_developer_profile, name='admin_developer_profile'),
    path('admin/developers/<int:developer_id>/sync-github/', views.sync_github_skills, name='sync_github_skills'),
    
    # ==================== PHASE 1: CUSTOMER PORTAL URLs ====================
    
    # Labs Authentication
    path('labs/login/', views.labs_login, name='labs_login'),
    path('labs/callback/', views.labs_callback, name='labs_callback'),
    path('labs/unlink/', views.labs_unlink, name='labs_unlink'),
    
    # Approval Workflows
    path('admin/approval-queue/', views.admin_approval_queue, name='admin_approval_queue'),
    path('admin/approve-community/<int:developer_id>/', views.admin_approve_community, name='admin_approve_community'),
    path('portal/dashboard/', views.customer_portal_dashboard, name='customer_portal_dashboard'),
    path('portal/', views.customer_portal_switcher, name='customer_portal_switcher'),
    path('portal/approve-developer/<int:assignment_id>/', views.customer_approve_developer, name='customer_approve_developer'),
    path('portal/request-removal/<int:assignment_id>/', views.request_developer_removal, name='request_developer_removal'),
    
    # Contract Signing
    path('contract/<int:contract_id>/sign/', views.contract_sign_form, name='contract_sign_form'),
    path('contract/<int:contract_id>/sign/submit/', views.contract_sign_submit, name='contract_sign_submit'),
    path('contract/<int:contract_id>/download/', views.contract_pdf_download, name='contract_pdf_download'),
    
    # Certificates
    path('certificates/', views.developer_certificates, name='developer_certificates'),
    path('certificate/<int:cert_id>/download/', views.certificate_download, name='certificate_download'),
    path('admin/certifications/', views.admin_certification_levels, name='admin_certification_levels'),
    path('admin/certification/create/', views.admin_certification_create, name='admin_certification_create'),
    path('admin/developer/<int:developer_id>/certify/', views.admin_issue_certificate, name='admin_issue_certificate'),
    
    # Verification (Public)
    path('verify/', views.verification_home, name='verification_home'),
    path('verify/contract/<str:contract_hash>/', views.verify_contract, name='verify_contract'),
    path('verify/certificate/<str:certificate_hash>/', views.verify_certificate, name='verify_certificate'),
    
    # Notifications
    path('notifications/', views.notification_center, name='notification_center'),
    path('notifications/<int:notification_id>/read/', views.notification_mark_read, name='notification_mark_read'),
    path('api/notifications/unread-count/', views.notification_unread_count, name='notification_unread_count'),

    # Developer Teams & Trainings
    path('teams/', views.developer_teams, name='developer_teams'),
    path('teams/resource/<int:resource_id>/complete/', views.mark_resource_complete, name='mark_resource_complete'),

    # Admin: Training Management
    path('admin/trainings/', views.admin_training_list, name='admin_training_list'),
    path('admin/trainings/create/', views.admin_training_create, name='admin_training_create'),
    path('admin/trainings/<int:training_id>/', views.admin_training_detail, name='admin_training_detail'),
    path('admin/trainings/<int:training_id>/edit/', views.admin_training_edit, name='admin_training_edit'),
    path('admin/trainings/<int:training_id>/enroll/', views.admin_training_enroll, name='admin_training_enroll'),
    path('admin/trainings/<int:training_id>/assign-team/', views.admin_training_assign_team, name='admin_training_assign_team'),
    
    # Admin: Developer Team Management
    path('admin/developer-teams/', views.admin_team_list, name='admin_team_list'),
    path('admin/developer-teams/create/', views.admin_team_create, name='admin_team_create'),
    path('admin/developer-teams/<int:team_id>/', views.admin_team_detail, name='admin_team_detail'),
    path('admin/developer-teams/<int:team_id>/edit/', views.admin_team_edit, name='admin_team_edit'),
    path('admin/developer-teams/<int:team_id>/add-member/', views.admin_team_add_member, name='admin_team_add_member'),
    path('admin/developer-teams/<int:team_id>/remove-member/<int:member_id>/', views.admin_team_remove_member, name='admin_team_remove_member'),
    
    # Developer: Project Submissions
    path('training/<int:training_id>/projects/', views.developer_project_list, name='developer_project_list'),
    path('project/<int:project_id>/submit/', views.developer_project_submit, name='developer_project_submit'),
    
    # Admin: Project Management
    path('admin/trainings/<int:training_id>/projects/', views.admin_project_list, name='admin_project_list'),
    path('admin/trainings/<int:training_id>/projects/create/', views.admin_project_create, name='admin_project_create'),
    path('admin/projects/<int:project_id>/edit/', views.admin_project_edit, name='admin_project_edit'),
    path('admin/projects/<int:project_id>/delete/', views.admin_project_delete, name='admin_project_delete'),
    
    # Admin: Submission Review
    path('admin/trainings/<int:training_id>/submissions/', views.admin_submission_list, name='admin_submission_list'),
    path('admin/submissions/<int:submission_id>/review/', views.admin_submission_review, name='admin_submission_review'),
    
    # API endpoints
    path('api/teams/', views.api_teams_list, name='api_teams_list'),
]

