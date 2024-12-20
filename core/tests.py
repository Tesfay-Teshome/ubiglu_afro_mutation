from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import UserProfile
from django.core.files.uploadedfile import SimpleUploadedFile

class UserProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123', email='test@example.com')
        self.profile = UserProfile.objects.create(user=self.user)

    def test_user_profile_creation(self):
        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())

class RegistrationTests(TestCase):
    def test_user_registration_with_profile_image(self):
        # Sample image file
        image = SimpleUploadedFile(name='test_image.jpg', content=b'file_content', content_type='image/jpeg')
        response = self.client.post(reverse('core:register'), {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'password123',
            'password2': 'password123',
            'profile_image': image,
        })

        print(response.content)  # Print response content for debugging
        print(response.context)  # Print response context for debugging
        self.assertEqual(response.status_code, 302)  # Check for redirect after successful registration
        self.assertTrue(User.objects.filter(username='testuser').exists())  # Check if user is created
        self.assertTrue(UserProfile.objects.filter(user__username='testuser').exists())  # Check if UserProfile is created

class ViewTests(TestCase):
    def test_home_view(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')

    def test_about_view(self):
        response = self.client.get(reverse('core:about'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/about.html')

    def test_contact_view(self):
        response = self.client.get(reverse('core:contact'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/contact.html')

    def test_user_settings_view(self):
        self.client.login(username='testuser', password='password123')  # Log in the test user
        response = self.client.get(reverse('core:user_settings'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/user_settings.html')
