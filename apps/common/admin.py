from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import Address


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    fields = ('user', 'name', 'street', 'city', 'postal_code')
    list_display = ('id', 'user', 'name', 'street', 'city')
    search_fields = ('user__phone_number', 'user__full_name', 'street', 'city')


    readonly_fields = ['created_at', 'updated_at']

    def coordinates_display(self, obj):
        """Display coordinates with map link if available"""
        if obj.lat and obj.long:
            map_url = f"https://www.google.com/maps?q={obj.lat},{obj.long}"
            return format_html(
                '<a href="{}" target="_blank" style="color: #007cba; text-decoration: none;">'
                '📍 {:.6f}, {:.6f}</a>',
                map_url, obj.lat, obj.long
            )
        return '-'

    coordinates_display.short_description = _('Coordinates')
