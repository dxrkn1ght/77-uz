import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

def validate_phone_number(phone_number):
    """Validate phone number format"""
    pattern = r'^\+\d{1,15}$'
    if not re.match(pattern, phone_number):
        raise ValidationError(_('Phone number must be in format +1234567890'))
    return phone_number

def validate_no_html(value):
    """Prevent HTML injection in text fields"""
    html_pattern = r'<[^>]*>'
    if re.search(html_pattern, value):
        raise ValidationError(_('HTML tags are not allowed'))
    return value

def validate_no_script(value):
    """Prevent script injection"""
    script_patterns = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'vbscript:',
        r'onload\s*=',
        r'onerror\s*=',
        r'eval\s*\(',
    ]
    
    for pattern in script_patterns:
        if re.search(pattern, value, re.IGNORECASE):
            raise ValidationError(_('Script content is not allowed'))
    
    return value

def validate_file_size(file):
    """Validate uploaded file size"""
    max_size = 10 * 1024 * 1024  # 10MB
    if file.size > max_size:
        raise ValidationError(_('File size cannot exceed 10MB'))
    return file

def validate_image_file(file):
    """Validate image file type"""
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if file.content_type not in allowed_types:
        raise ValidationError(_('Only JPEG, PNG, GIF, and WebP images are allowed'))
    return file

# Regex validators
phone_validator = RegexValidator(
    regex=r'^\+\d{1,15}$',
    message=_('Phone number must be in format +1234567890')
)

slug_validator = RegexValidator(
    regex=r'^[-a-zA-Z0-9_]+$',
    message=_('Slug can only contain letters, numbers, hyphens, and underscores')
)
