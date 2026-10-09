import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'navratri_project.settings')

application = get_wsgi_application()

# Automatically run database migrations & setup on server startup
try:
    from django.core.management import call_command
    call_command('migrate', interactive=False, run_syncdb=True)
    call_command('init_setup', interactive=False)
except Exception as e:
    import logging
    logging.getLogger(__name__).warning("Startup auto-migration notice: %s", e)
