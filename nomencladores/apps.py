from django.apps import AppConfig


class NomencladoresConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'nomencladores'

    def ready(self):
        import os
        from django.core.management import call_command
        # TODO:ONLY WORKS AFTER THE SECOND MIGRATE COMMENT IN THE FIRST
        if os.environ.get('RUN_MAIN', None) != 'true':
            call_command('populate_locations')
