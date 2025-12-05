from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.db import models
from django.http import HttpResponse
from django.utils import timezone
import stripe
import logging

from .models import ForgeApp, Purchase, Entitlement, UserProfile
from .pdf_generator import generate_license_pdf
from .github_release_service import GitHubReleaseService
from .download_service import LicenseDownloadService
from .serializers import (
    ForgeAppListSerializer, ForgeAppDetailSerializer, ForgeAppCreateUpdateSerializer,
    PurchaseSerializer, EntitlementSerializer, CheckoutSessionRequestSerializer,
    CheckoutSessionResponseSerializer, ValidationTriggerSerializer
)
from .services import GitHubRepoValidationService

logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = getattr(settings, 'STRIPE_API_KEY', '')


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for API responses"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ForgeAppViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Forge app management
    
    - list: Public listing of published apps
    - retrieve: Public detailed view of published apps
    - create: Staff only - create new app
    - update/partial_update: Staff only - update existing app
    - destroy: Staff only - delete app
    - validate: Staff only - trigger repository validation
    """
    pagination_class = StandardResultsSetPagination
    lookup_field = 'slug'
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        if self.action in ['list', 'retrieve']:
            # Public views - only published apps
            return ForgeApp.objects.filter(is_published=True).order_by('-created_at')
        else:
            # Staff views - all apps
            return ForgeApp.objects.all().order_by('-created_at')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return ForgeAppListSerializer
        elif self.action == 'retrieve':
            return ForgeAppDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ForgeAppCreateUpdateSerializer
        elif self.action == 'validate':
            return ValidationTriggerSerializer
        return ForgeAppDetailSerializer
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['list', 'retrieve']:
            # Public actions
            permission_classes = [permissions.AllowAny]
        else:
            # Staff-only actions
            permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def list(self, request, *args, **kwargs):
        """List published apps with filtering and search"""
        queryset = self.get_queryset()
        
        # Filter by categories
        categories = request.query_params.get('categories')
        if categories:
            category_list = [cat.strip() for cat in categories.split(',')]
            queryset = queryset.filter(categories__overlap=category_list)
        
        # Filter by targets
        targets = request.query_params.get('targets')
        if targets:
            target_list = [target.strip() for target in targets.split(',')]
            queryset = queryset.filter(targets__overlap=target_list)
        
        # Search by name or summary
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(name__icontains=search) | 
                models.Q(summary__icontains=search)
            )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, permissions.IsAdminUser])
    def validate(self, request, slug=None):
        """Trigger repository validation for an app"""
        app = self.get_object()
        
        try:
            # Use the validation service
            validator = GitHubRepoValidationService()
            validation = validator.validate_repository(
                owner=app.repo_owner,
                repo=app.repo_name,
                forge_app=app
            )
            
            # Return validation results
            from .serializers import RepoValidationSerializer
            serializer = RepoValidationSerializer(validation)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Validation failed for {app.slug}: {str(e)}")
            return Response(
                {'error': 'Validation failed', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, permissions.IsAdminUser])
    def update_release(self, request, slug=None):
        """
        Update GitHub release information for an app (admin only)
        
        Optional POST data: {'force': true/false}
        """
        app = self.get_object()
        force = request.data.get('force', False)
        
        if not app.repo_url:
            return Response(
                {'error': 'No repository configured for this app'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update release info
        github_service = GitHubReleaseService()
        updated = github_service.update_app_release_info(app, force=force)
        
        if updated:
            return Response({
                'success': True,
                'message': f'Release info updated for {app.name}',
                'release': {
                    'name': app.latest_release_name,
                    'tag': app.latest_release_tag,
                    'url': app.latest_release_url,
                    'last_checked': app.last_release_check
                }
            })
        else:
            return Response({
                'success': False,
                'message': 'No release found or not updated (check within last hour)'
            })
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def filter_options(self, request):
        """
        Get all unique categories and targets from published apps
        
        Returns: {
            'categories': ['productivity', 'development', ...],
            'targets': ['docker', 'k8s', ...]
        }
        """
        published_apps = ForgeApp.objects.filter(is_published=True)
        
        # Collect all unique categories
        all_categories = set()
        for app in published_apps:
            if app.categories:
                all_categories.update(app.categories)
        
        # Collect all unique targets
        all_targets = set()
        for app in published_apps:
            if app.targets:
                all_targets.update(app.targets)
        
        return Response({
            'categories': sorted(list(all_categories)),
            'targets': sorted(list(all_targets))
        })



class PurchaseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for user purchases (read-only)
    
    - list: User's own purchases
    - retrieve: Specific purchase details
    - create_checkout: Create Stripe checkout session
    """
    serializer_class = PurchaseSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Return purchases for the current user"""
        return Purchase.objects.filter(user=self.request.user).order_by('-created_at')
    
    @action(detail=False, methods=['post'])
    def create_checkout(self, request):
        """Create a Stripe checkout session for purchasing an app"""
        logger.info(f"Checkout request from user {request.user} with data: {request.data}")
        
        serializer = CheckoutSessionRequestSerializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Serializer validation failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.is_valid(raise_exception=True)
        
        forge_app_id = serializer.validated_data['forge_app_id']
        forge_app = get_object_or_404(ForgeApp, id=forge_app_id, is_published=True)
        
        # Check if user already owns this app
        if Entitlement.objects.filter(user=request.user, forge_app=forge_app).exists():
            return Response(
                {'error': 'You already own this app'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Check Stripe configuration
            if not stripe.api_key:
                logger.error("Stripe API key not configured")
                return Response(
                    {'error': 'Payment system not configured'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Get user profile to check for discounts
            user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
            
            # Calculate price with discount
            price_cents = forge_app.price_cents
            discount_applied = False
            
            if user_profile.is_labs_customer:
                # 50% discount for labs customers
                price_cents = price_cents // 2
                discount_applied = True
            
            # Create purchase record
            purchase = Purchase.objects.create(
                user=request.user,
                forge_app=forge_app,
                amount_cents=price_cents,
                discount_applied=discount_applied,
                status='pending'
            )
            
            # Create Stripe checkout session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': forge_app.name,
                            'description': forge_app.summary,
                        },
                        'unit_amount': price_cents,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=f"{settings.FRONTEND_URL}/forge/purchase/success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{settings.FRONTEND_URL}/forge/purchase/cancel",
                metadata={
                    'purchase_id': str(purchase.id),
                    'forge_app_id': str(forge_app.id),
                    'forge_app_slug': forge_app.slug,
                    'forge_app_name': forge_app.name,
                    'forge_app_repo_url': forge_app.repo_url,
                    'forge_app_repo_owner': forge_app.repo_owner,
                    'forge_app_repo_name': forge_app.repo_name,
                    'forge_app_license_type': forge_app.license_type,
                    'user_id': str(request.user.id),
                    'user_email': request.user.email,
                    'user_name': f"{request.user.first_name} {request.user.last_name}".strip(),
                    'original_price_cents': str(forge_app.price_cents),
                    'final_price_cents': str(price_cents),
                    'discount_applied': str(discount_applied),
                    'is_labs_customer': str(user_profile.is_labs_customer),
                }
            )
            
            # Update purchase with Stripe session info
            purchase.stripe_payment_intent_id = checkout_session.payment_intent
            purchase.stripe_session_id = checkout_session.id
            purchase.save()
            
            response_serializer = CheckoutSessionResponseSerializer({
                'checkout_url': checkout_session.url,
                'purchase_id': purchase.id
            })
            
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except stripe.StripeError as e:
            logger.error(f"Stripe error creating checkout: {str(e)}")
            return Response(
                {'error': 'Payment processing error', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.error(f"Error creating checkout: {str(e)}")
            return Response(
                {'error': 'Internal server error', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def guest_checkout_session(self, request):
        """Create a Stripe checkout session for guest users"""
        app_slug = request.data.get('app_slug')
        customer_email = request.data.get('customer_email')
        customer_name = request.data.get('customer_name')
        success_url = request.data.get('success_url')
        cancel_url = request.data.get('cancel_url')
        
        if not all([app_slug, customer_email, success_url, cancel_url]):
            return Response(
                {'error': 'Missing required fields'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        forge_app = get_object_or_404(ForgeApp, slug=app_slug, is_published=True)
        
        try:
            # Create Stripe checkout session for guest
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                customer_email=customer_email,
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': forge_app.name,
                            'description': forge_app.summary,
                        },
                        'unit_amount': forge_app.price_cents,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=cancel_url,
                metadata={
                    'forge_app_slug': forge_app.slug,
                    'customer_email': customer_email,
                    'customer_name': customer_name,
                    'is_guest_purchase': 'true'
                }
            )
            
            return Response({
                'checkout_url': checkout_session.url,
                'session_id': checkout_session.id
            }, status=status.HTTP_201_CREATED)
            
        except stripe.StripeError as e:
            logger.error(f"Stripe error in guest checkout: {str(e)}")
            return Response(
                {'error': 'Payment processing error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.error(f"Error in guest checkout: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """
        Download licensed release zip file for a purchased app
        
        Returns a zip file with the latest GitHub release and injected license
        """
        purchase = self.get_object()
        
        # Verify purchase is completed
        if purchase.status != 'completed':
            return Response(
                {'error': 'Purchase not completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user owns this purchase
        if purchase.user != request.user:
            return Response(
                {'error': 'Unauthorized'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        forge_app = purchase.forge_app
        
        # Check if app has GitHub releases
        if not forge_app.repo_url:
            return Response(
                {'error': 'No repository configured for this app'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create licensed download
        download_service = LicenseDownloadService()
        zip_content, filename = download_service.create_licensed_download(forge_app, purchase)
        
        if not zip_content:
            return Response(
                {'error': 'Failed to generate download. Please try again later.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Update download tracking
        purchase.download_count += 1
        purchase.last_downloaded = timezone.now()
        purchase.save(update_fields=['download_count', 'last_downloaded'])
        
        # Return zip file
        response = HttpResponse(zip_content, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Content-Length'] = len(zip_content)
        
        logger.info(f"User {request.user.username} downloaded {forge_app.name} (purchase {purchase.id})")
        
        return response
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def update_release(self, request):
        """
        Update GitHub release information for an app (admin only)
        
        POST data: {'app_id': 'uuid', 'force': true/false}
        """
        app_id = request.data.get('app_id')
        force = request.data.get('force', False)
        
        if not app_id:
            return Response(
                {'error': 'app_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            forge_app = ForgeApp.objects.get(id=app_id)
        except ForgeApp.DoesNotExist:
            return Response(
                {'error': 'App not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Update release info
        github_service = GitHubReleaseService()
        updated = github_service.update_app_release_info(forge_app, force=force)
        
        if updated:
            return Response({
                'success': True,
                'message': f'Release info updated for {forge_app.name}',
                'release': {
                    'name': forge_app.latest_release_name,
                    'tag': forge_app.latest_release_tag,
                    'url': forge_app.latest_release_url,
                }
            })
        else:
            return Response({
                'success': False,
                'message': 'No release found or not updated'
            })

    
    @action(detail=False, methods=['post'])
    def handle_webhook(self, request):
        """Handle Stripe webhook events"""
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError:
            logger.error("Invalid payload in Stripe webhook")
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except stripe.SignatureError:
            logger.error("Invalid signature in Stripe webhook")
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            self._handle_successful_payment(session)
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            self._handle_failed_payment(payment_intent)
        
        return Response(status=status.HTTP_200_OK)
    
    def _handle_successful_payment(self, session):
        """Handle successful payment from Stripe webhook"""
        try:
            purchase_id = session['metadata']['purchase_id']
            purchase = Purchase.objects.get(id=purchase_id)
            
            # Update purchase status
            purchase.status = 'completed'
            purchase.stripe_payment_intent_id = session['payment_intent']
            purchase.stripe_session_id = session['id']
            
            # Generate license PDF with comprehensive metadata
            purchase_data = session['metadata']
            pdf_buffer = generate_license_pdf(purchase_data, str(purchase.id))
            
            # Save the PDF to the purchase record
            filename = f"license_and_support_{purchase.forge_app.slug}_{purchase.id}.pdf"
            purchase.license_document.save(
                filename,
                ContentFile(pdf_buffer.read()),
                save=False
            )
            
            purchase.save()
            
            # Create entitlement
            Entitlement.objects.get_or_create(
                user=purchase.user,
                forge_app=purchase.forge_app,
                defaults={'purchase': purchase}
            )
            
            logger.info(f"Successfully processed payment and generated license for purchase {purchase_id}")
            
        except Purchase.DoesNotExist:
            logger.error(f"Purchase not found for session {session['id']}")
        except Exception as e:
            logger.error(f"Error processing successful payment: {str(e)}")
    
    def _handle_failed_payment(self, payment_intent):
        """Handle failed payment from Stripe webhook"""
        try:
            purchase = Purchase.objects.get(stripe_payment_intent_id=payment_intent['id'])
            purchase.status = 'failed'
            purchase.save()
            
            logger.info(f"Marked purchase {purchase.id} as failed")
            
        except Purchase.DoesNotExist:
            logger.error(f"Purchase not found for payment intent {payment_intent['id']}")
        except Exception as e:
            logger.error(f"Error processing failed payment: {str(e)}")
    
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def download_license(self, request, pk=None):
        """Download the license document for a completed purchase"""
        try:
            purchase = get_object_or_404(Purchase, id=pk, user=request.user, status='completed')
            
            if not purchase.license_document:
                # If no document exists, generate it now
                purchase_data = {
                    'forge_app_name': purchase.forge_app.name,
                    'forge_app_repo_url': purchase.forge_app.repo_url,
                    'forge_app_repo_owner': purchase.forge_app.repo_owner,
                    'forge_app_repo_name': purchase.forge_app.repo_name,
                    'forge_app_license_type': purchase.forge_app.license_type,
                    'user_email': purchase.user.email,
                    'user_name': f"{purchase.user.first_name} {purchase.user.last_name}".strip(),
                    'original_price_cents': str(purchase.forge_app.price_cents),
                    'final_price_cents': str(purchase.amount_cents),
                    'discount_applied': str(purchase.discount_applied),
                    'is_labs_customer': str(hasattr(purchase.user, 'forge_profile') and purchase.user.forge_profile.is_labs_customer),
                }
                
                pdf_buffer = generate_license_pdf(purchase_data, str(purchase.id))
                filename = f"license_and_support_{purchase.forge_app.slug}_{purchase.id}.pdf"
                purchase.license_document.save(
                    filename,
                    ContentFile(pdf_buffer.read()),
                    save=True
                )
            
            # Return the file for download
            from django.http import HttpResponse
            response = HttpResponse(purchase.license_document.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="Buildly_License_{purchase.forge_app.name}_{purchase.id}.pdf"'
            return response
            
        except Exception as e:
            logger.error(f"Error downloading license: {str(e)}")
            return Response(
                {'error': 'Unable to generate license document'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class EntitlementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for user entitlements (read-only)
    
    - list: User's owned apps
    - retrieve: Specific entitlement details
    """
    serializer_class = EntitlementSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Return entitlements for the current user"""
        return Entitlement.objects.filter(user=self.request.user).order_by('-created_at')


# Staff-only views for admin interface
class AdminForgeAppViewSet(viewsets.ModelViewSet):
    """
    Admin viewset for complete Forge app management
    Only accessible by staff users
    """
    queryset = ForgeApp.objects.all().order_by('-created_at')
    serializer_class = ForgeAppCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    pagination_class = StandardResultsSetPagination
    lookup_field = 'id'  # Use ID instead of slug for admin


class AdminPurchaseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Admin viewset for viewing all purchases
    Only accessible by staff users
    """
    queryset = Purchase.objects.all().order_by('-created_at')
    serializer_class = PurchaseSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Admin can see all purchases with filtering"""
        queryset = super().get_queryset()
        
        # Filter by user
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset


class AdminEntitlementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Admin viewset for viewing all entitlements
    Only accessible by staff users
    """
    queryset = Entitlement.objects.all().order_by('-created_at')
    serializer_class = EntitlementSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Admin can see all entitlements with filtering"""
        queryset = super().get_queryset()
        
        # Filter by user
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by forge app
        forge_app_id = self.request.query_params.get('forge_app_id')
        if forge_app_id:
            queryset = queryset.filter(forge_app_id=forge_app_id)
        
        return queryset


# HTML Template Views for Public Marketplace
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from django.http import JsonResponse
import json

class MarketplaceView(TemplateView):
    """Public marketplace listing page"""
    template_name = 'forge/marketplace.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['apps_count'] = ForgeApp.objects.filter(is_published=True).count()
        return context


class AppDetailView(TemplateView):
    """Public app detail page"""
    template_name = 'forge/app_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = kwargs.get('slug')
        app = get_object_or_404(ForgeApp, slug=slug, is_published=True)
        context['app'] = app
        return context


class CheckoutView(TemplateView):
    """Checkout page for app purchase"""
    template_name = 'forge/checkout.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = kwargs.get('slug')
        app = get_object_or_404(ForgeApp, slug=slug, is_published=True)
        
        context['app'] = app
        
        # Calculate pricing
        if self.request.user.is_authenticated:
            try:
                user_profile = UserProfile.objects.get(user=self.request.user)
                if user_profile.is_labs_customer:
                    context['discount_amount'] = app.price_dollars / 2
                    context['final_price'] = app.price_dollars / 2
                else:
                    context['final_price'] = app.price_dollars
            except UserProfile.DoesNotExist:
                context['final_price'] = app.price_dollars
        else:
            context['final_price'] = app.price_dollars
        
        return context


class SuccessView(TemplateView):
    """Purchase success page"""
    template_name = 'forge/success.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get session_id from URL parameters
        session_id = self.request.GET.get('session_id')
        
        if session_id:
            try:
                # Retrieve the Stripe session
                session = stripe.checkout.Session.retrieve(session_id)
                
                # Find the corresponding purchase
                purchase = Purchase.objects.get(
                    stripe_session_id=session_id,
                    user=self.request.user if self.request.user.is_authenticated else None
                )
                
                context['purchase'] = purchase
                context['session'] = session
                context['show_download_link'] = purchase.status == 'completed' and purchase.license_document
                
            except (Purchase.DoesNotExist, stripe.StripeError) as e:
                logger.error(f"Error retrieving purchase info for session {session_id}: {str(e)}")
                context['error'] = "Unable to retrieve purchase information"
        
        return context
