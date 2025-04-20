from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from tasks.models import Task
from datetime import timedelta

class Command(BaseCommand):
    help = 'Initialize database with superuser and sample task'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Create superuser if not exists
        if not User.objects.filter(email='admin@admin.com').exists():
            self.stdout.write('Creating superuser...')
            superuser = User.objects.create_superuser(
                username='admin',
                email='admin@admin.com',
                password='admin'
            )
            
            # Create a sample task for the superuser
            self.stdout.write('Creating sample task...')
            Task.objects.create(
                title='Sample Admin Task',
                duration=timedelta(hours=2),
                status='pending',
                user=superuser
            )
            
            self.stdout.write(self.style.SUCCESS('Successfully initialized database'))
        else:
            self.stdout.write('Superuser already exists')