from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'core'

# DRF Router
router = DefaultRouter()
router.register(r'digital-assets', views.DigitalAssetViewSet)
router.register(r'payments', views.PaymentViewSet)

urlpatterns = [
    # Basic Views
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings, name='settings'),
    
    # Authentication Views
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    
    # Profile Views
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('account/delete/', views.delete_account, name='account_delete'),
    
    # Password Reset URLs
    path('password-reset/', 
        auth_views.PasswordResetView.as_view(
            template_name='core/auth/password_reset_form.html',
            email_template_name='core/auth/password_reset_email.html',
            subject_template_name='core/auth/password_reset_subject.txt'
        ),
        name='password_reset'
    ),
    path('password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='core/auth/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path('password-reset-confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='core/auth/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),
    path('password-reset-complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='core/auth/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
    
    # Project URLs
    path('projects/', views.project_list, name='project_list'),
    path('projects/create/', views.project_create, name='project_create'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('projects/<int:pk>/edit/', views.project_edit, name='project_edit'),
    path('projects/<int:pk>/delete/', views.project_delete, name='project_delete'),
    
    # Payment Views
    path('payment/<int:project_id>/create/', views.create_payment, name='create_payment'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/cancel/', views.payment_cancel, name='payment_cancel'),
    
    # Static Pages
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms/', views.terms, name='terms'),
    path('faq/', views.faq, name='faq'),
    path('designer/', views.designer, name='designer'),
    
    # API Endpoints
    path('api/', include(router.urls)),
    path('api/designs/', views.save_design, name='save_design'),
]

# Error handlers
handler404 = views.handler404
handler500 = views.handler500