from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from apps.common.models import Address
from .models import User, SellerProfile

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'name', 'lat', 'long']

class UserProfileSerializer(serializers.ModelSerializer):
    address = AddressSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'full_name', 'phone_number', 'profile_photo', 
            'address', 'created_at', 'role'
        ]
        read_only_fields = ['id', 'phone_number', 'created_at', 'role']

class UserProfileEditSerializer(serializers.ModelSerializer):
    address = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(), 
        required=False, 
        allow_null=True
    )
    
    class Meta:
        model = User
        fields = ['full_name', 'phone_number', 'profile_photo', 'address']
        read_only_fields = ['profile_photo']

class UserLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        password = attrs.get('password')
        
        if phone_number and password:
            user = authenticate(
                request=self.context.get('request'),
                username=phone_number,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError(
                    _('Invalid phone number or password')
                )
            
            if not user.is_active:
                raise serializers.ValidationError(
                    _('User account is disabled')
                )
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError(
                _('Phone number and password are required')
            )

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = [
            'full_name', 'phone_number', 'password', 'password_confirm'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(
                _('Password confirmation does not match')
            )
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user

class SellerRegistrationSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    
    class Meta:
        model = SellerProfile
        fields = ['project_name', 'category', 'address']
    
    def create(self, validated_data):
        address_data = validated_data.pop('address')
        address = Address.objects.create(**address_data)
        
        user = self.context['request'].user
        user.address = address
        user.role = 'seller'
        user.save()
        
        seller_profile = SellerProfile.objects.create(
            user=user,
            **validated_data
        )
        return seller_profile

class LoginResponseSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    user = UserProfileSerializer()

class AdminUserSerializer(serializers.ModelSerializer):
    """Serializer for admin user management"""
    address = AddressSerializer(read_only=True)
    seller_profile = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'full_name', 'phone_number', 'profile_photo', 
            'address', 'role', 'is_active', 'is_verified', 
            'created_at', 'updated_at', 'seller_profile'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_seller_profile(self, obj):
        if hasattr(obj, 'seller_profile'):
            return {
                'id': obj.seller_profile.id,
                'project_name': obj.seller_profile.project_name,
                'is_approved': obj.seller_profile.is_approved,
                'category': obj.seller_profile.category.name if obj.seller_profile.category else None
            }
        return None

class AdminUserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating users by admin"""
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = [
            'full_name', 'phone_number', 'password', 'role', 'is_active'
        ]
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user

class SellerApprovalSerializer(serializers.ModelSerializer):
    """Serializer for seller approval/rejection"""
    
    class Meta:
        model = SellerProfile
        fields = ['is_approved']
    
    def update(self, instance, validated_data):
        instance.is_approved = validated_data.get('is_approved', instance.is_approved)
        instance.save()
        
        # Update user verification status
        if instance.is_approved:
            instance.user.is_verified = True
            instance.user.save()
        
        return instance
