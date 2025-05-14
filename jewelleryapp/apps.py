from django.apps import AppConfig

class JewelleryappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'jewelleryapp'

    def ready(self):
        import jewelleryapp.signals
