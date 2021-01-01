from django.apps import AppConfig


class MainAppConfig(AppConfig):
    name = 'main_app'
    def ready(self):
        from scheduler import scheduler
        scheduler.start()
