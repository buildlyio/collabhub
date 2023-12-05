from django.conf import settings
from django.urls import include, path, re_path
from django.contrib import admin

from django.conf.urls import url
from bounty.views import *
from . import views


from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.authtoken.views import obtain_auth_token

schema_view = get_schema_view(
   openapi.Info(
      title="Buildly Marketplace",
      default_version='v1',
      description="Buildly Marketplace API",
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

    path('accounts/', include('allauth.urls')),
    path('bounty/<int:bounty_id>/submit/', submit_user_for_bounty, name='submit_user_for_bounty'),
    
    # Include your API URLs
    re_path(r'^docs/swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),

]


urlpatterns = urlpatterns + [
    # Bountys
    url(r'^bounty/dashboard/(?P<pk>\w+)/$', dashboard),
    url(r'^bounty/report/(?P<pk>\w+)/$', report),
    url(r'^bounties/$', BountyList.as_view(), name='bountys_list'),
    # Forms
    url(r'^bounty_add/$', BountyCreate.as_view(), name='bountys_add'),
    url(r'^bounty_update/(?P<pk>\w+)/$', BountyUpdate.as_view(), name='bountys_update'),
    url(r'^bounty_delete/(?P<pk>\w+)/$', BountyDelete.as_view(), name='bountys_delete'),
    url(r'^bounty_detail/(?P<pk>\w+)/$', BountyDetailView.as_view(), name='bounty_detail'),
    
    # BountyHunterForms
    url(r'^bountyhunter_add/$', BountyHunterCreate.as_view(), name='bountyhunter_add'),
    url(r'^bountyhunter_update/(?P<pk>\w+)/$', BountyHunterUpdate.as_view(), name='bountyhunter_update'),
    url(r'^bountyhunter_delete/(?P<pk>\w+)/$', BountyHunterDelete.as_view(), name='bountyhunter_delete'),
    url(r'^bountyhunter_detail/(?P<pk>\w+)/$', BountyHunterDetailView.as_view(), name='bountyhunter_detail'),
    
    # UserSubmittedBug
    url(r'^bug_add/$', BugCreateView.as_view(), name='bug_add'),
    path('bug_list/', bug_list, name='bug_list'),
    path('bug_accept/<str:pk>/', accept_bug, name='bug_accept'),
    path('bug_send_to_github/<str:pk>/', send_to_github, name='bug_send_to_github'),
    path('submit_bug_to_github/<str:pk>/<str:object_type>=bug', submit_to_github, name='submit_bug_to_github'),
    path('submit_issue_to_github/<str:pk>/<str:object_type>=issue', submit_to_github, name='submit_issue_to_github'),
    
    # Agency
    url(r'^agency_add/$', DevelopmentAgencyCreateView.as_view(), name='agency_add'),
    url(r'^agency_list/$', showcase_agencies, name='agency_list'),
    url(r'^partner/$', DevelopmentAgencyCreateView.as_view(), name='partner'),
    
    # Marketplace
    path('marketplace/', marketplace, name='marketplace'),
    
    # Basic Token Auth
    # Obtain authentication token
    path('get-auth-token/', obtain_auth_token, name='get_auth_token'),
]


from django.urls import path
from bounty import serializer_views

urlpatterns = urlpatterns + [
    path('positions/', serializer_views.PositionList.as_view(), name='position-list'),
    path('positions/<int:pk>/', serializer_views.PositionDetail.as_view(), name='position-detail'),

    path('bugs/', serializer_views.BugList.as_view(), name='bug-list'),
    path('bugs/<int:pk>/', serializer_views.BugDetail.as_view(), name='bug-detail'),

    path('bounty-submissions/', serializer_views.BountySubmissionList.as_view(), name='bounty-submission-list'),
    path('bounty-submissions/<int:pk>/', serializer_views.BountySubmissionDetail.as_view(), name='bounty-submission-detail'),

    path('bounty-setters/', serializer_views.BountySetterList.as_view(), name='bounty-setter-list'),
    path('bounty-setters/<int:pk>/', serializer_views.BountySetterDetail.as_view(), name='bounty-setter-detail'),

    path('bounty-hunters/', serializer_views.BountyHunterList.as_view(), name='bounty-hunter-list'),
    path('bounty-hunters/<int:pk>/', serializer_views.BountyHunterDetail.as_view(), name='bounty-hunter-detail'),

    path('bounties/', serializer_views.BountyList.as_view(), name='bounty-list'),
    path('bounties/<int:pk>/', serializer_views.BountyDetail.as_view(), name='bounty-detail'),

    path('issues/', serializer_views.IssueList.as_view(), name='issue-list'),
    path('issues/<int:pk>/', serializer_views.IssueDetail.as_view(), name='issue-detail'),

    path('plans/', serializer_views.PlanList.as_view(), name='plan-list'),
    path('plans/<int:pk>/', serializer_views.PlanDetail.as_view(), name='plan-detail'),

    path('accepted-bounties/', serializer_views.AcceptedBountyList.as_view(), name='accepted-bounty-list'),
    path('accepted-bounties/<int:pk>/', serializer_views.AcceptedBountyDetail.as_view(), name='accepted-bounty-detail'),

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
