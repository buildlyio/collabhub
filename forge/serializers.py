from rest_framework import serializers
from django.contrib.auth.models import User
from django.urls import reverse
from urllib.parse import urlparse
from .models import ForgeApp, RepoValidation, Purchase, Entitlement, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    
    class Meta:
        model = UserProfile
        fields = ['is_labs_customer', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class RepoValidationSerializer(serializers.ModelSerializer):
    """Serializer for repository validation results"""
    
    class Meta:
        model = RepoValidation
        fields = [
            'id', 'status', 'missing_items', 'detected_targets', 
            'validated_commit_sha', 'run_at'
        ]
        read_only_fields = ['id', 'run_at']


class ForgeAppListSerializer(serializers.ModelSerializer):
    """Serializer for listing Forge apps (public view)"""
    price_dollars = serializers.ReadOnlyField()
    latest_validation_status = serializers.SerializerMethodField()
    has_release = serializers.SerializerMethodField()
    
    class Meta:
        model = ForgeApp
        fields = [
            'id', 'slug', 'name', 'summary', 'price_cents', 'price_dollars',
            'categories', 'targets', 'logo_url', 'featured_screenshot', 'license_type', 'change_date_utc',
            'latest_validation_status', 'has_release', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_latest_validation_status(self, obj):
        """Get the status of the latest validation"""
        latest = obj.latest_validation
        return latest.status if latest else None
    
    def get_has_release(self, obj):
        """Check if app has a GitHub release available"""
        return obj.has_github_release


class ForgeAppDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed Forge app view (public)"""
    price_dollars = serializers.ReadOnlyField()
    latest_validation = RepoValidationSerializer(read_only=True)
    video_embed_url = serializers.ReadOnlyField()
    has_release = serializers.ReadOnlyField(source='has_github_release')
    
    class Meta:
        model = ForgeApp
        fields = [
            'id', 'slug', 'name', 'summary', 'price_cents', 'price_dollars',
            'repo_url', 'license_type', 'change_date_utc', 'categories', 'targets',
            'logo_url', 'featured_screenshot', 'screenshots', 'demo_video_url', 'video_type', 'video_embed_url',
            'latest_release_name', 'latest_release_tag', 'latest_release_url',
            'has_release', 'latest_validation', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ForgeAppCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating Forge apps (staff only)"""
    
    class Meta:
        model = ForgeApp
        fields = [
            'slug', 'name', 'summary', 'price_cents', 'repo_url', 'repo_owner',
            'repo_name', 'license_type', 'change_date_utc', 'categories', 'targets',
            'logo_url', 'featured_screenshot', 'screenshots', 'demo_video_url', 'video_type', 'is_published'
        ]
    
    def validate_repo_url(self, value):
        """Validate that repo_url is a valid GitHub URL"""
        if not value.startswith('https://github.com/'):
            raise serializers.ValidationError("Repository URL must be a GitHub URL")
        return value
    
    def validate_video_type(self, value):
        """Validate video type is one of allowed choices"""
        if value and value not in ['youtube', 'vimeo', 'loom']:
            raise serializers.ValidationError("Video type must be one of: youtube, vimeo, loom")
        return value
    
    def validate(self, data):
        """Validate repo_owner and repo_name against repo_url"""
        repo_url = data.get('repo_url')
        if repo_url:
            try:
                parsed = urlparse(repo_url)
                path_parts = parsed.path.strip('/').split('/')
                if len(path_parts) >= 2:
                    owner, name = path_parts[0], path_parts[1]
                    # Remove .git suffix if present
                    if name.endswith('.git'):
                        name = name[:-4]
                    
                    data['repo_owner'] = owner
                    data['repo_name'] = name
                else:
                    raise serializers.ValidationError("Invalid GitHub repository URL format")
            except Exception:
                raise serializers.ValidationError("Could not parse repository URL")
        
        return data
    
    def validate_repo_owner(self, value):
        """Validate that repo_owner matches the marketplace organization"""
        from django.conf import settings
        marketplace_org = getattr(settings, 'FORGE_MARKETPLACE_ORG', 'buildly-marketplace')
        if value != marketplace_org:
            raise serializers.ValidationError(f"Repository must be in {marketplace_org} organization")
        return value
    
    def validate_targets(self, value):
        """Validate targets list"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Targets must be a list")
        
        valid_targets = ['github-pages', 'docker', 'k8s', 'desktop', 'web-embed']
        invalid_targets = [target for target in value if target not in valid_targets]
        if invalid_targets:
            raise serializers.ValidationError(f"Invalid targets: {invalid_targets}")
        
        return value
    
    def validate_categories(self, value):
        """Validate categories list"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Categories must be a list")
        return value
    
    def validate_screenshots(self, value):
        """Validate screenshots list"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Screenshots must be a list")
        return value


class PurchaseSerializer(serializers.ModelSerializer):
    """Serializer for user purchases"""
    user = serializers.StringRelatedField(read_only=True)
    forge_app = ForgeAppListSerializer(read_only=True)
    amount_dollars = serializers.ReadOnlyField()
    can_download = serializers.SerializerMethodField()
    
    class Meta:
        model = Purchase
        fields = [
            'id', 'user', 'forge_app', 'stripe_payment_intent_id',
            'amount_cents', 'amount_dollars', 'discount_applied', 'status', 
            'download_count', 'last_downloaded', 'can_download', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'download_count', 'last_downloaded', 'created_at']
    
    def get_can_download(self, obj):
        """Check if purchase can be downloaded"""
        return obj.status == 'completed' and obj.forge_app.has_github_release


class EntitlementSerializer(serializers.ModelSerializer):
    """Serializer for user entitlements"""
    user = serializers.StringRelatedField(read_only=True)
    forge_app_slug = serializers.CharField(source='forge_app.slug', read_only=True)
    forge_app_name = serializers.CharField(source='forge_app.name', read_only=True)
    
    class Meta:
        model = Entitlement
        fields = ['id', 'user', 'forge_app_slug', 'forge_app_name', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class CheckoutSessionRequestSerializer(serializers.Serializer):
    """Serializer for checkout session creation request"""
    forge_app_id = serializers.UUIDField()
    
    def validate_forge_app_id(self, value):
        """Validate that the forge app exists and is published"""
        try:
            app = ForgeApp.objects.get(id=value, is_published=True)
            return value
        except ForgeApp.DoesNotExist:
            raise serializers.ValidationError("Forge app not found or not published")


class CheckoutSessionResponseSerializer(serializers.Serializer):
    """Serializer for checkout session creation response"""
    checkout_url = serializers.URLField()
    purchase_id = serializers.UUIDField()


class ValidationTriggerSerializer(serializers.Serializer):
    """Serializer for triggering validation"""
    pass  # No input fields needed