from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, Http404, HttpResponse
from django.views.decorators.http import require_POST
from rest_framework import viewsets, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Project, UserProfile, DigitalAsset, Payment, Category, Fabric, Design, Profile
from .forms import ProjectForm, UserProfileForm, CustomUserCreationForm, PaymentForm, ContactForm, DigitalAssetForm, ColorPaletteForm, UserSettingsForm
import stripe
import json
from django.shortcuts import get_object_or_404
import logging

stripe.api_key = 'YOUR_STRIPE_SECRET_KEY'  # Replace with your actual Stripe key

# Set up logging
logger = logging.getLogger(__name__)

# Basic Views
def home(request):
    """Home page view."""
    latest_projects = Project.objects.filter(status='published').order_by('-created_at')[:3]
    categories = Category.objects.all()
    return render(request, 'core/home.html', {'latest_projects': latest_projects, 'categories': categories})

def about(request):
    """About page view."""
    return render(request, 'core/about.html')

def contact(request):
    """Contact page view."""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you for your message! We will get back to you soon.')
            return redirect('core:contact')
    else:
        form = ContactForm()
    
    return render(request, 'core/contact.html', {
        'form': form
    })

@login_required
def dashboard(request):
    """User dashboard view."""
    total_projects = Project.objects.filter(owner=request.user).count()
    user_projects = Project.objects.filter(owner=request.user).order_by('-created_at')[:5]
    user_assets = DigitalAsset.objects.filter(user=request.user)
    user_payments = Payment.objects.filter(user=request.user)
    total_earnings = sum(project.price for project in Project.objects.filter(owner=request.user))
    total_sales = Payment.objects.filter(user=request.user).count()
    context = {
        'projects': user_projects,
        'total_projects': total_projects,
        'assets': user_assets,
        'payments': user_payments,
        'total_earnings': total_earnings,
        'total_sales': total_sales
    }
    return render(request, 'core/dashboard.html', context)

@login_required
def profile(request):
    """User profile view."""
    return render(request, 'core/profile.html', {
        'user': request.user
    })

@login_required
def user_settings(request):
    """User settings view."""
    return render(request, 'core/user_settings.html')

@login_required
def edit_profile(request):
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('core:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'core/edit_profile.html', {'form': form})

@login_required
def delete_account(request):
    """Delete user account view."""
    if request.method == 'POST':
        password = request.POST.get('password')
        user = request.user
        
        if user.check_password(password):
            user.delete()
            messages.success(request, 'Your account has been deleted.')
            return redirect('core:home')
        else:
            messages.error(request, 'Incorrect password. Please try again.')
    
    return render(request, 'core/delete_account.html')

# Authentication Views
def login_view(request):
    """Custom login view."""
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = User.objects.filter(username=username).first()
        if user is None:
            messages.error(request, 'Username does not exist. Please try again.')
        else:
            # Check if the user has a profile
            if not hasattr(user, 'profile'):
                UserProfile.objects.create(user=user)  # Create a profile if it doesn't exist
                messages.info(request, 'Profile created for this user.')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', 'core:dashboard')
                return redirect(next_url)
            else:
                messages.error(request, 'Incorrect password. Please try again.')
                form = AuthenticationForm()
                return render(request, 'core/auth/login.html', {'form': form})
        
        form = AuthenticationForm()  # Recreate the form to return it to the template
        return render(request, 'core/auth/login.html', {'form': form})

    else:
        form = AuthenticationForm()
    
    return render(request, 'core/auth/login.html', {'form': form})

def logout_view(request):
    """Logout view."""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('core:home')

def register(request):
    """Handle user registration with profile image upload."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)  # Include request.FILES
        if form.is_valid():
            user = form.save()
            # Create a UserProfile instance for the new user
            UserProfile.objects.create(user=user, profile_image=request.FILES.get('profile_image'))  # Save the profile image correctly to the right directory
            messages.success(request, 'Registration successful. You can now log in.')
            logger.info('User registered successfully: %s', user.username)
            return redirect('core:login')
        else:
            logger.error('Registration form is invalid: %s', form.errors)
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'core/auth/register.html', {'form': form})  # Ensure this points to the correct template location

# Project Views
def project_list(request):
    """Display list of projects with pagination."""
    projects_list = Project.objects.filter(status='published').order_by('-created_at')
    paginator = Paginator(projects_list, 9)  # Show 9 projects per page
    
    page = request.GET.get('page')
    try:
        projects = paginator.page(page)
    except PageNotAnInteger:
        projects = paginator.page(1)
    except EmptyPage:
        projects = paginator.page(paginator.num_pages)
    
    return render(request, 'core/projects.html', {'projects': projects})

@login_required
def project_create(request):
    """Create a new project."""
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            
            # Debugging output to check form data
            print(f"Form data: {request.POST}")
            
            # Log the submitted category value
            selected_category = request.POST.get('category')
            print(f"Submitted category: {selected_category}")
            
            # Save design data and measurements
            design_data = request.POST.get('design_data')
            measurements = request.POST.get('measurements')
            
            if design_data:
                try:
                    project.design_data = json.loads(design_data)
                except json.JSONDecodeError:
                    messages.warning(request, 'Invalid design data format')
            
            if measurements:
                try:
                    project.measurements = json.loads(measurements)
                except json.JSONDecodeError:
                    messages.warning(request, 'Invalid measurements format')
            
            project.status = 'published'  # Set project status to published
            
            project.save()
            print(f"Project saved: {project.title}")  # Debugging statement
            
            # Save fabric design if provided
            if 'fabric_design' in request.FILES:
                fabric = Fabric.objects.create(
                    name=f"Fabric for {project.title}",
                    description="Custom fabric design",
                    image=request.FILES['fabric_design'],
                    project=project
                )
            
            messages.success(request, 'Project created successfully!')
            return redirect('core:project_detail', pk=project.pk)
        else:
            print(f"Form errors: {form.errors}")  # Debugging statement
    else:
        form = ProjectForm()
    
    # Get available fabrics for the designer
    fabrics = Fabric.objects.all()
    categories = Category.objects.all()  # Retrieve categories
    print(f"Categories: {[cat.name for cat in categories]}")  # Debugging output
    return render(request, 'core/project_form.html', {
        'form': form,
        'title': 'Create Project',
        'fabrics': fabrics,
        'categories': categories  # Pass categories to the template
    })

def project_detail(request, pk):
    """Display project details."""
    project = get_object_or_404(Project, pk=pk)
    return render(request, 'core/project_detail.html', {'project': project})

@login_required
def project_edit(request, pk):
    """Edit an existing project."""
    project = get_object_or_404(Project, pk=pk)
    if project.owner != request.user:
        messages.error(request, 'You do not have permission to edit this project.')
        return redirect('core:project_detail', pk=pk)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully!')
            return redirect('core:project_detail', pk=pk)
    else:
        form = ProjectForm(instance=project)
    return render(request, 'core/project_form.html', {'form': form, 'title': 'Edit Project'})

@login_required
def project_delete(request, pk):
    """Delete a project."""
    project = get_object_or_404(Project, pk=pk)
    if project.owner != request.user:
        messages.error(request, 'You do not have permission to delete this project.')
        return redirect('core:project_detail', pk=pk)
    
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project deleted successfully!')
        return redirect('core:project_list')
    return render(request, 'core/project_confirm_delete.html', {'project': project})

# Payment Views
@login_required
def create_payment(request, project_id):
    """Create a payment session for a project."""
    project = get_object_or_404(Project, id=project_id)
    
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': project.title,
                    },
                    'unit_amount': int(project.price * 100),  # Convert to cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri('/payment/success/'),
            cancel_url=request.build_absolute_uri('/payment/cancel/'),
        )
        return JsonResponse({'sessionId': session.id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def payment_success(request):
    """Handle successful payment."""
    messages.success(request, 'Payment successful! Thank you for your purchase.')
    return redirect('core:dashboard')

def payment_cancel(request):
    """Handle cancelled payment."""
    messages.warning(request, 'Payment cancelled.')
    return redirect('core:dashboard')

# Product Views
def products(request):
    """View function for the products page."""
    return render(request, 'core/products.html')

# Static Pages
def privacy_policy(request):
    """View for privacy policy page."""
    return render(request, 'core/static/privacy_policy.html')

def terms(request):
    """View for terms of service page."""
    return render(request, 'core/static/terms.html')

def faq(request):
    """View for FAQ page."""
    return render(request, 'core/static/faq.html')

def designer(request):
    """View for designer page."""
    fabrics = Fabric.objects.all()
    return render(request, 'core/designer.html', {
        'fabrics': fabrics
    })

# API Views
class DigitalAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = DigitalAsset
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class DigitalAssetViewSet(viewsets.ModelViewSet):
    """ViewSet for digital assets API."""
    queryset = DigitalAsset.objects.all()
    serializer_class = DigitalAssetSerializer

    @action(detail=True, methods=['post'])
    def apply_colorway(self, request, pk=None):
        """Apply a colorway to a digital asset."""
        asset = self.get_object()
        # Add your colorway application logic here
        return Response({'message': 'Colorway applied successfully'})

class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for payments API."""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """Process a payment."""
        payment = self.get_object()
        try:
            # Add your payment processing logic here
            return Response({'message': 'Payment processed successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=400)

@require_POST
def save_design(request):
    """API endpoint to save a design."""
    try:
        data = json.loads(request.body)
        # Add your design saving logic here
        return JsonResponse({'status': 'success'})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def test_view(request):
    return HttpResponse('Test view works!')

# Error Handlers
def handler404(request, exception):
    """Custom 404 error handler."""
    return render(request, 'core/errors/404.html', status=404)

def handler500(request):
    """Custom 500 error handler."""
    return render(request, 'core/errors/500.html', status=500)

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ... your other url patterns
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
