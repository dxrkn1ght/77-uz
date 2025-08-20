from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    LoginView, RegisterView, UserProfileView, 
    SellerRegistrationView, logout_view,
    AdminUserListView, AdminUserDetailView, SellerApprovalView,
    PendingSellersView, UserStatsView
)

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('accounts/login/', LoginView.as_view(), name='login'),
    path('accounts/register/', RegisterView.as_view(), name='register'),
    path('accounts/logout/', logout_view, name='logout'),
    path('accounts/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Profile management
    path('accounts/me/', UserProfileView.as_view(), name='profile'),
    path('accounts/edit/', UserProfileView.as_view(), name='profile_edit'),
    
    # Admin user management
    path('admin/users/', AdminUserListView.as_view(), name='admin_users'),
    path('admin/users/<int:pk>/', AdminUserDetailView.as_view(), name='admin_user_detail'),
    path('admin/users/stats/', UserStatsView.as_view(), name='user_stats'),
    
    # Seller management
    path('admin/sellers/register/', SellerRegistrationView.as_view(), name='seller_register'),
    path('admin/sellers/pending/', PendingSellersView.as_view(), name='pending_sellers'),
    path('admin/sellers/<int:seller_id>/approve/', SellerApprovalView.as_view(), name='seller_approval'),
]
