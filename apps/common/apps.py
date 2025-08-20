from django.apps import AppConfig

class CommonConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.common'
    
    def ready(self):
        # Import translation modules to register them
        try:
            pass
        except ImportError:
            pass
