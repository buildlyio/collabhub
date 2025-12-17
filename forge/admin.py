from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django import forms
from .models import ForgeApp, RepoValidation, Purchase, Entitlement, UserProfile


class ForgeAppForm(forms.ModelForm):
    """Custom form for ForgeApp with better price handling"""
    
    # Custom fields for better UX
    categories_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g., productivity, development, ai-ml (comma-separated)',
            'size': 80
        }),
        help_text='Enter categories separated by commas. Examples: productivity, development, ai-ml, database, security'
    )
    
    targets_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g., docker, k8s, github-pages (comma-separated)',
            'size': 80
        }),
        help_text='Enter deployment targets separated by commas. Valid options: docker, k8s, github-pages, desktop, web-embed'
    )
    
    class Meta:
        model = ForgeApp
        fields = '__all__'
        help_texts = {
            'price_cents': 'Enter price in cents (e.g., 2999 for $29.99, 0 for free)',
        }
        widgets = {
            'price_cents': forms.NumberInput(attrs={
                'min': 0,
                'step': 1,
                'placeholder': 'e.g., 2999 for $29.99'
            }),
            'categories': forms.HiddenInput(),
            'targets': forms.HiddenInput(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-populate the text input fields with existing values
        if self.instance.pk:
            if self.instance.categories:
                self.fields['categories_input'].initial = ', '.join(self.instance.categories)
            if self.instance.targets:
                self.fields['targets_input'].initial = ', '.join(self.instance.targets)
    
    def clean_categories_input(self):
        """Convert comma-separated string to list"""
        value = self.cleaned_data.get('categories_input', '')
        if not value:
            return []
        # Split by comma, strip whitespace, filter empty strings
        return [cat.strip() for cat in value.split(',') if cat.strip()]
    
    def clean_targets_input(self):
        """Convert comma-separated string to list and validate"""
        value = self.cleaned_data.get('targets_input', '')
        if not value:
            return []
        # Split by comma, strip whitespace, filter empty strings
        targets = [t.strip() for t in value.split(',') if t.strip()]
        
        # Validate against allowed targets
        valid_targets = ['github-pages', 'docker', 'k8s', 'desktop', 'web-embed']
        invalid = [t for t in targets if t not in valid_targets]
        if invalid:
            raise forms.ValidationError(
                f"Invalid targets: {', '.join(invalid)}. Valid options are: {', '.join(valid_targets)}"
            )
        return targets
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Set the JSON fields from the text inputs
        instance.categories = self.cleaned_data.get('categories_input', [])
        instance.targets = self.cleaned_data.get('targets_input', [])
        if commit:
            instance.save()
        return instance


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_labs_customer', 'created_at']
    list_filter = ['is_labs_customer', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']


class RepoValidationInline(admin.TabularInline):
    model = RepoValidation
    fields = ['status', 'detected_targets', 'run_at']
    readonly_fields = ['status', 'detected_targets', 'run_at']
    extra = 0
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(ForgeApp)
class ForgeAppAdmin(admin.ModelAdmin):
    form = ForgeAppForm
    list_display = [
        'name', 'slug', 'price_dollars', 'is_published', 
        'latest_validation_status', 'has_release_display', 'repo_link', 'created_at'
    ]
    list_filter = [
        'is_published', 'license_type', 'categories', 
        'targets', 'video_type', 'created_at'
    ]
    search_fields = ['name', 'slug', 'summary', 'repo_owner', 'repo_name']
    readonly_fields = [
        'id', 'repo_owner', 'repo_name', 
        'latest_validation_display', 'release_info_display', 
        'created_at', 'updated_at'
    ]
    prepopulated_fields = {'slug': ('name',)}
    inlines = [RepoValidationInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'summary', 'is_published')
        }),
        ('Repository', {
            'fields': ('repo_url', 'repo_owner', 'repo_name')
        }),
        ('Pricing & Metadata', {
            'fields': ('price_cents', 'license_type', 'change_date_utc'),
            'description': 'Price in cents (e.g., 2999 = $29.99)'
        }),
        ('Categories & Targets', {
            'fields': ('categories_input', 'targets_input'),
            'description': 'Enter values as comma-separated lists. Categories can be any text, targets must be: docker, k8s, github-pages, desktop, or web-embed'
        }),
        ('Media', {
            'fields': ('logo_url', 'featured_screenshot', 'screenshots', 'demo_video_url', 'video_type'),
            'description': 'Logo: App icon/logo. Featured Screenshot: Main image shown on marketplace listing. Screenshots: Up to 2 additional images as JSON array. Video: YouTube/Vimeo/Loom demo URL.'
        }),
        ('GitHub Releases', {
            'fields': ('release_info_display',),
            'classes': ('collapse',),
            'description': 'Latest release information from GitHub'
        }),
        ('Validation', {
            'fields': ('latest_validation_display',),
            'classes': ('collapse',)
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def price_dollars(self, obj):
        """Display price in dollars"""
        if obj.price_cents is None:
            return "Not set"
        return f"${obj.price_cents / 100:.2f}"
    price_dollars.short_description = 'Price (USD)'
    
    def has_release_display(self, obj):
        """Display if app has GitHub release"""
        if obj.has_github_release:
            return format_html('<span style="color: green;">✓ Yes</span>')
        return format_html('<span style="color: gray;">✗ No</span>')
    has_release_display.short_description = 'Has Release'
    
    def release_info_display(self, obj):
        """Display GitHub release information"""
        if not obj.has_github_release:
            return format_html('<p style="color: gray;">No release information available</p>')
        
        html = f"""
        <div style="padding: 10px; background-color: #f8f9fa; border-radius: 5px;">
            <p><strong>Release Name:</strong> {obj.latest_release_name or 'N/A'}</p>
            <p><strong>Tag:</strong> {obj.latest_release_tag or 'N/A'}</p>
            <p><strong>Release URL:</strong> <a href="{obj.latest_release_url}" target="_blank">{obj.latest_release_url}</a></p>
            <p><strong>Download URL:</strong> <a href="{obj.latest_release_zip_url}" target="_blank">ZIP</a></p>
            <p><strong>Last Checked:</strong> {obj.last_release_check.strftime('%Y-%m-%d %H:%M:%S UTC') if obj.last_release_check else 'Never'}</p>
        </div>
        """
        return format_html(html)
    release_info_display.short_description = 'Release Information'
    
    def repo_link(self, obj):
        """Display clickable repository link"""
        if obj.repo_url:
            return format_html(
                '<a href="{}" target="_blank">{}/{}</a>',
                obj.repo_url, obj.repo_owner, obj.repo_name
            )
        return '-'
    repo_link.short_description = 'Repository'
    
    def latest_validation_status(self, obj):
        """Display latest validation status with color"""
        latest = obj.latest_validation
        if not latest:
            return format_html('<span style="color: gray;">No validation</span>')
        
        colors = {
            'pending': 'orange',
            'valid': 'green', 
            'invalid': 'red',
            'error': 'darkred'
        }
        color = colors.get(latest.status, 'gray')
        return format_html(
            '<span style="color: {};">{}</span>',
            color, latest.status.title()
        )
    latest_validation_status.short_description = 'Validation'
    
    def latest_validation_display(self, obj):
        """Display detailed validation information"""
        latest = obj.latest_validation
        if not latest:
            return "No validation runs"
        
        html = f"""
        <div>
            <strong>Status:</strong> {latest.status}<br>
            <strong>Run at:</strong> {latest.run_at}<br>
            <strong>Commit:</strong> {latest.validated_commit_sha or 'N/A'}<br>
            <strong>Detected targets:</strong> {', '.join(latest.detected_targets) if latest.detected_targets else 'None'}<br>
        """
        
        if latest.missing_items:
            html += f"<strong>Missing items:</strong><br>"
            for item in latest.missing_items:
                html += f"• {item}<br>"
        
        html += "</div>"
        return mark_safe(html)
    latest_validation_display.short_description = 'Latest Validation Details'
    
    actions = ['trigger_validation', 'update_releases', 'publish_apps', 'unpublish_apps']
    
    def trigger_validation(self, request, queryset):
        """Trigger validation for selected apps"""
        from .services import GitHubRepoValidationService
        validator = GitHubRepoValidationService()
        
        success_count = 0
        for app in queryset:
            try:
                validator.validate_repository(
                    owner=app.repo_owner,
                    repo=app.repo_name,
                    forge_app=app
                )
                success_count += 1
            except Exception as e:
                self.message_user(request, f"Validation failed for {app.name}: {str(e)}", level='ERROR')
        
        if success_count:
            self.message_user(request, f"Successfully triggered validation for {success_count} apps.")
    
    trigger_validation.short_description = "Trigger repository validation"
    
    def update_releases(self, request, queryset):
        """Update GitHub release information for selected apps"""
        from .github_release_service import GitHubReleaseService
        release_service = GitHubReleaseService()
        
        success_count = 0
        for app in queryset:
            if not app.repo_url:
                self.message_user(request, f"No repository URL for {app.name}", level='WARNING')
                continue
            
            try:
                updated = release_service.update_app_release_info(app, force=True)
                if updated:
                    success_count += 1
            except Exception as e:
                self.message_user(request, f"Release update failed for {app.name}: {str(e)}", level='ERROR')
        
        if success_count:
            self.message_user(request, f"Successfully updated releases for {success_count} apps.")
    
    update_releases.short_description = "Update GitHub releases"
    
    def publish_apps(self, request, queryset):
        """Publish selected apps"""
        updated = queryset.update(is_published=True)
        self.message_user(request, f"Published {updated} apps.")
    
    publish_apps.short_description = "Publish selected apps"
    
    def unpublish_apps(self, request, queryset):
        """Unpublish selected apps"""
        updated = queryset.update(is_published=False)
        self.message_user(request, f"Unpublished {updated} apps.")
    
    unpublish_apps.short_description = "Unpublish selected apps"


@admin.register(RepoValidation)
class RepoValidationAdmin(admin.ModelAdmin):
    list_display = ['forge_app', 'status', 'detected_targets_display', 'run_at']
    list_filter = ['status', 'detected_targets', 'run_at']
    search_fields = ['forge_app__name', 'forge_app__slug']
    readonly_fields = ['id', 'run_at']
    
    fieldsets = (
        ('Validation Run', {
            'fields': ('forge_app', 'status', 'run_at', 'validated_commit_sha')
        }),
        ('Results', {
            'fields': ('detected_targets', 'missing_items')
        }),
        ('System', {
            'fields': ('id',),
            'classes': ('collapse',)
        })
    )
    
    def detected_targets_display(self, obj):
        """Display detected targets as comma-separated string"""
        return ', '.join(obj.detected_targets) if obj.detected_targets else 'None'
    detected_targets_display.short_description = 'Detected Targets'
    
    def has_add_permission(self, request):
        """Validations are created automatically, not manually"""
        return False


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'forge_app', 'amount_dollars', 
        'discount_applied', 'status', 'download_count', 'created_at'
    ]
    list_filter = ['status', 'discount_applied', 'created_at']
    search_fields = [
        'user__username', 'user__email', 'forge_app__name', 
        'stripe_payment_intent_id'
    ]
    readonly_fields = [
        'id', 'amount_dollars', 'stripe_payment_intent_id', 
        'download_count', 'last_downloaded', 'created_at'
    ]
    
    fieldsets = (
        ('Purchase Details', {
            'fields': ('user', 'forge_app', 'status')
        }),
        ('Payment', {
            'fields': ('amount_cents', 'amount_dollars', 'discount_applied', 'stripe_payment_intent_id')
        }),
        ('Download Tracking', {
            'fields': ('download_count', 'last_downloaded'),
            'classes': ('collapse',)
        }),
        ('System', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        })
    )
    
    def amount_dollars(self, obj):
        """Display amount in dollars"""
        return f"${obj.amount_cents / 100:.2f}"
    amount_dollars.short_description = 'Amount (USD)'
    
    def has_add_permission(self, request):
        """Purchases are created through the API, not manually"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Allow status changes only"""
        return True
    
    def get_readonly_fields(self, request, obj=None):
        """Make most fields readonly, allow status changes"""
        if obj:  # Editing existing purchase
            return [
                'id', 'user', 'forge_app', 'amount_cents', 'amount_dollars',
                'discount_applied', 'stripe_payment_intent_id', 'created_at'
            ]
        return self.readonly_fields


@admin.register(Entitlement)
class EntitlementAdmin(admin.ModelAdmin):
    list_display = ['user', 'forge_app', 'purchase_link', 'created_at']
    list_filter = ['created_at', 'forge_app']
    search_fields = ['user__username', 'user__email', 'forge_app__name']
    readonly_fields = ['id', 'created_at']
    
    fieldsets = (
        ('Entitlement', {
            'fields': ('user', 'forge_app', 'purchase')
        }),
        ('System', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        })
    )
    
    def purchase_link(self, obj):
        """Display link to related purchase"""
        if obj.purchase:
            url = reverse('admin:forge_purchase_change', args=[obj.purchase.id])
            return format_html('<a href="{}">{}</a>', url, obj.purchase.id)
        return '-'
    purchase_link.short_description = 'Purchase'
    
    def has_add_permission(self, request):
        """Entitlements are created automatically, not manually"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Entitlements should not be modified manually"""
        return False


# Customize admin site header
admin.site.site_header = "CollabHub Forge Administration"
admin.site.site_title = "Forge Admin"
admin.site.index_title = "Forge Marketplace Management"
