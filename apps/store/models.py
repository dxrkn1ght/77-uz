from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from apps.common.models import BaseModel
from .utils import generate_unique_slug

User = get_user_model()


class Category(BaseModel):
    """Product categories with hierarchical structure"""
    name_uz = models.CharField(_('Name (Uzbek)'), max_length=255)
    name_ru = models.CharField(_('Name (Russian)'), max_length=255)
    slug = models.SlugField(_('Slug'), max_length=255, unique=True)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='children',
        verbose_name=_('Parent Category')
    )
    icon = models.ImageField(_('Icon'), upload_to='categories/', null=True, blank=True)
    is_active = models.BooleanField(_('Is Active'), default=True)
    order = models.PositiveIntegerField(_('Order'), default=0)
    
    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['order', 'name_uz']
        
    def __str__(self):
        return self.name_uz
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(Category, self.name_uz)
        super().save(*args, **kwargs)
    
    @property
    def name(self):
        """Return name based on current language"""
        from django.utils.translation import get_language
        lang = get_language()
        if lang == 'ru':
            return self.name_ru
        return self.name_uz
    
    def get_all_children(self):
        """Get all descendant categories"""
        children = list(self.children.all())
        for child in self.children.all():
            children.extend(child.get_all_children())
        return children

class Ad(BaseModel):
    """Product advertisements"""
    name_uz = models.CharField(_('Name (Uzbek)'), max_length=255)
    name_ru = models.CharField(_('Name (Russian)'), max_length=255)
    slug = models.SlugField(_('Slug'), max_length=255, unique=True)
    description_uz = models.TextField(_('Description (Uzbek)'))
    description_ru = models.TextField(_('Description (Russian)'))
    price = models.DecimalField(_('Price'), max_digits=12, decimal_places=2)
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE,
        related_name='ads',
        verbose_name=_('Category')
    )
    seller = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='ads',
        verbose_name=_('Seller')
    )
    is_active = models.BooleanField(_('Is Active'), default=True)
    is_featured = models.BooleanField(_('Is Featured'), default=False)
    view_count = models.PositiveIntegerField(_('View Count'), default=0)
    published_at = models.DateTimeField(_('Published At'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Advertisement')
        verbose_name_plural = _('Advertisements')
        ordering = ['-published_at']
        
    def __str__(self):
        return self.name_uz
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(Ad, self.name_uz)
        super().save(*args, **kwargs)
    
    @property
    def name(self):
        """Return name based on current language"""
        from django.utils.translation import get_language
        lang = get_language()
        if lang == 'ru':
            return self.name_ru
        return self.name_uz
    
    @property
    def description(self):
        """Return description based on current language"""
        from django.utils.translation import get_language
        lang = get_language()
        if lang == 'ru':
            return self.description_ru
        return self.description_uz
    
    def increment_view_count(self):
        """Increment view count"""
        self.view_count += 1
        self.save(update_fields=['view_count'])

class AdPhoto(BaseModel):
    """Photos for advertisements"""
    ad = models.ForeignKey(
        Ad, 
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name=_('Advertisement')
    )
    image = models.ImageField(_('Image'), upload_to='ads/')
    order = models.PositiveIntegerField(_('Order'), default=0)
    
    class Meta:
        verbose_name = _('Ad Photo')
        verbose_name_plural = _('Ad Photos')
        ordering = ['order']
        
    def __str__(self):
        return f"{self.ad.name_uz} - Photo {self.order}"

class AdLike(BaseModel):
    """User likes for advertisements"""
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='liked_ads',
        verbose_name=_('User')
    )
    ad = models.ForeignKey(
        Ad, 
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name=_('Advertisement')
    )
    
    class Meta:
        verbose_name = _('Ad Like')
        verbose_name_plural = _('Ad Likes')
        unique_together = ['user', 'ad']
        
    def __str__(self):
        return f"{self.user.phone_number} likes {self.ad.name_uz}"

class AdView(BaseModel):
    """Track ad views by users"""
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        null=True, 
        blank=True,
        related_name='ad_views',
        verbose_name=_('User')
    )
    ad = models.ForeignKey(
        Ad, 
        on_delete=models.CASCADE,
        related_name='views',
        verbose_name=_('Advertisement')
    )
    ip_address = models.GenericIPAddressField(_('IP Address'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('Ad View')
        verbose_name_plural = _('Ad Views')
        
    def __str__(self):
        return f"View of {self.ad.name_uz}"
