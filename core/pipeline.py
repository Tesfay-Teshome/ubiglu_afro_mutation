from .models import UserProfile

def create_user_profile(backend, user, response, *args, **kwargs):
    """Create user profile for social auth users if it doesn't exist."""
    if not hasattr(user, 'userprofile'):
        UserProfile.objects.create(
            user=user,
            # Set default values or extract from social auth response
            bio=f"Hi, I'm {user.get_full_name() or user.username}!",
            # Add any other default fields here
        )
