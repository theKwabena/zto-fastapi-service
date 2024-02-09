import os
import requests
from .customExceptions import CustomHttpException

zimbra_mail = os.getenv("ZIMBRA_MAIL", 'https://mail.knust.edu.gh')
download_folder = "/home/data/mailbox-downloads"
mailboxes_folder = os.path.expanduser("/home/data/mailbox-extracts")


[os.makedirs(folder, exist_ok=True) for folder in [download_folder, mailboxes_folder]]


def download_mailbox(*, folder_name: str or None = '', user: dict):
    folder_request = requests.get(
        f"{zimbra_mail}/home/{user['email']}/{folder_name}?fmt=tgz&auth=sc",
        auth=(user['email'], user['password']),
        allow_redirects=False
    )

    if folder_request.status_code == 200:
        folder_file_path = os.path.join(
            download_folder,
            f"{user['email']}-{folder_name}.tgz") if folder_name \
            else os.path.join(download_folder, f"{user['email']}.tgz"
            )

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

