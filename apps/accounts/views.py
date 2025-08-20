from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from apps.common.permissions import IsAdmin, IsSuperAdmin
from .models import User, SellerProfile
from .serializers import (
    UserLoginSerializer, UserRegisterSerializer, UserProfileSerializer,
    UserProfileEditSerializer, SellerRegistrationSerializer, LoginResponseSerializer,
    AdminUserSerializer, AdminUserCreateSerializer, SellerApprovalSerializer
)

User = get_user_model()

class LoginView(APIView):
    """User login endpoint"""
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        request=UserLoginSerializer,
        responses={
            200: LoginResponseSerializer,
            401: OpenApiResponse(description='Invalid credentials'),
            429: OpenApiResponse(description='Too many requests')
        },
        summary='User login',
        description='Authenticate user and return access tokens'
    )
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            
            response_data = {
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'user': UserProfileSerializer(user).data
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

class RegisterView(APIView):
    """User registration endpoint"""
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        request=UserRegisterSerializer,
        responses={
            201: LoginResponseSerializer,
            400: OpenApiResponse(description='Validation errors')
        },
        summary='User registration',
        description='Register new user and return access tokens'
    )
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            
            response_data = {
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'user': UserProfileSerializer(user).data
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(RetrieveUpdateAPIView):
    """User profile view and edit"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserProfileEditSerializer
        return UserProfileSerializer
    
    @extend_schema(
        responses={200: UserProfileSerializer},
        summary='Get current user profile',
        description='Retrieve current authenticated user profile'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        request=UserProfileEditSerializer,
        responses={200: UserProfileEditSerializer},
        summary='Update user profile',
        description='Update current user profile information'
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        request=UserProfileEditSerializer,
        responses={200: UserProfileEditSerializer},
        summary='Partially update user profile',
        description='Partially update current user profile information'
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

class SellerRegistrationView(APIView):
    """Seller registration endpoint for admins"""
    permission_classes = [IsAdmin]
    
    @extend_schema(
        request=SellerRegistrationSerializer,
        responses={
            201: OpenApiResponse(description='Seller registered successfully'),
            400: OpenApiResponse(description='Validation errors'),
            403: OpenApiResponse(description='Permission denied')
        },
        summary='Register new seller',
        description='Admin endpoint to register new seller with profile'
    )
    def post(self, request):
        # Create user first
        user_data = {
            'phone_number': request.data.get('phone_number'),
            'full_name': request.data.get('full_name', ''),
            'password': request.data.get('password', 'temp_password_123'),
            'password_confirm': request.data.get('password', 'temp_password_123'),
        }
        
        user_serializer = UserRegisterSerializer(data=user_data)
        if user_serializer.is_valid():
            user = user_serializer.save()
            
            # Create seller profile
            request.data['user'] = user.id
            seller_serializer = SellerRegistrationSerializer(
                data=request.data, 
                context={'request': request}
            )
            
            if seller_serializer.is_valid():
                seller_profile = seller_serializer.save()
                return Response(
                    {'message': 'Seller registered successfully'}, 
                    status=status.HTTP_201_CREATED
                )
            else:
                user.delete()  # Rollback user creation
                return Response(
                    seller_serializer.errors, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminUserListView(ListCreateAPIView):
    """Admin endpoint to list and create users"""
    permission_classes = [IsAdmin]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AdminUserCreateSerializer
        return AdminUserSerializer
    
    def get_queryset(self):
        queryset = User.objects.all().order_by('-created_at')
        
        # Filter by role
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        
        # Search by phone number or name
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(phone_number__icontains=search) | 
                Q(full_name__icontains=search)
            )
        
        return queryset
    
    @extend_schema(
        parameters=[
            OpenApiParameter('role', str, description='Filter by user role'),
            OpenApiParameter('search', str, description='Search by phone number or name'),
        ],
        responses={200: AdminUserSerializer(many=True)},
        summary='List all users',
        description='Admin endpoint to list all users with filtering options'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        request=AdminUserCreateSerializer,
        responses={201: AdminUserSerializer},
        summary='Create new user',
        description='Admin endpoint to create new user with specific role'
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class AdminUserDetailView(RetrieveUpdateDestroyAPIView):
    """Admin endpoint to manage specific user"""
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdmin]
    
    def get_permissions(self):
        # Only super admin can delete users
        if self.request.method == 'DELETE':
            return [IsSuperAdmin()]
        return [IsAdmin()]
    
    @extend_schema(
        responses={200: AdminUserSerializer},
        summary='Get user details',
        description='Admin endpoint to get specific user details'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        request=AdminUserSerializer,
        responses={200: AdminUserSerializer},
        summary='Update user',
        description='Admin endpoint to update user information and role'
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        request=AdminUserSerializer,
        responses={200: AdminUserSerializer},
        summary='Partially update user',
        description='Admin endpoint to partially update user information'
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        responses={204: OpenApiResponse(description='User deleted successfully')},
        summary='Delete user',
        description='Super admin endpoint to delete user (requires super admin role)'
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

class SellerApprovalView(APIView):
    """Admin endpoint to approve/reject sellers"""
    permission_classes = [IsAdmin]
    
    @extend_schema(
        request=SellerApprovalSerializer,
        responses={
            200: OpenApiResponse(description='Seller status updated'),
            404: OpenApiResponse(description='Seller not found')
        },
        summary='Approve or reject seller',
        description='Admin endpoint to approve or reject seller applications'
    )
    def patch(self, request, seller_id):
        try:
            seller_profile = SellerProfile.objects.get(id=seller_id)
        except SellerProfile.DoesNotExist:
            return Response(
                {'error': 'Seller not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = SellerApprovalSerializer(
            seller_profile, 
            data=request.data, 
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'Seller status updated successfully'}, 
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PendingSellersView(APIView):
    """Admin endpoint to get pending seller applications"""
    permission_classes = [IsAdmin]
    
    @extend_schema(
        responses={200: SellerRegistrationSerializer(many=True)},
        summary='Get pending sellers',
        description='Admin endpoint to get all pending seller applications'
    )
    def get(self, request):
        pending_sellers = SellerProfile.objects.filter(is_approved=False)
        serializer = SellerRegistrationSerializer(pending_sellers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserStatsView(APIView):
    """Admin endpoint to get user statistics"""
    permission_classes = [IsAdmin]
    
    @extend_schema(
        responses={200: OpenApiResponse(description='User statistics')},
        summary='Get user statistics',
        description='Admin endpoint to get user statistics by role and status'
    )
    def get(self, request):
        stats = {
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'users_by_role': {
                'super_admin': User.objects.filter(role='super_admin').count(),
                'admin': User.objects.filter(role='admin').count(),
                'seller': User.objects.filter(role='seller').count(),
                'user': User.objects.filter(role='user').count(),
            },
            'pending_sellers': SellerProfile.objects.filter(is_approved=False).count(),
            'approved_sellers': SellerProfile.objects.filter(is_approved=True).count(),
        }
        
        return Response(stats, status=status.HTTP_200_OK)

@extend_schema(
    responses={200: OpenApiResponse(description='Logout successful')},
    summary='User logout',
    description='Logout current user (client-side token removal)'
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """Logout endpoint (client handles token removal)"""
    return Response(
        {'message': 'Logout successful'}, 
        status=status.HTTP_200_OK
    )
