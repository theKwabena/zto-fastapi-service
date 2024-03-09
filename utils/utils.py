import requests
from fastapi import Request, HTTPException, status
from fastapi.security.utils import get_authorization_scheme_param
from celery.result import AsyncResult
from Celery import celery_app


def check_mailbox_size(url):
    # Send a HEAD request to retrieve metadata, including content length
    response = requests.head(url, allow_redirects=False)
    if response.status_code == 200:
        # Check if the 'Content-Length' header is present in the response
        if 'Content-Length' in response.headers:
            return int(response.headers['Content-Length'])
    return None


async def get_auth_token(request: Request):
    auth_token = request.headers.get("Authorization").split()
    print(auth_token)
    if len(auth_token) != 2 or auth_token[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    return auth_token[1]


async def get_auth_token_from_cookie(request: Request):
    token: str = request.cookies.get("access_token")  # changed to accept access token from httpOnly Cookie
    print("access_token is", token)

    scheme, param = get_authorization_scheme_param(token)
    if not token or scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return param


def check_tasks_exit(username):
    def generate_task_id(prefix):
        return f'{prefix}-{username}'

    # Generate task IDs
    task_id_dw = generate_task_id('dt')
    task_id_ew = generate_task_id('et')

    # Check task existence using result backend
    task_dw_result = AsyncResult(task_id_dw).state
    task_ew_result = AsyncResult(task_id_ew).state
    print(task_ew_result, task_dw_result)

    # Check if tasks exist
    task_id_dw_exists = task_dw_result != 'PENDING'
    task_id_ew_exists = task_ew_result != 'PENDING'

    return task_id_dw if task_id_dw_exists else None, task_id_ew if task_id_ew_exists else None
