# apps/store/utils.py
from django.utils.text import slugify

def generate_unique_slug(instance, value, slug_field='slug'):
    slug = slugify(value)
    Klass = instance.__class__
    counter = 1
    unique_slug = slug
    while Klass.objects.filter(**{slug_field: unique_slug}).exists():
        unique_slug = f"{slug}-{counter}"
        counter += 1
    return unique_slug
