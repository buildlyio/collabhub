from django.conf import settings
from django.urls import include, path
from django.contrib import admin

from django.conf.urls import url
from bounty.views import *
from . import views

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', homepage),
    path("register/", views.register, name="register"),
    path("login", views.login_request, name="login"),
    path("logout", views.logout_request, name= "logout"),
    path("edit_profile/", views.edit_profile, name="edit_profile"),

    path('accounts/', include('allauth.urls')),
    path('bounty/<int:bounty_id>/submit/', submit_user_for_bounty, name='submit_user_for_bounty'),

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
    url(r'^bbountyhunter_delete/(?P<pk>\w+)/$', BountyHunterDelete.as_view(), name='bountyhunter_delete'),
    url(r'^bountyhunter_detail/(?P<pk>\w+)/$', BountyHunterDetailView.as_view(), name='bountyhunter_detail'),
    
    # UserSubmittedBug
    url(r'^bug_add/$', BugCreateView.as_view(), name='bug_add'),
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
