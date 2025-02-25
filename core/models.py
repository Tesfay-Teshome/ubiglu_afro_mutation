from django.contrib.auth.models import User
from django.db import models
from django.core.validators import RegexValidator
from cryptography.fernet import Fernet
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone
import os
from uuid import uuid4

# Encryption Setup
encryption_key = settings.ENCRYPTION_KEY
cipher = Fernet(encryption_key)

# Custom upload function for user avatar
def user_avatar_upload_to(instance, filename):
    ext = filename.split('.')[-1]
    return f'user_profile_images/{uuid4()}.{ext}'  # Save images directly in user_profile_images/

# User Profile
class UserProfile(models.Model):
    """Extended user profile model."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(
        upload_to='user_profile_images/%Y/%m/%d/',
        blank=True,
        null=True,
        default='user_profile_images/default.jpg'
    )
    bio = models.TextField(max_length=500, blank=True, null=True)
    website = models.URLField(max_length=200, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    skills = models.CharField(max_length=200, blank=True, null=True, help_text="Comma-separated list of skills")
    interests = models.CharField(max_length=200, blank=True, null=True, help_text="Comma-separated list of interests")
    social_github = models.URLField(max_length=200, blank=True, null=True)
    social_twitter = models.URLField(max_length=200, blank=True, null=True)
    social_linkedin = models.URLField(max_length=200, blank=True, null=True)
    social_instagram = models.URLField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')],
        blank=True,
        null=True
    )
    street_address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    body_measurements = models.JSONField(blank=True, null=True)  # Store self-measurement data

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def get_absolute_url(self):
        return reverse('core:profile')

    @property
    def skills_list(self):
        return [skill.strip() for skill in self.skills.split(',') if skill.strip()]

    @property
    def interests_list(self):
        return [interest.strip() for interest in self.interests.split(',') if interest.strip()]

    def set_phone_number(self, raw_phone_number):
        self.phone_number = cipher.encrypt(raw_phone_number.encode()).decode()

    def get_phone_number(self):
        return cipher.decrypt(self.phone_number.encode()).decode() if self.phone_number else None
    
class PasswordResetRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Password reset request for {self.email} at {self.created_at}"

# Profile
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(
        upload_to='user_profile_images/%Y/%m/%d/',
        blank=True,
        null=True,
        default='user_profile_images/default.jpg'
    )

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

# Category
class Category(models.Model):
    """Category model for projects and assets."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

# Project
class Project(models.Model):
    """Enhanced Project Model with Earnings and Sales Tracking."""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_sales = models.IntegerField(default=0)  # Tracks number of sales
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)  # Tracks earnings
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('completed', 'Completed'),
    ], default='draft')
    image = models.ImageField(upload_to='project_images/', blank=True)
    design_data = models.JSONField(null=True, blank=True)  # Stores design details
    measurements = models.JSONField(null=True, blank=True)  # Stores measurements
    visibility = models.BooleanField(default=True)  # Visibility toggle
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('core:project_detail', kwargs={'pk': self.pk})

    def update_sales_and_earnings(self, price):
        """Update total sales and earnings for the project."""
        self.total_sales += 1
        self.total_earnings += price
        self.save()

    @property
    def tags_list(self):
        """Converts comma-separated tags into a list."""
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]

# Digital Asset
class DigitalAsset(models.Model):
    """Digital asset model for user uploads."""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    file = models.FileField(upload_to='assets/')
    file_type = models.CharField(max_length=50, editable=False, default='unknown')
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated list of tags")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    file_format = models.CharField(max_length=10, choices=[
        ('OBJ', 'OBJ'),
        ('FBX', 'FBX'),
        ('GLB', 'GLB'),
        ('GLTF', 'GLTF'),
    ], blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Set file type based on extension
        if self.file:
            self.file_type = self.file.name.split('.')[-1].lower()
        super().save(*args, **kwargs)

    @property
    def tags_list(self):
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
    
# 3D Garment
class Garment3D(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    digital_asset = models.ForeignKey(DigitalAsset, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title


# Fabric
class Fabric(models.Model):
    """Model for fabric designs."""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='fabrics/', blank=True, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='fabrics', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    color = models.CharField(max_length=50)
    texture = models.CharField(max_length=100)
    thread_density = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    elasticity = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sheen = models.CharField(max_length=50, blank=True, null=True)
    scanned_data = models.JSONField(blank=True, null=True)  # Data from scanning technologies
    pbr_textures = models.JSONField(blank=True, null=True)  # For 3D visualization in Babylon.js
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

# Color Palette
class ColorPalette(models.Model):
    """Color palette model for user color palettes."""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    colors = models.JSONField()  # Stores HEX, RGB, and CMYK values as JSON
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='color_palettes')

    def __str__(self):
        return f"{self.name} (Created by {self.user.username})"

# Payment
class Payment(models.Model):
    """Payment model for user payments."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=255, unique=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50)  # PayPal, Stripe, Flutterwave, etc.
    status = models.CharField(max_length=50, default='Pending')

    def __str__(self):
        return f"Payment {self.transaction_id} by {self.user.username}"

# Order Tracking
class OrderTracking(models.Model):
    """Order tracking model for user orders."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=50, default='Received')  # Status of the order
    shipping_details = models.JSONField(blank=True, null=True)
    progress = models.FloatField(default=0.0)  # Progress bar percentage

    def __str__(self):
        return f"Order {self.id} - Status: {self.status}"

# Design
class Design(models.Model):
    """Model for storing user clothing designs."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    measurements = models.JSONField(default=dict)
    style_options = models.JSONField(default=dict)
    thumbnail = models.TextField()  # Base64 encoded image
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} by {self.user.username}"

    class Meta:
        ordering = ['-created_at']

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
