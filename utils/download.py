import os
import requests
from .customExceptions import CustomHttpException
from authentication.schema import User
from config import settings


[os.makedirs(folder, exist_ok=True) for folder in [settings.DOWNLOAD_FOLDER, settings.EXTRACTION_FOLDER]]


def download_mailbox(*, folder_name: str or None = '', user: User):
    folder_request = requests.get(
        f"{settings.ZIMBRA_SERVER_URL}/home/{user.username}/{folder_name}/?fmt=tgz&auth=qp&zauthtoken={user.auth_token}",
        allow_redirects=False
    )
    print(folder_request.url)
    if folder_request.status_code == 200 or 204:
        folder_file_path = os.path.join(
            settings.DOWNLOAD_FOLDER,
            f"{user.username}-{folder_name}.tgz") if folder_name \
            else os.path.join(settings.DOWNLOAD_FOLDER, f"{user.username}.tgz")

        try:
            with open(folder_file_path, 'wb') as file:
                for chunk in folder_request.iter_content(chunk_size=1024):
                    file.write(chunk)
        except Exception as e:
            raise e
        return folder_file_path
    else:
        raise CustomHttpException(
            f"An error occurred downloading mailbox {folder_request.text}",
            folder_request.status_code
        )
        # Handle error or log it

