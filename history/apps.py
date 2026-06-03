from django.apps import AppConfig

class HistoryConfig(AppConfig):
    name = 'history'

    def ready(self):
        import history.models  # Ensures signals are connected