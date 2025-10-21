import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone


class LicenseType(models.TextChoices):
    """License types for Forge apps"""
    BSL_TO_APACHE = 'BSL-1.1→Apache-2.0', 'BSL-1.1→Apache-2.0'
    APACHE_2_0 = 'Apache-2.0', 'Apache-2.0'
    MIT = 'MIT', 'MIT'
    OTHER = 'Other', 'Other'


class ValidationStatus(models.TextChoices):
    """Repository validation status"""
    PENDING = 'pending', 'Pending'
    PASSED = 'passed', 'Passed'
    FAILED = 'failed', 'Failed'


class PurchaseStatus(models.TextChoices):
    """Purchase status"""
    REQUIRES_PAYMENT = 'requires_payment', 'Requires Payment'
    PAID = 'paid', 'Paid'
    FAILED = 'failed', 'Failed'
    REFUNDED = 'refunded', 'Refunded'


class UserProfile(models.Model):
    """User profile to track Labs customer status"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='forge_profile')
    is_labs_customer = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - Labs: {self.is_labs_customer}"

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"


class ForgeApp(models.Model):
    """Buildly Forge marketplace application"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    summary = models.TextField()
    price_cents = models.IntegerField(default=0, validators=[MinValueValidator(0)], 
                                    help_text="Price in cents (e.g., 2999 for $29.99, 0 for free)")
    repo_url = models.URLField(max_length=500)
    repo_owner = models.CharField(max_length=100)
    repo_name = models.CharField(max_length=100)
    license_type = models.CharField(max_length=50, choices=LicenseType.choices)
    change_date_utc = models.DateTimeField(null=True, blank=True)
    categories = models.JSONField(default=list, blank=True)
    targets = models.JSONField(default=list, blank=True)
    logo_url = models.URLField(max_length=500, null=True, blank=True)
    screenshots = models.JSONField(default=list, blank=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.slug})"

    @property
    def price_dollars(self):
        """Convert price from cents to dollars"""
        if self.price_cents is None:
            return 0.0
        return self.price_cents / 100

    @property
    def latest_validation(self):
        """Get the latest validation for this app"""
        return self.validations.order_by('-run_at').first()

    class Meta:
        verbose_name = "Forge App"
        verbose_name_plural = "Forge Apps"
        ordering = ['-created_at']


class RepoValidation(models.Model):
    """Repository validation results"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    forge_app = models.ForeignKey(ForgeApp, on_delete=models.CASCADE, related_name='validations')
    status = models.CharField(max_length=20, choices=ValidationStatus.choices, default=ValidationStatus.PENDING)
    missing_items = models.JSONField(default=list, blank=True)
    detected_targets = models.JSONField(default=list, blank=True)
    validated_commit_sha = models.CharField(max_length=40, null=True, blank=True)
    run_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.forge_app.name} - {self.status} ({self.run_at})"

    class Meta:
        verbose_name = "Repository Validation"
        verbose_name_plural = "Repository Validations"
        ordering = ['-run_at']


class Purchase(models.Model):
    """User purchase of a Forge app"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forge_purchases')
    forge_app = models.ForeignKey(ForgeApp, on_delete=models.CASCADE, related_name='purchases')
    stripe_payment_intent_id = models.CharField(max_length=200, blank=True)
    stripe_session_id = models.CharField(max_length=200, blank=True)
    amount_cents = models.IntegerField(validators=[MinValueValidator(0)])
    discount_applied = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=PurchaseStatus.choices, default=PurchaseStatus.REQUIRES_PAYMENT)
    license_document = models.FileField(upload_to='licenses/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.forge_app.name} - {self.status}"

    @property
    def amount_dollars(self):
        """Convert amount from cents to dollars"""
        if self.amount_cents is None:
            return 0.0
        return self.amount_cents / 100

    class Meta:
        verbose_name = "Purchase"
        verbose_name_plural = "Purchases"
        ordering = ['-created_at']


class Entitlement(models.Model):
    """User entitlement to a Forge app"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forge_entitlements')
    forge_app = models.ForeignKey(ForgeApp, on_delete=models.CASCADE, related_name='entitlements')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} owns {self.forge_app.name}"

    class Meta:
        verbose_name = "Entitlement"
        verbose_name_plural = "Entitlements"
        unique_together = [['user', 'forge_app']]
        ordering = ['-created_at']
