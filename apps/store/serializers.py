from rest_framework import serializers
from django.utils.translation import get_language
from apps.accounts.serializers import UserProfileSerializer
from .models import Category, Ad, AdPhoto, AdLike

class CategorySerializer(serializers.ModelSerializer):
    """Basic category serializer"""
    name = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'icon']
    
    def get_name(self, obj):
        return obj.name

class CategoryDetailSerializer(serializers.ModelSerializer):
    """Detailed category serializer with children"""
    name = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'icon', 'children']
    
    def get_name(self, obj):
        return obj.name
    
    def get_children(self, obj):
        children = obj.children.filter(is_active=True)
        return CategorySerializer(children, many=True).data

class CategoryWithChildsSerializer(serializers.ModelSerializer):
    """Category serializer with all nested children"""
    name = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'icon', 'children']
    
    def get_name(self, obj):
        return obj.name
    
    def get_children(self, obj):
        children = obj.children.filter(is_active=True)
        return CategoryWithChildsSerializer(children, many=True).data

class AdPhotoSerializer(serializers.ModelSerializer):
    """Ad photo serializer"""
    
    class Meta:
        model = AdPhoto
        fields = ['id', 'image', 'order']

class AdListSerializer(serializers.ModelSerializer):
    """Ad list serializer"""
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)
    seller = UserProfileSerializer(read_only=True)
    photos = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Ad
        fields = [
            'id', 'name', 'slug', 'description', 'price', 'category',
            'seller', 'photos', 'is_liked', 'view_count', 'published_at'
        ]
    
    def get_name(self, obj):
        return obj.name
    
    def get_description(self, obj):
        # Return truncated description for list view
        desc = obj.description
        return desc[:200] + '...' if len(desc) > 200 else desc
    
    def get_photos(self, obj):
        photos = obj.photos.all()[:3]  # First 3 photos for list view
        return [photo.image.url for photo in photos]
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return AdLike.objects.filter(user=request.user, ad=obj).exists()
        return False

class AdDetailSerializer(serializers.ModelSerializer):
    """Detailed ad serializer"""
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)
    seller = UserProfileSerializer(read_only=True)
    photos = AdPhotoSerializer(many=True, read_only=True)
    is_liked = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    updated_time = serializers.DateTimeField(source='updated_at', read_only=True)
    
    class Meta:
        model = Ad
        fields = [
            'id', 'name', 'slug', 'description', 'price', 'category',
            'seller', 'photos', 'is_liked', 'view_count', 'published_at',
            'address', 'updated_time'
        ]
    
    def get_name(self, obj):
        return obj.name
    
    def get_description(self, obj):
        return obj.description
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return AdLike.objects.filter(user=request.user, ad=obj).exists()
        return False
    
    def get_address(self, obj):
        if obj.seller.address:
            return obj.seller.address.name
        return None

class AdCreateSerializer(serializers.ModelSerializer):
    """Ad creation serializer"""
    photos = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Ad
        fields = [
            'name_uz', 'name_ru', 'description_uz', 'description_ru',
            'price', 'category', 'photos'
        ]
    
    def create(self, validated_data):
        photos_data = validated_data.pop('photos', [])
        validated_data['seller'] = self.context['request'].user
        
        ad = Ad.objects.create(**validated_data)
        
        # Create photos
        for i, photo in enumerate(photos_data):
            AdPhoto.objects.create(ad=ad, image=photo, order=i)
        
        return ad

class AdUpdateSerializer(serializers.ModelSerializer):
    """Ad update serializer"""
    
    class Meta:
        model = Ad
        fields = [
            'name_uz', 'name_ru', 'description_uz', 'description_ru',
            'price', 'category', 'is_active'
        ]
    
    def update(self, instance, validated_data):
        # Only allow seller to update their own ads
        if instance.seller != self.context['request'].user:
            raise serializers.ValidationError("You can only update your own ads")
        
        return super().update(instance, validated_data)

class AdLikeSerializer(serializers.ModelSerializer):
    """Ad like serializer"""
    
    class Meta:
        model = AdLike
        fields = ['id', 'created_at']
        read_only_fields = ['id', 'created_at']
