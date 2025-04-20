from django.core.management.base import BaseCommand
from tasks.models import Task
import time
import logging

# Get logger for this module
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Prints all tasks in the database every 10 seconds'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting to monitor tasks...')
        
        try:
            while True:
                tasks = Task.objects.all()
                if tasks:
                    for task in tasks:
                        logger.info(
                            f"Task: {task.title} - Duration: {task.duration} - "
                            f"Status: {task.status} - Created: {task.created_at}"
                        )
                else:
                    logger.info("No tasks found in the database")
                
                time.sleep(10)  # Wait for 10 seconds
                
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS('Stopped monitoring tasks'))