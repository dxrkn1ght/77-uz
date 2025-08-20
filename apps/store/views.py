from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from apps.common.permissions import IsSeller, IsOwnerOrReadOnly
from .models import Category, Ad, AdLike, AdView
from .serializers import (
    CategorySerializer, CategoryWithChildsSerializer, AdListSerializer,
    AdDetailSerializer, AdCreateSerializer, AdUpdateSerializer, AdLikeSerializer
)
from .filters import AdFilter

class CategoryListView(ListAPIView):
    """List all active categories"""
    queryset = Category.objects.filter(is_active=True, parent=None)
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        responses={200: CategorySerializer(many=True)},
        summary='List categories',
        description='Get list of all active root categories'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class CategoryWithChildsView(ListAPIView):
    """List categories with all nested children"""
    queryset = Category.objects.filter(is_active=True, parent=None)
    serializer_class = CategoryWithChildsSerializer
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        responses={200: CategoryWithChildsSerializer(many=True)},
        summary='List categories with children',
        description='Get list of categories with all nested children'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class AdListView(ListAPIView):
    """List ads with filtering and search"""
    serializer_class = AdListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = AdFilter
    search_fields = ['name_uz', 'name_ru', 'description_uz', 'description_ru']
    ordering_fields = ['price', 'published_at', 'view_count']
    ordering = ['-published_at']
    
    def get_queryset(self):
        return Ad.objects.filter(is_active=True).select_related(
            'category', 'seller', 'seller__address'
        ).prefetch_related('photos')
    
    @extend_schema(
        parameters=[
            OpenApiParameter('category', int, description='Filter by category ID'),
            OpenApiParameter('min_price', float, description='Minimum price filter'),
            OpenApiParameter('max_price', float, description='Maximum price filter'),
            OpenApiParameter('seller', int, description='Filter by seller ID'),
            OpenApiParameter('search', str, description='Search in name and description'),
            OpenApiParameter('ordering', str, description='Order by: price, -price, published_at, -published_at, view_count, -view_count'),
        ],
        responses={200: AdListSerializer(many=True)},
        summary='List advertisements',
        description='Get paginated list of active advertisements with filtering and search'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class AdDetailView(RetrieveAPIView):
    """Get ad details by slug"""
    queryset = Ad.objects.filter(is_active=True)
    serializer_class = AdDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Track view
        self.track_view(request, instance)
        
        # Increment view count
        instance.increment_view_count()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def track_view(self, request, ad):
        """Track ad view"""
        user = request.user if request.user.is_authenticated else None
        ip_address = self.get_client_ip(request)
        
        # Avoid duplicate views from same user/IP in short time
        if not AdView.objects.filter(
            ad=ad,
            user=user,
            ip_address=ip_address,
            created_at__gte=timezone.now() - timezone.timedelta(hours=1)
        ).exists():
            AdView.objects.create(ad=ad, user=user, ip_address=ip_address)
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @extend_schema(
        responses={200: AdDetailSerializer},
        summary='Get advertisement details',
        description='Get detailed information about advertisement by slug'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class AdCreateView(CreateAPIView):
    """Create new advertisement"""
    serializer_class = AdCreateSerializer
    permission_classes = [IsSeller]
    
    @extend_schema(
        request=AdCreateSerializer,
        responses={201: AdDetailSerializer},
        summary='Create advertisement',
        description='Create new advertisement (seller only)'
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class AdUpdateView(RetrieveUpdateDestroyAPIView):
    """Update/delete advertisement"""
    serializer_class = AdUpdateSerializer
    permission_classes = [IsSeller, IsOwnerOrReadOnly]
    lookup_field = 'slug'
    
    def get_queryset(self):
        return Ad.objects.filter(seller=self.request.user)
    
    @extend_schema(
        responses={200: AdUpdateSerializer},
        summary='Get advertisement for editing',
        description='Get advertisement details for editing (owner only)'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        request=AdUpdateSerializer,
        responses={200: AdUpdateSerializer},
        summary='Update advertisement',
        description='Update advertisement (owner only)'
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        request=AdUpdateSerializer,
        responses={200: AdUpdateSerializer},
        summary='Partially update advertisement',
        description='Partially update advertisement (owner only)'
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        responses={204: OpenApiResponse(description='Advertisement deleted')},
        summary='Delete advertisement',
        description='Delete advertisement (owner only)'
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

class AdLikeView(APIView):
    """Like/unlike advertisement"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        responses={
            200: OpenApiResponse(description='Advertisement liked'),
            201: OpenApiResponse(description='Advertisement unliked')
        },
        summary='Toggle advertisement like',
        description='Like or unlike advertisement'
    )
    def post(self, request, slug):
        ad = get_object_or_404(Ad, slug=slug, is_active=True)
        like, created = AdLike.objects.get_or_create(user=request.user, ad=ad)
        
        if created:
            return Response(
                {'message': 'Advertisement liked', 'is_liked': True},
                status=status.HTTP_200_OK
            )
        else:
            like.delete()
            return Response(
                {'message': 'Advertisement unliked', 'is_liked': False},
                status=status.HTTP_200_OK
            )

class MyAdsView(ListAPIView):
    """List current user's advertisements"""
    serializer_class = AdListSerializer
    permission_classes = [IsSeller]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name_uz', 'name_ru']
    ordering_fields = ['published_at', 'view_count', 'price']
    ordering = ['-published_at']
    
    def get_queryset(self):
        return Ad.objects.filter(seller=self.request.user).select_related(
            'category'
        ).prefetch_related('photos')
    
    @extend_schema(
        responses={200: AdListSerializer(many=True)},
        summary='Get my advertisements',
        description='Get list of current user advertisements (seller only)'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class PopularAdsView(ListAPIView):
    """List popular advertisements"""
    serializer_class = AdListSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        return Ad.objects.filter(is_active=True).select_related(
            'category', 'seller'
        ).prefetch_related('photos').order_by('-view_count')[:20]
    
    @extend_schema(
        responses={200: AdListSerializer(many=True)},
        summary='Get popular advertisements',
        description='Get list of most viewed advertisements'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class FeaturedAdsView(ListAPIView):
    """List featured advertisements"""
    serializer_class = AdListSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        return Ad.objects.filter(is_active=True, is_featured=True).select_related(
            'category', 'seller'
        ).prefetch_related('photos').order_by('-published_at')
    
    @extend_schema(
        responses={200: AdListSerializer(many=True)},
        summary='Get featured advertisements',
        description='Get list of featured advertisements'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
