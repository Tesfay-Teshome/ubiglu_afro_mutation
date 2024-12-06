from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from allauth.account.signals import user_signed_up
from allauth.socialaccount.signals import social_account_added
from .models import UserProfile

@receiver(user_signed_up)
def create_user_profile(sender, request, user, **kwargs):
    """Create UserProfile when a new user signs up"""
    UserProfile.objects.get_or_create(user=user)

@receiver(social_account_added)
def update_user_profile(sender, request, sociallogin, **kwargs):
    """Update UserProfile when a social account is added"""
    user = sociallogin.user
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    # Update profile with social account data if available
    if sociallogin.account.provider == 'google':
        data = sociallogin.account.extra_data
        if not user.first_name and 'given_name' in data:
            user.first_name = data['given_name']
        if not user.last_name and 'family_name' in data:
            user.last_name = data['family_name']
        if 'picture' in data and not profile.avatar:
            profile.avatar = data['picture']
        user.save()
        profile.save()
