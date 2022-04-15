from django.apps import AppConfig


class ProfilesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'open_fitness_calculator.profiles'

    def ready(self):
        from open_fitness_calculator.profiles import signals
