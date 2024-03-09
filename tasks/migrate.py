import requests, os, tarfile, glob  # boto3
from fastapi import HTTPException, status
from Celery import celery_app
from utils.download import download_mailbox
from authentication.schema import User
from config import settings

excluded_folders = ["trash", "junk"]


@celery_app.task(name="download")
def download_tar_file(username: str, auth_token: str):
    user_data = User(
        username=username,
        auth_token=auth_token
    )
    download_main = download_mailbox(user=user_data)
    if download_main:
        for folder in excluded_folders:
            download_mailbox(folder_name=folder, user=user_data)
    return user_data.username


@celery_app.task(name="extract")
def extract_to_storage(email: str):
    extraction_folder = os.path.join(settings.EXTRACTION_FOLDER, email)

    # Check if the extraction folder exists
    if not os.path.exists(settings.EXTRACTION_FOLDER):
        print(f"Extraction folder '{settings.EXTRACTION_FOLDER}' does not exist. Stopping extraction.")
        return None

    file_pattern = os.path.join(settings.DOWNLOAD_FOLDER, f"{email}*.tgz")

    for file_path in glob.glob(file_pattern):
        try:
            with tarfile.open(file_path, 'r:gz') as mailbox:
                mailbox.extractall(f"{settings.EXTRACTION_FOLDER}/nss2022_emma@ytgqc.onmicrosoft.com")
        except tarfile.ReadError as e:
            print(f"Error reading tar archive '{file_path}': {e}")
        except Exception as e:
            raise e
    return email


@celery_app.task(queue="worker")
def cleanup(email: str):
    file_pattern = os.path.join(settings.DOWNLOAD_FOLDER, f"{email}*.tgz")
    # for file_path in glob.glob(file_pattern):
    #     try:
    #         os.remove(file_path)  # Delete the file
    #     except Exception as e:
    #         # Handle the exception (e.g., log the error)
    #         raise e
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
