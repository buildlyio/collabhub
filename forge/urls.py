from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from .views import (
    ForgeAppViewSet, PurchaseViewSet, EntitlementViewSet,
    AdminForgeAppViewSet, AdminPurchaseViewSet, AdminEntitlementViewSet,
    MarketplaceView, AppDetailView, CheckoutView, SuccessView
)

# Create routers for public and admin APIs
public_router = DefaultRouter()
public_router.register(r'apps', ForgeAppViewSet, basename='forgeapp')
public_router.register(r'purchases', PurchaseViewSet, basename='purchase')
public_router.register(r'entitlements', EntitlementViewSet, basename='entitlement')

admin_router = DefaultRouter()
admin_router.register(r'apps', AdminForgeAppViewSet, basename='admin-forgeapp')
admin_router.register(r'purchases', AdminPurchaseViewSet, basename='admin-purchase')
admin_router.register(r'entitlements', AdminEntitlementViewSet, basename='admin-entitlement')

app_name = 'forge'

urlpatterns = [
    # Public HTML marketplace pages
    path('', MarketplaceView.as_view(), name='marketplace-home'),
    # path('debug/', TemplateView.as_view(template_name='forge/debug.html'), name='debug'),
    path('app/<slug:slug>/', AppDetailView.as_view(), name='app-detail'),
    path('checkout/<slug:slug>/', CheckoutView.as_view(), name='checkout'),
    path('success/', SuccessView.as_view(), name='purchase-success'),
    
    # Public API endpoints
    path('api/', include(public_router.urls)),
    
    # Admin API endpoints
    path('admin-api/', include(admin_router.urls)),
    
    # Stripe webhook endpoint (separate from viewset for security)
    path('webhook/stripe/', PurchaseViewSet.as_view({'post': 'handle_webhook'}), name='stripe-webhook'),
]

"""
URL Structure:

Public API (no authentication required for listing/viewing):
- GET /forge/api/apps/ - List published apps (with filtering)
- GET /forge/api/apps/{slug}/ - Get app details

Authenticated API:
- GET /forge/api/purchases/ - User's purchases
- POST /forge/api/purchases/create_checkout/ - Create Stripe checkout
- GET /forge/api/entitlements/ - User's owned apps

Admin API (staff only):
- GET /forge/admin-api/apps/ - List all apps
- POST /forge/admin-api/apps/ - Create new app  
- GET /forge/admin-api/apps/{id}/ - Get app details
- PUT/PATCH /forge/admin-api/apps/{id}/ - Update app
- DELETE /forge/admin-api/apps/{id}/ - Delete app
- POST /forge/admin-api/apps/{slug}/validate/ - Trigger validation

- GET /forge/admin-api/purchases/ - All purchases (with filtering)
- GET /forge/admin-api/entitlements/ - All entitlements (with filtering)

Webhooks:
- POST /forge/webhook/stripe/ - Stripe payment webhooks

Example API calls:

1. List apps with filtering:
   GET /forge/api/apps/?categories=productivity,development&targets=docker&search=buildly

2. Get app details:
   GET /forge/api/apps/buildly-dashboard/

3. Create purchase:
   POST /forge/api/purchases/create_checkout/
   {"forge_app_id": "123e4567-e89b-12d3-a456-426614174000"}

4. Staff create app:
   POST /forge/admin-api/apps/
   {
     "slug": "my-app",
     "name": "My App", 
     "summary": "Description",
     "price_cents": 999,
     "repo_url": "https://github.com/buildly-marketplace/my-app",
     "license_type": "mit",
     "categories": ["productivity"],
     "targets": ["docker"],
     "is_published": true
   }

5. Trigger validation:
   POST /forge/admin-api/apps/my-app/validate/
"""