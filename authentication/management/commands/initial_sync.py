from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Initial sync from MySQL to SQLite'
    
    def handle(self, *args, **options):
        # Temporarily set to use MySQL
        old_use_sqlite = os.environ.get('USE_SQLITE')
        os.environ['USE_SQLITE'] = 'False'
        
        # Export from MySQL
        self.stdout.write('Exporting from MySQL...')
        call_command('dumpdata', 
                    '--exclude=contenttypes',
                    '--exclude=auth.permission',
                    '--exclude=sessions.session',
                    '--output=sync_data.json')
        
        # Switch to SQLite
        os.environ['USE_SQLITE'] = 'True'
        
        # Ensure SQLite has proper structure
        call_command('migrate')
        
        # Import to SQLite
        self.stdout.write('Importing to SQLite...')
        call_command('loaddata', 'sync_data.json')
        
        # Restore original setting
        if old_use_sqlite:
            os.environ['USE_SQLITE'] = old_use_sqlite
        else:
            del os.environ['USE_SQLITE']
        
        self.stdout.write(self.style.SUCCESS('Initial sync completed!'))