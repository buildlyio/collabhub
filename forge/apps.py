from django.apps import AppConfig


class ForgeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'forge'
    verbose_name = 'Buildly Forge Marketplace'
    
    def ready(self):
        """Import signals when app is ready"""
        try:
            import forge.signals  # noqa F401
        except ImportError:
            pass
