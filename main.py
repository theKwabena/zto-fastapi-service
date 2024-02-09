import time, asyncio

from fastapi import FastAPI, WebSocket, Request
from sse_starlette import EventSourceResponse
from fastapi.middleware.cors import CORSMiddleware
from authentication.login import router as LoginRouter
from celery.result import AsyncResult
from pydantic import BaseModel


class Tasks(BaseModel):
    download_id: str
    extract_id: str


app = FastAPI()

allowed_origins = ['localhost:5173']

MESSAGE_STREAM_DELAY = 1  # second
MESSAGE_STREAM_RETRY_TIMEOUT = 15000  # milisecond

# add CORS so our web page can connect to our api
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

COUNTER = 0


def get_message(task : Tasks):
    result = {
        "download" : AsyncResult(task.download_id).state,
        "extract" : AsyncResult(task.extract_id).state
    }
    return result


@app.get("/stream/")
async def message_stream(request: Request, dt_id: str, et_id: str):
    async def event_generator():
        while True:
            if await request.is_disconnected():
                print("Request disconnected")
                break
            # Checks for new messages and return them to client if any
            task = Tasks(download_id=dt_id, extract_id=et_id)
            print(task.download_id, task.extract_id)
            status = get_message(task)
            if status:
                yield {
                    "event": "new_message",
                    "id": "message_id",
                    "retry": MESSAGE_STREAM_RETRY_TIMEOUT,
                    "data": f"Task status {status}",
                }
            else:
                yield {
                    "event": "end_event",
                    "id": "message_id",
                    "retry": MESSAGE_STREAM_RETRY_TIMEOUT,
                    "data": "End of the stream",
                }
            await asyncio.sleep(MESSAGE_STREAM_DELAY)

    return EventSourceResponse(event_generator())


app.include_router(LoginRouter)
