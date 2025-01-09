from celery import shared_task

@shared_task
def another_sample_task():
    return "This is a sample task from monica."
