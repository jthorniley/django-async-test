import asyncio
import threading
import time
from django.http import HttpResponse
from asgiref.sync import sync_to_async, async_to_sync
from app.models import MyModel
import logging

logger = logging.getLogger(__name__)


def sync_response():
    instance = MyModel.objects.create(current_time=int(time.time()))
    time.sleep(1)
    instance.save()
    return instance.current_time


@async_to_sync
async def task_runner():
    return await asyncio.create_task(sync_to_async(sync_response)())


# Create your views here.
def foo(request):
    logging.info("thread id %s", threading.current_thread())
    if request.GET.get("safe"):
        logging.info("performing safe request in thread %s", threading.current_thread())
        response = HttpResponse(sync_response())
        logging.info("finished %s", threading.current_thread())
        return response
    logging.info("performing unsafe request in thread %s", threading.current_thread())
    response = HttpResponse(task_runner())
    logging.info("finished %s", threading.current_thread())
    return response
