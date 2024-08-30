from django.contrib.auth.models import AbstractUser
from django.db import models
from punchlist.models import Product  # Import the Product model from Punchlist

class CustomUser(AbstractUser):
    is_product_owner = models.BooleanField(default=False)
    is_labs_user_owner = models.BooleanField(default=False)
    # Add any other fields common to all users
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',  # Change related_name to avoid clash
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',  # Change related_name to avoid clash
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

class ProductOwnerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='product_owner_profile')
    organization_name = models.CharField(max_length=255)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    # Add any other fields related to the Product Owner

    def __str__(self):
        return self.user.username
