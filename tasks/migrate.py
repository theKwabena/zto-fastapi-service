import requests, os, tarfile, glob  # boto3
from fastapi import HTTPException, status
from Celery import celery_app
from utils.download import download_mailbox

zimbra_mail = os.getenv("ZIMBRA_MAIL", 'https://mail.knust.edu.gh')
download_folder = "/home/data/mailbox-downloads"
mailboxes_folder = os.path.expanduser("/home/data/mailbox-extracts")

excluded_folders = ["trash", "junk"]


@celery_app.task(name="download")
def download_tar_file(email: str, password: str):
    user_data = {
        'email': email,
        'password': password
    }
    download_main = download_mailbox(user=user_data)
    if download_main:
        for folder in excluded_folders:
            download_mailbox(folder_name=folder, user=user_data)
    return user_data['email']


@celery_app.task(name="extract")
def extract_to_storage(email: str):
    file_pattern = os.path.join(download_folder, f"{email}*.tgz")
    for file_path in glob.glob(file_pattern):
        try:
            with tarfile.open(file_path, 'r:gz') as mailbox:
                mailbox.extractall(f"{mailboxes_folder}/{email}")
        except Exception as e:
            raise e
    return email


@celery_app.task
def cleanup(email: str):
    file_pattern = os.path.join(download_folder, f"{email}*.tgz")
    for file_path in glob.glob(file_pattern):
        try:
            os.remove(file_path)  # Delete the file
        except Exception as e:
            # Handle the exception (e.g., log the error)
            raise e
    return "Cleanup done"


@celery_app.task
def add_mistake(a, b):
    try:
        result = a / b
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed, Message {e}"
        )
