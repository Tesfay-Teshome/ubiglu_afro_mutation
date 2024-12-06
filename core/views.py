from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import serializers, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import (
    UserProfile, Category, Project, Payment,
    Fabric, DigitalAsset, ColorPalette, OrderTracking
)
from .forms import (
    CustomUserCreationForm, UserProfileForm, ProjectForm,
    PaymentForm, ContactForm, DigitalAssetForm, ColorPaletteForm
)
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

# Basic Views
def home(request):
    """Home page view."""
    projects = Project.objects.filter(status='Completed')[:6]
    categories = Category.objects.all()
    return render(request, 'core/home.html', {
        'projects': projects,
        'categories': categories
    })

@login_required
def dashboard(request):
    """User dashboard view."""
    user_projects = Project.objects.filter(owner=request.user)
    user_assets = DigitalAsset.objects.filter(user=request.user)
    user_payments = Payment.objects.filter(user=request.user)
    context = {
        'projects': user_projects,
        'assets': user_assets,
        'payments': user_payments
    }
    return render(request, 'core/dashboard.html', context)

# Authentication Views
def register(request):
    """User registration view."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create associated profile
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to Ubiglu Afro Mutation.')
            return redirect('core:dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# Profile Views
@login_required
def profile_view(request):
    """Handle user profile view and updates"""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)

    context = {
        'form': form,
        'profile': profile,
        'social_accounts': request.user.socialaccount_set.all()
    }
    return render(request, 'core/profile.html', context)

@login_required
def profile_settings(request):
    """Handle user account settings"""
    return render(request, 'core/profile_settings.html', {
        'user': request.user,
        'social_accounts': request.user.socialaccount_set.all()
    })

@login_required
def edit_profile(request):
    """Edit user profile view."""
    profile = request.user.userprofile
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('core:profile')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'core/edit_profile.html', {'form': form})

@login_required
def delete_account(request):
    """Handle account deletion"""
    if request.method == 'POST':
        user = request.user
        # Logout before deleting
        logout(request)
        # Delete user account
        user.delete()
        messages.success(request, 'Your account has been successfully deleted.')
        return redirect('home')
    return redirect('profile_settings')

def custom_logout(request):
    """Custom logout view with success message"""
    messages.success(request, 'You have been successfully logged out.')
    return logout(request)

# Project Views
class ProjectListView(LoginRequiredMixin, ListView):
    """View for listing all projects."""
    model = Project
    template_name = 'core/project_list.html'
    context_object_name = 'projects'
    paginate_by = 12
    
    def get_queryset(self):
        """Filter projects to show only user's projects."""
        queryset = super().get_queryset()
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__name=category)
        return queryset

class ProjectDetailView(LoginRequiredMixin, DetailView):
    """View for showing project details."""
    model = Project
    template_name = 'core/project_detail.html'

class ProjectCreateView(LoginRequiredMixin, CreateView):
    """View for creating a new project."""
    model = Project
    form_class = ProjectForm
    template_name = 'core/project_form.html'
    success_url = reverse_lazy('core:dashboard')
    
    def form_valid(self, form):
        """Set the owner of the project to the current user."""
        form.instance.owner = self.request.user
        return super().form_valid(form)

class ProjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """View for updating an existing project."""
    model = Project
    form_class = ProjectForm
    template_name = 'core/project_form.html'
    
    def test_func(self):
        """Check if current user is the owner of the project."""
        project = self.get_object()
        return self.request.user in project.users.all()

class ProjectDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """View for deleting a project."""
    model = Project
    success_url = reverse_lazy('core:dashboard')
    template_name = 'core/project_confirm_delete.html'
    
    def test_func(self):
        """Check if current user is the owner of the project."""
        project = self.get_object()
        return self.request.user in project.users.all()

# Payment Views
@login_required
def create_payment(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=int(project.price * 100),
                currency='usd',
                metadata={'project_id': project.id}
            )
            return JsonResponse({
                'clientSecret': payment_intent.client_secret
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=403)
    return render(request, 'core/payment.html', {'project': project})

@login_required
def payment_success(request):
    return render(request, 'core/payment_success.html')

@login_required
def payment_cancel(request):
    return render(request, 'core/payment_cancel.html')

# Contact Views
def contact(request):
    """Contact page view."""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Process the form data
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            
            # Send email
            send_mail(
                f'Contact Form: {subject}',
                f'From: {name} <{email}>\n\n{message}',
                email,
                ['support@ubigluafro.com'],
                fail_silently=False,
            )
            
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('core:contact')
    else:
        form = ContactForm()
    
    return render(request, 'core/contact.html', {'form': form})

def privacy_policy(request):
    """Privacy policy page view."""
    return render(request, 'core/privacy_policy.html')

def terms(request):
    """Terms of service page view."""
    return render(request, 'core/terms.html')

def faq(request):
    """FAQ page view."""
    return render(request, 'core/faq.html')

# API Views
class DigitalAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = DigitalAsset
        fields = '__all__'

class ColorPaletteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColorPalette
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class DigitalAssetViewSet(viewsets.ModelViewSet):
    queryset = DigitalAsset.objects.all()
    serializer_class = DigitalAssetSerializer

    @action(detail=True, methods=['post'])
    def apply_colorway(self, request, pk=None):
        asset = self.get_object()
        asset.applied_colors = request.data.get('colors', {})
        asset.save()
        return Response({'message': 'Colorway applied successfully'})

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    @action(detail=False, methods=['post'])
    def create_payment_intent(self, request):
        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=int(request.data['amount'] * 100),
                currency='usd'
            )
            return Response({'clientSecret': payment_intent.client_secret})
        except Exception as e:
            return Response({'error': str(e)}, status=400)

# Error Views
def handler404(request, exception):
    return render(request, 'core/404.html', status=404)

def handler500(request):
    return render(request, 'core/500.html', status=500)
