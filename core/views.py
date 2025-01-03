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
from django.contrib.auth.views import PasswordResetView
from .models import PasswordResetRequest
from django.core.mail import send_mail
from .models import Garment3D
from django.utils.translation import gettext_lazy as _
from .models import Project, UserProfile, DigitalAsset, Payment, Category, Fabric, Design, Profile
from .forms import ProjectForm, UserProfileForm, CustomUserCreationForm, PaymentForm, ContactForm, DigitalAssetForm, ColorPaletteForm, UserSettingsForm
import stripe
from django.conf import settings
import json
from django.shortcuts import get_object_or_404
import logging

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY  # Replace with your actual Stripe key

# Set up logging
logger = logging.getLogger(__name__)

# Basic Views
def home(request):
    """Home page view."""
    latest_projects = Project.objects.filter(status='published').order_by('-created_at')[:5]
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
def  dashboard(request):
    """User dashboard view."""
    total_projects = Project.objects.filter(owner=request.user).count()
    
    # Get all projects owned by the user
    projects = Project.objects.filter(owner=request.user).order_by('-created_at')  # Removed the limit to show all projects
    
    # Get digital assets owned by the user
    assets = DigitalAsset.objects.filter(user=request.user)
    
    # Get payments made by the user
    payments = Payment.objects.filter(user=request.user)
    
    # Calculate total earnings from all projects owned by the user
    total_earnings = sum(project.total_earnings for project in projects)  # Use the total_earnings field from the Project model
    
    # Calculate total sales from all payments made by the user
    total_sales = sum(project.total_sales for project in projects)  # Use the total_sales field from the Project model

    # Prepare context for rendering
    context = {
        'projects': projects,
        'total_projects': total_projects,
        'assets': assets,
        'payments': payments,
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
            clear_image = form.cleaned_data.get('clear_image')

            # Clear the previous image if the checkbox is checked
            if clear_image:
                profile.profile_image.delete()  # Delete the old image from storage
                profile.profile_image = None  # Clear the field

            # Save the new profile image if uploaded
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

class CustomPasswordResetView(PasswordResetView):
    def form_valid(self, form):
        response = super().form_valid(form)
        user_email = form.cleaned_data['email']
        user = User.objects.get(email=user_email)
        PasswordResetRequest.objects.create(user=user, email=user_email)
        return response

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
# views.py
def project_create(request):
    """Create a new project."""
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user

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

            project.status = 'published' # Set project status to published
            project.save()

            # Save fabric design if provided
            if 'fabric_design' in request.FILES:
                fabric = Fabric.objects.create(
                    name=f"Fabric for {project.title}",
                    description="Custom fabric design",
                    image=request.FILES['fabric_design'],
                    project=project
                )

            messages.success(request, 'Project created successfully!')
            return redirect('core:project_detail', project_id=project.id)
        else:
            messages.error(request, 'Please correct the errors below.')

    else:
        form = ProjectForm()

    # Get available fabrics for the designer
    fabrics = Fabric.objects.all()
    categories = Category.objects.all() # Retrieve categories

    return render(request, 'core/create_project.html', {
        'form': form,
        'title': 'Create Project',
        'fabrics': fabrics,
        'categories': categories # Pass categories to the template
    })

def project_detail(request, project_id):
    """Display project details."""
    project = get_object_or_404(Project, id=project_id)
    form = ProjectForm(instance=project)  # Ensure you are passing the project instance
    print(form.errors)  # This will show any validation errors
    return render(request, 'core/project_detail.html', {'form': form, 'project': project})

class FabricSerializer(serializers.ModelSerializer):
    class Meta:
      model = Fabric
      fields = '__all__'

class FabricViewSet(viewsets.ModelViewSet):
    """ViewSet for fabrics API."""
    queryset = Fabric.objects.all()
    serializer_class = FabricSerializer

@login_required
def edit_project(request, project_id):
    """Edit an existing project."""
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully!')
            return redirect('core:project_detail', project_id=project.id)  # Redirect after saving
        else:
            messages.error(request, 'There was an error updating the project. Please check the form.')
    else:
        form = ProjectForm(instance=project)  # Pre-fill the form with existing project data

    return render(request, 'core/edit_project.html', {'form': form, 'project': project})
@login_required
def project_delete(request, project_id):
    """Delete a project."""
    project = get_object_or_404(Project, id=project_id)
    if project.owner != request.user:
        messages.error(request, 'You do not have permission to delete this project.')
        return redirect('core:project_detail', pk=pk)
    
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project deleted successfully!')
        return redirect('core:project_list')
    return render(request, 'core/project_confirm_delete.html', {'project': project})

@login_required
def create_payment(request, project_id):
    """Create a Stripe payment session for a project."""
    project = get_object_or_404(Project, id=project_id)
    request.session['project_id'] = project.id

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': project.title,
                    },
                    'unit_amount': int(project.price * 100),  # Convert dollars to cents
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
    

@login_required
def payment_success(request):
    """Handle successful payment."""
    # Retrieve the project ID from the session
    project_id = request.session.get('project_id')

    if project_id is None:
        messages.error(request, 'No project ID found in session.')
        return redirect('core:dashboard')

    project = get_object_or_404(Project, id=project_id)

    # Increment the sales count and update total earnings
    project.total_sales += 1
    project.total_earnings += project.price  # Add the price to total earnings
    project.save()

    messages.success(request, 'Payment successful! Thank you for your purchase.')
    return redirect('core:project_detail', project_id=project.id)

@login_required
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
