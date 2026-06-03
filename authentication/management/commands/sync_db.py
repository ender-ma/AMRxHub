import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from django.db import connections

class Command(BaseCommand):
    help = 'Sync data from MySQL to SQLite'
    
    def handle(self, *args, **options):
        # Export data from MySQL
        self.stdout.write('Exporting data from MySQL...')
        call_command('dumpdata', 
                    '--database=default',
                    '--exclude=contenttypes',
                    '--exclude=auth.permission',
                    '--exclude=sessions.session',
                    '--output=mysql_data.json')
        
        # Switch to SQLite and import
        self.stdout.write('Importing data to SQLite...')
        call_command('loaddata', 'mysql_data.json', '--database=default')
        
        self.stdout.write(self.style.SUCCESS('Database sync completed!'))