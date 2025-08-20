from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models import BaseModel, Address
from apps.common.utils import validate_phone_number
from .managers import UserManager

class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    """Custom User model with phone number authentication"""
    
    ROLE_CHOICES = [
        ('super_admin', _('Super Admin')),
        ('admin', _('Admin')),
        ('seller', _('Seller')),
        ('user', _('User')),
    ]
    
    phone_number = models.CharField(
        _('Phone number'), 
        max_length=15, 
        unique=True,
        validators=[validate_phone_number]
    )
    full_name = models.CharField(_('Full name'), max_length=255, blank=True)
    profile_photo = models.ImageField(
        _('Profile photo'), 
        upload_to='profiles/', 
        null=True, 
        blank=True
    )
    address = models.ForeignKey(
        Address, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name=_('Address')
    )
    role = models.CharField(
        _('Role'), 
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='user'
    )
    is_active = models.BooleanField(_('Is active'), default=True)
    is_staff = models.BooleanField(_('Is staff'), default=False)
    is_verified = models.BooleanField(_('Is verified'), default=False)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        
    def __str__(self):
        return self.phone_number
    
    @property
    def is_super_admin(self):
        return self.role == 'super_admin'
    
    @property
    def is_admin(self):
        return self.role in ['super_admin', 'admin']
    
    @property
    def is_seller(self):
        return self.role == 'seller'

class SellerProfile(BaseModel):
    """Extended profile for sellers"""
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='seller_profile'
    )
    project_name = models.CharField(_('Project name'), max_length=255, blank=True)
    category = models.ForeignKey(
        'store.Category', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name=_('Category')
    )
    is_approved = models.BooleanField(_('Is approved'), default=False)
    
    class Meta:
        verbose_name = _('Seller Profile')
        verbose_name_plural = _('Seller Profiles')
        
    def __str__(self):
        return f"{self.user.phone_number} - {self.project_name}"
