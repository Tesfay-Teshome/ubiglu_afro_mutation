from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Project, DigitalAsset, Category, Fabric, Payment, ColorPalette
from allauth.account.forms import SignupForm, LoginForm
import json

class CustomUserCreationForm(UserCreationForm):
    """Custom form for user registration with additional fields."""
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your first name'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your last name'}))
    terms_agreement = forms.BooleanField(
        required=True,
        label='I agree to the Terms of Service and Privacy Policy',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    profile_image = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'profile_image')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    terms_accepted = forms.BooleanField(
        required=True,
        error_messages={'required': 'You must accept the Terms of Service and Privacy Policy'}
    )

    def save(self, request):
        user = super().save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return user

class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['login'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Email'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})

class UserProfileForm(forms.ModelForm):
    """Form for editing user profile information."""
    profile_image = forms.ImageField(required=False)

    class Meta:
        model = UserProfile
        fields = ['profile_image', 'bio', 'website', 'location']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'website': forms.TextInput(attrs={'placeholder': 'Enter your website'}),
            'location': forms.TextInput(attrs={'placeholder': 'Enter your location'}),
        }

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'category', 'price', 'description', 'status', 'visibility', 'tags','image']  # Include additional_info if it exists in the model
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'price': forms.NumberInput(attrs={'min': 0, 'step': 0.01}),
        }

    def clean_price(self):
        """Validate price."""
        price = self.cleaned_data.get('price')
        if price is None:
            raise forms.ValidationError("Price is required.")
        if price < 0:
            raise forms.ValidationError("Price cannot be negative.")
        return price

class DigitalAssetForm(forms.ModelForm):
    """Form for uploading and editing digital assets."""
    class Meta:
        model = DigitalAsset
        fields = ['title', 'description', 'file', 'category', 'tags']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'tags': forms.TextInput(attrs={'placeholder': 'Enter tags separated by commas'})
        }

    def clean_file(self):
        """Validate file size and type."""
        file = self.cleaned_data.get('file')
        if file:
            if file.size > 10 * 1024 * 1024:  # 10MB limit
                raise forms.ValidationError('File size cannot exceed 10MB.')
            
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf']
            if hasattr(file, 'content_type') and file.content_type not in allowed_types:
                raise forms.ValidationError('Unsupported file type.')
        return file

class CategoryForm(forms.ModelForm):
    """Form for creating and editing categories."""
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3})
        }

class FabricForm(forms.ModelForm):
    """Form for creating and editing fabric entries."""
    class Meta:
        model = Fabric
        fields = ['name', 'description', 'image', 'category', 'price']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'price': forms.NumberInput(attrs={'step': '0.01'})
        }

class PaymentForm(forms.ModelForm):
    """Form for processing payments."""
    class Meta:
        model = Payment
        fields = ['amount', 'payment_method']
        widgets = {
            'amount': forms.NumberInput(attrs={'step': '0.01'})
        }

class ColorPaletteForm(forms.ModelForm):
    """Form for creating and editing color palettes."""
    class Meta:
        model = ColorPalette
        fields = ['name', 'description', 'colors']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'colors': forms.Textarea(attrs={'rows': 4, 'class': 'json-editor'})
        }

    def clean_colors(self):
        """Validate colors JSON data."""
        data = self.cleaned_data['colors']
        if data:
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                raise forms.ValidationError('Invalid JSON format')
        return None

class UserSettingsForm(forms.ModelForm):
    """Form for updating user settings."""
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your first name'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your last name'}))
    password = forms.CharField(required=False, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter new password (leave blank to keep current)'}))

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password']

class ContactForm(forms.Form):
    """Form for contact page."""
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Name'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Email'
        })
    )
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Subject'
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Your Message',
            'rows': 5
        })
    )
    captcha = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Please solve: 2 + 3 = ?'
        })
    )

    def clean_captcha(self):
        """Validate captcha answer."""
        answer = self.cleaned_data.get('captcha')
        if answer != '5':
            raise forms.ValidationError('Incorrect captcha answer. Please try again.')
        return answer