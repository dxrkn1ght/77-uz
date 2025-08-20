from django.db import models
from django.utils.translation import gettext_lazy as _

class BaseModel(models.Model):
    """Base model with common fields for all models"""
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)
    
    class Meta:
        abstract = True

class Address(BaseModel):
    """Address model for users and sellers"""
    name = models.CharField(_('Name'), max_length=250)
    lat = models.FloatField(_('Latitude'), null=True, blank=True)
    long = models.FloatField(_('Longitude'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('Address')
        verbose_name_plural = _('Addresses')
        
    def __str__(self):
        return self.name
