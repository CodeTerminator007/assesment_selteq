import logging
from celery import shared_task
from .models import Task
from django.contrib.auth import get_user_model

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

@shared_task
def print_user1_tasks():
    """
    Celery task that prints tasks for user with ID 1 every minute
    """
    User = get_user_model()
    user_1 = User.objects.filter(id=1).first()
    
    if not user_1:
        logger.info("User with ID 1 not found")
        return
    
    tasks = Task.objects.filter(user=user_1)
    
    if tasks:
        for task in tasks:
            logger.info(
                f"User 1 Task: {task.title}\n"
                f"Duration: {task.duration}\n"
                f"Created: {task.created_at}\n"
                "------------------------"
            )
    else:
        logger.info("No tasks found for User 1")