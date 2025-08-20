from django.urls import path
from .views import (
    CategoryListView, CategoryWithChildsView, AdListView, AdDetailView,
    AdCreateView, AdUpdateView, AdLikeView, MyAdsView, PopularAdsView,
    FeaturedAdsView
)

app_name = 'store'

urlpatterns = [
    # Categories
    path('store/categories/', CategoryListView.as_view(), name='categories'),
    path('store/categories-with-childs/', CategoryWithChildsView.as_view(), name='categories_with_childs'),
    
    # Advertisements
    path('store/ads/', AdListView.as_view(), name='ads_list'),
    path('store/ads/create/', AdCreateView.as_view(), name='ads_create'),
    path('store/ads/my/', MyAdsView.as_view(), name='my_ads'),
    path('store/ads/popular/', PopularAdsView.as_view(), name='popular_ads'),
    path('store/ads/featured/', FeaturedAdsView.as_view(), name='featured_ads'),
    path('store/ads/<slug:slug>/', AdDetailView.as_view(), name='ads_detail'),
    path('store/ads/<slug:slug>/edit/', AdUpdateView.as_view(), name='ads_update'),
    path('store/ads/<slug:slug>/like/', AdLikeView.as_view(), name='ads_like'),
]
