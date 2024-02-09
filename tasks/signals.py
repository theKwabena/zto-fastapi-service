from celery.signals import after_task_publish, task_success, task_failure, before_task_publish
from tasks.migrate import add_mistake, extract_to_storage, cleanup


# @task_success.connect()
# def download_tar_success(sender, headers=None, body=None, **kwargs):
#     if sender.name == "download":
#         if kwargs['result']:
#             pass
#             # extract_to_storage.delay(kwargs['result'])
#
#     if sender.name == "extract":
#         if kwargs['result']:
#             pass
#             # cleanup(kwargs['result'])
#     print(f"Executing this to show that task has been sent{sender.name}, {kwargs} {body}, {headers}")


@task_failure.connect()
def extract_failure(sender=extract_to_storage, body=None, headers=None, **kwargs):
    print("Task failed")
