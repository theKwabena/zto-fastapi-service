import requests
from fastapi import APIRouter, status, HTTPException
from tasks.migrate import cleanup, extract_to_storage, download_tar_file
from utils.utils import check_mailbox_size
from celery import chain

router = APIRouter()

on_prem_mail = "https://mail.knust.edu.gh/"
another_mail = "https://apps.knust.edu.gh/students"


@router.get("/login", status_code=status.HTTP_200_OK)
async def extract(username: str, password: str):
    # TODO  Authenticate user with Zimbra SOAP API

    # Check the size of the user's mailbox
    mailbox_size = check_mailbox_size(f"{on_prem_mail}/home/{username}/?fmt=tgz&auth=sc", auth=(username, password))

    if mailbox_size and  mailbox_size <= 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Mailbox size too huge, please try the manual method')

    # Chain download tasks together so they executed once they are done.
    task = chain(
        download_tar_file.s(username, password).set(countdown=30),
        extract_to_storage.s().set(countdown=30),
        cleanup.s()
    )()
    # if not task.get():
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail=f"""Please check email and password and try again"""
    #     )
    task_ids = {
        "download" : task.parent.parent.id,
        "extract" : task.parent.id
    }
    return {f"Mailbox download started: dt_id={task_ids['download']}&et_id={task_ids['extract']}"}
