from django.conf import settings
from django.urls import include, path
from django.contrib import admin

from django.conf.urls import url
from hunters.views import *
from . import views

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', homepage),
    path("register", views.register_request, name="register"),
    path("login", views.login_request, name="login"),
    path("logout", views.logout_request, name= "logout"),

    # Paypal forms
    path('paypal/', include('paypal.standard.ipn.urls')),
    path('/paypal-return/', views.PaypalReturnView.as_view(), name='paypal-return'),
    path('/paypal-cancel/', views.PaypalCancelView.as_view(), name='paypal-cancel'),

    path('accounts/', include('allauth.urls')),
]


urlpatterns = urlpatterns + [
    # Hunters
    url(r'^hunters/dashboard/(?P<pk>\w+)/$', dashboard),
    url(r'^hunters/report/(?P<pk>\w+)/$', report),
    url(r'^hunters/$', HunterList.as_view(), name='hunters_list'),
    # Forms
    url(r'^hunter_add/$', HunterCreate.as_view(), name='hunters_add'),
    url(r'^hunter_update/(?P<pk>\w+)/$', HunterUpdate.as_view(), name='hunters_update'),
    url(r'^hunter_delete/(?P<pk>\w+)/$', HunterDelete.as_view(), name='hunters_delete'),
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
