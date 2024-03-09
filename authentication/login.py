import requests

from fastapi import APIRouter, status, HTTPException, Request, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm
from tasks.migrate import cleanup, extract_to_storage, download_tar_file
from utils.utils import check_mailbox_size, get_auth_token_from_cookie
from typing import Annotated, Any
from celery import chain

from config import OAuth2PasswordBearerWithCookie, create_access_token
from .schema import UserLogin, User, Token
from config import settings
from utils.utils import check_tasks_exit

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/access-token")

on_prem_mail = "https://mail.knust.edu.gh/"
another_mail = "https://apps.knust.edu.gh/students"


# @router.post("/login", status_code=status.HTTP_200_OK)
# async def login(user: UserLogin):
#     auth = requests.get(f"{settings.ZIMBRA_SERVER_URL}/home/{user.username}/rss/?fmt=sync&auth=sc",
#                         auth=(user.username, user.password))
#
#     if not auth.status_code == 404:
#         raise HTTPException(
#             status_code=auth.status_code,
#             detail=auth.text
#         )
#
#     cookie = auth.cookies.get_dict()
#     return cookie['ZM_AUTH_TOKEN']


@router.post("/access-token", status_code=status.HTTP_200_OK)
async def login_user(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    auth = requests.get(f"{settings.ZIMBRA_SERVER_URL}/home/{form_data.username}/rss/?fmt=sync&auth=sc",
                        auth=(form_data.username, form_data.password))

    if not auth.status_code == 404:
        raise HTTPException(
            status_code=auth.status_code,
            detail=auth.text
        )

    cookie = auth.cookies.get_dict()

    download_id, extract_id = check_tasks_exit(form_data.username)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {cookie['ZM_AUTH_TOKEN']}",
        samesite='lax',
        expires=60 * 60 * 24,
        httponly=True
    )
    return {
        'user': form_data.username,
        'dt_id' : download_id,
        'et_id' : extract_id
    }


@router.get("/begin-migration", status_code=status.HTTP_200_OK)
async def extract(username: str, token: Annotated[str, Depends(oauth2_scheme)], ):
    # TODO  Authenticate user with Zimbra SOAP API
    dt_id, et_id = check_tasks_exit(username)

    if dt_id or et_id:
        print("I return and he doesn't 1")
        return {
            "dt_id" : f"dt-{username}",
            "et_id" : f"ft-{username}"
        }

    print("I run too")
    # Check the size of the user's mailbox
    mailbox_size = check_mailbox_size(
        f"{on_prem_mail}/home/{username}/?fmt=tgz&auth=qp&zauthtoken={token}"
    )

    if mailbox_size and mailbox_size <= 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Mailbox size too huge, please refer to the manual method')

    # Chain download tasks together so they executed once they are done.
    task = chain(
        download_tar_file.s(username, token).set(task_id=f"dt-{username}"),
        extract_to_storage.s().set(task_id=f"et-{username}"),
        cleanup.s()
    )()
    task_ids = {
        "download": task.parent.parent.id,
        "extract": task.parent.id
    }

    return {"dt_id": task_ids['download'], "et_id": task_ids['extract']}


@router.get("/trial")
async def try_token(token: Annotated[str, Depends(oauth2_scheme)], request: Request):
    auth_token = request.headers.get("Authorization").split()[1]
    return {"token": token}


@router.get('/me')
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], username: str):
    auth = requests.get(
        f"{settings.ZIMBRA_SERVER_URL}/home//home/{username}/rss/?fmt=sync&auth=qp&zauthtoken={token}"
    )
    print(auth.status_code)
    if not auth.status_code == 404:
        raise HTTPException(
            status_code=auth.status_code,
            detail=auth.text
        )
    return {
        'username': username
    }
