from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from django.contrib.admin import SimpleListFilter
from .models import User, SellerProfile

class RoleFilter(SimpleListFilter):
    """Custom filter for user roles"""
    title = _('Role')
    parameter_name = 'role'

    def lookups(self, request, model_admin):
        return User.ROLE_CHOICES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(role=self.value())
        return queryset

class SellerProfileInline(admin.StackedInline):
    """Inline for seller profile"""
    model = SellerProfile
    extra = 0
    fields = ('project_name', 'category', 'is_approved')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        'phone_number', 'full_name', 'role_badge', 'is_active', 
        'is_verified', 'created_at', 'ads_count'
    ]
    list_filter = [RoleFilter, 'is_active', 'is_verified', 'created_at']
    search_fields = ['phone_number', 'full_name']
    ordering = ['-created_at']
    list_per_page = 25
    
    fieldsets = (
        (_('Authentication'), {
            'fields': ('phone_number', 'password'),
            'classes': ('wide',)
        }),
        (_('Personal Information'), {
            'fields': ('full_name', 'profile_photo', 'address'),
            'classes': ('wide',)
        }),
        (_('Permissions & Role'), {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'is_verified'),
            'classes': ('wide',)
        }),
        (_('Important Dates'), {
            'fields': ('last_login', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (_('Create New User'), {
            'classes': ('wide',),
            'fields': ('phone_number', 'password1', 'password2', 'role', 'full_name'),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'last_login']
    inlines = [SellerProfileInline]
    
    def role_badge(self, obj):
        """Display role as colored badge"""
        colors = {
            'super_admin': '#dc3545',  # Red
            'admin': '#fd7e14',        # Orange
            'seller': '#198754',       # Green
            'user': '#6c757d'          # Gray
        }
        color = colors.get(obj.role, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color, obj.get_role_display()
        )
    role_badge.short_description = _('Role')
    
    def ads_count(self, obj):
        """Display number of ads for sellers"""
        if obj.role == 'seller':
            count = obj.ads.count()
            if count > 0:
                url = reverse('admin:store_ad_changelist') + f'?seller__id={obj.id}'
                return format_html('<a href="{}">{} ads</a>', url, count)
            return '0 ads'
        return '-'
    ads_count.short_description = _('Ads Count')
    
    actions = ['activate_users', 'deactivate_users', 'verify_users']
    
    def activate_users(self, request, queryset):
        """Activate selected users"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} users activated successfully.')
    activate_users.short_description = _('Activate selected users')
    
    def deactivate_users(self, request, queryset):
        """Deactivate selected users"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} users deactivated successfully.')
    deactivate_users.short_description = _('Deactivate selected users')
    
    def verify_users(self, request, queryset):
        """Verify selected users"""
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} users verified successfully.')
    verify_users.short_description = _('Verify selected users')

@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user_phone', 'user_name', 'project_name', 'category', 
        'approval_status', 'created_at'
    ]
    list_filter = ['is_approved', 'category', 'created_at']
    search_fields = [
        'user__phone_number', 'user__full_name', 'project_name'
    ]
    raw_id_fields = ['user', 'category']
    list_per_page = 25
    
    fieldsets = (
        (_('Seller Information'), {
            'fields': ('user', 'project_name', 'category'),
            'classes': ('wide',)
        }),
        (_('Approval Status'), {
            'fields': ('is_approved',),
            'classes': ('wide',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def user_phone(self, obj):
        return obj.user.phone_number
    user_phone.short_description = _('Phone Number')
    
    def user_name(self, obj):
        return obj.user.full_name or '-'
    user_name.short_description = _('Full Name')
    
    def approval_status(self, obj):
        """Display approval status as badge"""
        if obj.is_approved:
            return format_html(
                '<span style="background-color: #198754; color: white; padding: 3px 8px; '
                'border-radius: 3px; font-size: 11px; font-weight: bold;">Approved</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #ffc107; color: black; padding: 3px 8px; '
                'border-radius: 3px; font-size: 11px; font-weight: bold;">Pending</span>'
            )
    approval_status.short_description = _('Status')
    
    actions = ['approve_sellers', 'reject_sellers']
    
    def approve_sellers(self, request, queryset):
        """Approve selected sellers"""
        updated = queryset.update(is_approved=True)
        # Also verify the users
        user_ids = queryset.values_list('user_id', flat=True)
        User.objects.filter(id__in=user_ids).update(is_verified=True)
        self.message_user(request, f'{updated} sellers approved successfully.')
    approve_sellers.short_description = _('Approve selected sellers')
    
    def reject_sellers(self, request, queryset):
        """Reject selected sellers"""
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} sellers rejected.')
    reject_sellers.short_description = _('Reject selected sellers')
