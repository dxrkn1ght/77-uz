import django_filters
from .models import User, SellerProfile

class UserFilter(django_filters.FilterSet):
    """Filter for user management"""
    role = django_filters.ChoiceFilter(choices=User.ROLE_CHOICES)
    is_active = django_filters.BooleanFilter()
    is_verified = django_filters.BooleanFilter()
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = User
        fields = ['role', 'is_active', 'is_verified']

class SellerProfileFilter(django_filters.FilterSet):
    """Filter for seller profile management"""
    is_approved = django_filters.BooleanFilter()
    category = django_filters.NumberFilter()
    
    class Meta:
        model = SellerProfile
        fields = ['is_approved', 'category']
