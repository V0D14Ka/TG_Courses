from celery import Celery

celery = Celery('tasks')
celery.autodiscover_tasks()


@celery.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
