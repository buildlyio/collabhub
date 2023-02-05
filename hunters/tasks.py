from celery import shared_task
from .health_check import check_all_sites

@shared_task
def my_scheduled_job():
    check_all_sites()
