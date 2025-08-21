from rest_framework import permissions

class IsSuperAdmin(permissions.BasePermission):
    """Permission for super admin users only"""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'super_admin'
        )

class IsAdmin(permissions.BasePermission):
    """Permission for admin users (includes super admin)"""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['super_admin', 'admin']
        )

class IsSeller(permissions.BasePermission):
    """Permission for seller users"""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'seller'
        )

class IsOwnerOrReadOnly(permissions.BasePermission):
    """Permission to only allow owners of an object to edit it"""
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only to the owner
        owner = getattr(obj, 'user', None) or getattr(obj, 'seller', None)
        return owner == request.user
