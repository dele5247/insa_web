from django.apps import AppConfig

class InsaConfig(AppConfig):
    name = 'insa'

    def ready(self):
        import insa.templatetags.menu_tags

