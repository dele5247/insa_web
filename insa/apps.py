from django.apps import AppConfig
from django.conf import settings

class InsaConfig(AppConfig):
    name = 'insa'

    def ready(self):
        import insa.templatetags.menu_tags
