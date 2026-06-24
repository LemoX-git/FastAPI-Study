from fastapi import FastAPI
from celery import Celery
from task import call_background_task

app = FastAPI()

celery = Celery(
    __name__,
    broker='redis://127.0.0.1:6379/0',
    backend='redis://127.0.0.1:6379/0',
    broker_connection_retry_on_startup=True
)


@app.get("/")
async def hello_world(message: str):
    call_background_task.apply_async(args=[message], countdown=60*5)
    return {'message': 'Hello World!'}
