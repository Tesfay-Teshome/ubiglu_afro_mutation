from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import (
    UserProfile, Category, Project, Payment, 
    Fabric, DigitalAsset, ColorPalette, OrderTracking
)

class UserProfileInline(admin.StackedInline):
    """Inline admin for user profiles."""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'

class CustomUserAdmin(UserAdmin):
    """Custom admin for User model with profile inline."""
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)

# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin interface for Category model."""
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'category', 'status', 'created_at', 'updated_at')  
    search_fields = ('title', 'description')

admin.site.register(Project, ProjectAdmin)

@admin.register(DigitalAsset)
class DigitalAssetAdmin(admin.ModelAdmin):
    """Admin interface for DigitalAsset model."""
    list_display = ('title', 'user', 'category', 'file_type', 'created_at')
    list_filter = ('category', 'created_at', 'file_type')
    search_fields = ('title', 'description', 'user__username')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at', 'file_type')

@admin.register(Fabric)
class FabricAdmin(admin.ModelAdmin):
    """Admin interface for Fabric model."""
    list_display = ('name', 'category', 'price')
    list_filter = ('category',)
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'transaction_id', 'payment_date', 'status']
    list_filter = ['status', 'payment_date', 'payment_method']
    search_fields = ['user__username', 'transaction_id']

@admin.register(ColorPalette)
class ColorPaletteAdmin(admin.ModelAdmin):
    list_display = ['name', 'user']
    search_fields = ['name', 'description', 'user__username']

@admin.register(OrderTracking)
class OrderTrackingAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'progress']
    list_filter = ['status']
    search_fields = ['user__username']
