from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Address

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['name', 'lat', 'long', 'created_at']
    search_fields = ['name']
    list_filter = ['created_at']
    
    fieldsets = (
        (_('Address Information'), {
            'fields': ('name', 'lat', 'long'),
            'classes': ('wide',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
