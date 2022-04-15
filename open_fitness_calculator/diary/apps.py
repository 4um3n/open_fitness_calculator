from django.apps import AppConfig


class DiaryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'open_fitness_calculator.diary'

    def ready(self):
        from open_fitness_calculator.diary import signals
