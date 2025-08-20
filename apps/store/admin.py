from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from django.contrib.admin import SimpleListFilter
from .models import Category, Ad, AdPhoto, AdLike, AdView

try:
    from modeltranslation.admin import TabbedTranslationAdmin

    TRANSLATION_AVAILABLE = True
except ImportError:
    TabbedTranslationAdmin = admin.ModelAdmin
    TRANSLATION_AVAILABLE = False


class CategoryFilter(SimpleListFilter):
    """Custom filter for categories"""
    title = _('Category')
    parameter_name = 'category'

    def lookups(self, request, model_admin):
        categories = Category.objects.filter(is_active=True)
        return [(cat.id, cat.name_uz) for cat in categories]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(category_id=self.value())
        return queryset


class SubCategoryInline(admin.TabularInline):
    """Inline for subcategories"""
    model = Category
    fk_name = 'parent'
    extra = 0
    fields = ('name_uz', 'name_ru', 'slug', 'is_active', 'order')
    prepopulated_fields = {'slug': ('name_uz',)}


@admin.register(Category)
class CategoryAdmin(TabbedTranslationAdmin if TRANSLATION_AVAILABLE else admin.ModelAdmin):
    list_display = [
        'name_uz', 'name_ru', 'icon_preview', 'parent', 'is_active',
        'order', 'children_count', 'ads_count'
    ]
    list_filter = ['is_active', 'parent']
    search_fields = ['name_uz', 'name_ru']
    prepopulated_fields = {'slug': ('name_uz',)}
    ordering = ['order', 'name_uz']
    list_per_page = 25
    inlines = [SubCategoryInline]

    fieldsets = (
        (_('Category Information'), {
            'fields': ('name_uz', 'name_ru', 'slug', 'parent', 'icon'),
            'classes': ('wide',)
        }),
        (_('Settings'), {
            'fields': ('is_active', 'order'),
            'classes': ('wide',)
        }),
    )

    def icon_preview(self, obj):
        """Display category icon preview"""
        if obj.icon:
            return format_html(
                '<img src="{}" style="width: 30px; height: 30px; object-fit: cover; border-radius: 4px;">',
                obj.icon.url
            )
        return format_html(
            '<div style="width: 30px; height: 30px; background-color: #f8f9fa; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 10px; color: #6c757d;">No Icon</div>'
        )

    icon_preview.short_description = _('Icon')

    def children_count(self, obj):
        """Display number of subcategories"""
        count = obj.children.count()
        if count > 0:
            url = reverse('admin:store_category_changelist') + f'?parent__id={obj.id}'
            return format_html('<a href="{}">{} children</a>', url, count)
        return '0'

    children_count.short_description = _('Subcategories')

    def ads_count(self, obj):
        """Display number of ads in category"""
        count = obj.ads.filter(is_active=True).count()
        if count > 0:
            url = reverse('admin:store_ad_changelist') + f'?category__id={obj.id}'
            return format_html('<a href="{}">{} ads</a>', url, count)
        return '0'

    ads_count.short_description = _('Active Ads')

    actions = ['activate_categories', 'deactivate_categories']

    def activate_categories(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} categories activated.')

    activate_categories.short_description = _('Activate selected categories')

    def deactivate_categories(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} categories deactivated.')

    deactivate_categories.short_description = _('Deactivate selected categories')


class AdPhotoInline(admin.TabularInline):
    model = AdPhoto
    extra = 1
    fields = ['image', 'image_preview', 'order']
    readonly_fields = ['image_preview']
    ordering = ['order']

    def image_preview(self, obj):
        """Display image preview in inline"""
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 4px;">',
                obj.image.url
            )
        return 'No image'

    image_preview.short_description = _('Preview')


@admin.register(Ad)
class AdAdmin(TabbedTranslationAdmin if TRANSLATION_AVAILABLE else admin.ModelAdmin):
    list_display = [
        'name_uz', 'main_photo', 'category', 'seller_info', 'price_formatted',
        'status_badge', 'view_count', 'likes_count', 'published_at'
    ]
    list_filter = [CategoryFilter, 'is_active', 'is_featured', 'published_at']
    search_fields = ['name_uz', 'name_ru', 'seller__phone_number', 'seller__full_name']
    prepopulated_fields = {'slug': ('name_uz',)}
    raw_id_fields = ['seller', 'category']
    readonly_fields = ['view_count', 'published_at', 'created_at', 'updated_at']
    inlines = [AdPhotoInline]
    list_per_page = 25
    date_hierarchy = 'published_at'

    fieldsets = (
        (_('Advertisement Information'), {
            'fields': ('name_uz', 'name_ru', 'slug', 'description_uz', 'description_ru'),
            'classes': ('wide',)
        }),
        (_('Details'), {
            'fields': ('price', 'category', 'seller'),
            'classes': ('wide',)
        }),
        (_('Settings'), {
            'fields': ('is_active', 'is_featured'),
            'classes': ('wide',)
        }),
        (_('Statistics'), {
            'fields': ('view_count', 'published_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def main_photo(self, obj):
        """Display main photo thumbnail with enhanced styling"""
        photo = obj.photos.first()
        if photo and photo.image:
            return format_html(
                '<div style="position: relative; display: inline-block;">'
                '<img src="{}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 8px; border: 2px solid #e9ecef; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">'
                '<div style="position: absolute; bottom: -5px; right: -5px; background: #28a745; color: white; border-radius: 50%; width: 16px; height: 16px; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: bold;">{}</div>'
                '</div>',
                photo.image.url, obj.photos.count()
            )
        return format_html(
            '<div style="width: 60px; height: 60px; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 8px; display: flex; align-items: center; justify-content: center; border: 2px dashed #dee2e6; color: #6c757d; font-size: 10px; text-align: center;">No<br>Photo</div>'
        )

    main_photo.short_description = _('Photo')

    def seller_info(self, obj):
        """Display seller information with link"""
        url = reverse('admin:accounts_user_change', args=[obj.seller.id])
        return format_html(
            '<a href="{}">{}</a><br><small>{}</small>',
            url, obj.seller.full_name or 'No name', obj.seller.phone_number
        )

    seller_info.short_description = _('Seller')

    def price_formatted(self, obj):
        """Display formatted price"""
        return f"{obj.price:,} UZS" if obj.price else '-'

    price_formatted.short_description = _('Price')

    def status_badge(self, obj):
        """Display status as colored badge"""
        if obj.is_active:
            badge_class = 'success' if not obj.is_featured else 'warning'
            text = 'Featured' if obj.is_featured else 'Active'
            color = '#198754' if not obj.is_featured else '#ffc107'
        else:
            badge_class = 'secondary'
            text = 'Inactive'
            color = '#6c757d'

        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color, text
        )

    status_badge.short_description = _('Status')

    def likes_count(self, obj):
        """Display number of likes"""
        count = obj.likes.count()
        if count > 0:
            return format_html('<strong>{}</strong> ❤️', count)
        return '0'

    likes_count.short_description = _('Likes')

    actions = ['activate_ads', 'deactivate_ads', 'feature_ads', 'unfeature_ads']

    def activate_ads(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} ads activated.')

    activate_ads.short_description = _('Activate selected ads')

    def deactivate_ads(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} ads deactivated.')

    deactivate_ads.short_description = _('Deactivate selected ads')

    def feature_ads(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} ads featured.')

    feature_ads.short_description = _('Feature selected ads')

    def unfeature_ads(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} ads unfeatured.')

    unfeature_ads.short_description = _('Unfeature selected ads')


@admin.register(AdPhoto)
class AdPhotoAdmin(admin.ModelAdmin):
    list_display = ['ad', 'image_preview', 'order', 'created_at']
    list_filter = ['created_at']
    raw_id_fields = ['ad']
    ordering = ['ad', 'order']

    def image_preview(self, obj):
        """Display image preview with enhanced styling"""
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 80px; height: 80px; object-fit: cover; border-radius: 8px; border: 2px solid #e9ecef; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">',
                obj.image.url
            )
        return format_html(
            '<div style="width: 80px; height: 80px; background: #f8f9fa; border-radius: 8px; display: flex; align-items: center; justify-content: center; border: 2px dashed #dee2e6; color: #6c757d; font-size: 12px;">No Image</div>'
        )

    image_preview.short_description = _('Preview')


@admin.register(AdLike)
class AdLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'ad', 'created_at']
    list_filter = ['created_at']
    raw_id_fields = ['user', 'ad']
    readonly_fields = ['created_at']


@admin.register(AdView)
class AdViewAdmin(admin.ModelAdmin):
    list_display = ['ad', 'user', 'ip_address', 'created_at']
    list_filter = ['created_at']
    raw_id_fields = ['user', 'ad']
    readonly_fields = ['created_at']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('ad', 'user')
