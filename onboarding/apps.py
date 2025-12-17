from django.apps import AppConfig


class OnboardingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'onboarding'
    
    def ready(self):
        """Import signals when the app is ready"""
        import onboarding.signals  # noqa
