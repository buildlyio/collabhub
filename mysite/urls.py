from django.conf import settings
from django.urls import include, path, re_path
from django.contrib import admin


from . import views
from .views import homepage

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.authtoken.views import obtain_auth_token

from django.contrib.auth import views as auth_views

from django.urls import path, include

from django.contrib.admin.views.decorators import staff_member_required


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
    path('', homepage, name="home"),  # Homepage as root/default page
    path("register/", views.register, name="register"),
    path("login", views.login_request, name="login"),
    path("logout", views.logout_request, name= "logout"),
    path("edit_profile/", views.edit_profile, name="edit_profile"),
    
    # qr code submissions
    path('submission/', include('submission.urls')),
    
    # team member onboarding
    path('onboarding/', include('onboarding.urls')),
    
    # Agency URLs (redirecting to onboarding app)
    path('agency_list/', views.agency_list_redirect, name='agency_list'),  # Redirect to onboarding agencies list
    path('partner/', views.partner_redirect, name='partner'),  # Redirect to agency registration
    
    # password reset
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('accounts/', include('allauth.urls')),
    # path('punchlist/<int:punchlist_id>/submit/', submit_user_for_punchlist, name='submit_user_for_punchlist'),
    
    # agency review utility call
    path('agency_review_utility/', views.agency_review_utility, name='agency_review_utility'),
    
    # Include your API URLs
    re_path(r'^docs/swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),

]


urlpatterns = urlpatterns + [
    # Basic Token Auth
    path('get-auth-token/', obtain_auth_token, name='get_auth_token'),
]

# Admin URLs
urlpatterns += [
    path('admin/', admin.site.urls),
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
