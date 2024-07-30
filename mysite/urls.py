from django.conf import settings
from django.urls import include, path, re_path
from django.contrib import admin

from django.conf.urls import url
from punchlist.views import *
from . import views


from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.authtoken.views import obtain_auth_token

from django.contrib.auth import views as auth_views

schema_view = get_schema_view(
   openapi.Info(
      title="Buildly CollabHub",
      default_version='v1',
      description="Buildly CollabHub API",
      terms_of_service="https://www.buildly.io/terms/",
      contact=openapi.Contact(email="team@buildly.io"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', homepage, name="home"),
    path("register/", views.register, name="register"),
    path("login", views.login_request, name="login"),
    path("logout", views.logout_request, name= "logout"),
    path("edit_profile/", views.edit_profile, name="edit_profile"),
    
    # password reset
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('accounts/', include('allauth.urls')),
    path('punchlist/<int:punchlist_id>/submit/', submit_user_for_punchlist, name='submit_user_for_punchlist'),
    
    # Include your API URLs
    re_path(r'^docs/swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),

]


urlpatterns = urlpatterns + [
    # Punchlists
    url(r'^punchlist/dashboard/(?P<pk>\w+)/$', dashboard),
    url(r'^punchlist/report/(?P<pk>\w+)/$', report),
    url(r'^bounties/$', PunchlistList.as_view(), name='punchlists_list'),
    # Forms
    url(r'^punchlist_add/$', PunchlistCreate.as_view(), name='punchlists_add'),
    url(r'^punchlist_update/(?P<pk>\w+)/$', PunchlistUpdate.as_view(), name='punchlists_update'),
    url(r'^punchlist_delete/(?P<pk>\w+)/$', PunchlistDelete.as_view(), name='punchlists_delete'),
    url(r'^punchlist_detail/(?P<pk>\w+)/$', PunchlistDetailView.as_view(), name='punchlist_detail'),
    
    # PunchlistHunterForms
    url(r'^punchlisthunter_add/$', PunchlistHunterCreate.as_view(), name='punchlisthunter_add'),
    url(r'^punchlisthunter_update/(?P<pk>\w+)/$', PunchlistHunterUpdate.as_view(), name='punchlisthunter_update'),
    url(r'^punchlisthunter_delete/(?P<pk>\w+)/$', PunchlistHunterDelete.as_view(), name='punchlisthunter_delete'),
    url(r'^punchlisthunter_detail/(?P<pk>\w+)/$', PunchlistHunterDetailView.as_view(), name='punchlisthunter_detail'),
    
    # UserSubmittedBug
    url(r'^bug_add/$', BugCreateView.as_view(), name='bug_add'),
    path('bug_list/', bug_list, name='bug_list'),
    path('bug_accept/<str:pk>/', accept_bug, name='bug_accept'),
    path('bug_send_to_github/<str:pk>/', send_to_github, name='bug_send_to_github'),
    path('submit_bug_to_github/<str:pk>/', submit_bug_to_github, name='submit_bug_to_github'),
    path('submit_issue_to_github/<str:pk>/', submit_issue_to_github, name='submit_issue_to_github'),
    
    # Agency
    url(r'^agency_add/$', DevelopmentAgencyCreateView.as_view(), name='agency_add'),
    url(r'^agency_list/$', showcase_agencies, name='agency_list'),
    url(r'^partner/$', DevelopmentAgencyCreateView.as_view(), name='partner'),
    
    # CollabHub
    path('collabhub/', collabhub, name='collabhub'),
    
    # Basic Token Auth
    # Obtain authentication token
    path('get-auth-token/', obtain_auth_token, name='get_auth_token'),
]


from django.urls import path
from punchlist import serializer_views

urlpatterns = urlpatterns + [
    path('positions/', serializer_views.PositionList.as_view(), name='position-list'),
    path('positions/<int:pk>/', serializer_views.PositionDetail.as_view(), name='position-detail'),

    path('bugs/', serializer_views.BugList.as_view(), name='bug-list'),
    path('bugs/<int:pk>/', serializer_views.BugDetail.as_view(), name='bug-detail'),

    path('punchlist-submissions/', serializer_views.PunchlistSubmissionList.as_view(), name='punchlist-submission-list'),
    path('punchlist-submissions/<int:pk>/', serializer_views.PunchlistSubmissionDetail.as_view(), name='punchlist-submission-detail'),

    path('punchlist-setters/', serializer_views.PunchlistSetterList.as_view(), name='punchlist-setter-list'),
    path('punchlist-setters/<int:pk>/', serializer_views.PunchlistSetterDetail.as_view(), name='punchlist-setter-detail'),

    path('punchlist-hunters/', serializer_views.PunchlistHunterList.as_view(), name='punchlist-hunter-list'),
    path('punchlist-hunters/<int:pk>/', serializer_views.PunchlistHunterDetail.as_view(), name='punchlist-hunter-detail'),

    path('bounties/', serializer_views.PunchlistList.as_view(), name='punchlist-list'),
    path('bounties/<int:pk>/', serializer_views.PunchlistDetail.as_view(), name='punchlist-detail'),

    path('issues/', serializer_views.IssueList.as_view(), name='issue-list'),
    path('issues/<int:pk>/', serializer_views.IssueDetail.as_view(), name='issue-detail'),

    path('plans/', serializer_views.PlanList.as_view(), name='plan-list'),
    path('plans/<int:pk>/', serializer_views.PlanDetail.as_view(), name='plan-detail'),

    path('accepted-bounties/', serializer_views.AcceptedPunchlistList.as_view(), name='accepted-punchlist-list'),
    path('accepted-bounties/<int:pk>/', serializer_views.AcceptedPunchlistDetail.as_view(), name='accepted-punchlist-detail'),

    path('contracts/', serializer_views.ContractList.as_view(), name='contract-list'),
    path('contracts/<int:pk>/', serializer_views.ContractDetail.as_view(), name='contract-detail'),

    path('development-agencies/', serializer_views.DevelopmentAgencyList.as_view(), name='development-agency-list'),
    path('development-agencies/<int:pk>/', serializer_views.DevelopmentAgencyDetail.as_view(), name='development-agency-detail'),
]



if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    urlpatterns = urlpatterns + [
        # For anything not caught by a more specific rule above, hand over to
        # the list:
        path('__debug__/', include('debug_toolbar.urls')),
]
