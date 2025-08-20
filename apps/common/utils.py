import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_phone_number(phone_number):
    """Validate phone number format"""
    pattern = r'^\+\d{1,15}$'
    if not re.match(pattern, phone_number):
        raise ValidationError(_('Phone number must be in format +1234567890'))
    return phone_number

def generate_unique_slug(model_class, title, slug_field='slug'):
    """Generate unique slug for model"""
    from django.utils.text import slugify
    
    base_slug = slugify(title)
    slug = base_slug
    counter = 1
    
    while model_class.objects.filter(**{slug_field: slug}).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    return slug
