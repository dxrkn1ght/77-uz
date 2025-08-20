import django_filters
from .models import Ad, Category

class AdFilter(django_filters.FilterSet):
    """Filter for advertisements"""
    category = django_filters.ModelChoiceFilter(queryset=Category.objects.all())
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    seller = django_filters.NumberFilter(field_name='seller__id')
    is_featured = django_filters.BooleanFilter()
    published_after = django_filters.DateTimeFilter(field_name='published_at', lookup_expr='gte')
    published_before = django_filters.DateTimeFilter(field_name='published_at', lookup_expr='lte')
    
    class Meta:
        model = Ad
        fields = ['category', 'seller', 'is_featured']
