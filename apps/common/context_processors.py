from django.conf import settings

def language_context(request):
    """Add language context to templates"""
    return {
        'LANGUAGES': settings.LANGUAGES,
        'LANGUAGE_CODE': settings.LANGUAGE_CODE,
        'current_language': getattr(request, 'LANGUAGE_CODE', settings.LANGUAGE_CODE)
    }
