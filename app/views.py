import asyncio
import threading
import time
from asgiref.local import Local
from django.http import HttpResponse
from asgiref.sync import sync_to_async, async_to_sync
from app.models import MyModel
import logging

logger = logging.getLogger(__name__)


def sync_response(request, asgiref_local):
    asgiref_local.foo = 4
    logging.info(
        f"REQUEST ID: {id(request):10d} sync_response thread {threading.current_thread()}"
    )
    instance = MyModel.objects.create(current_time=int(time.time()))
    time.sleep(1)
    instance.save()
    return instance.current_time


@async_to_sync
async def async_response(request, asgiref_local):
    asgiref_local.foo = 3
    logging.info(
        f"REQUEST ID: {id(request):10d} async_response thread {threading.current_thread()}"
    )
    instance = await MyModel.objects.acreate(current_time=int(time.time()))
    await asyncio.sleep(1)
    return instance.current_time


@async_to_sync
async def task_runner(request, asgiref_local):
    asgiref_local.foo = 2
    logging.info(
        f"REQUEST ID: {id(request):10d} task_runner thread {threading.current_thread()}"
    )
    return await asyncio.create_task(
        sync_to_async(sync_response)(request, asgiref_local)
    )


# Create your views here.
def foo(request):
    logging.info(f"REQUEST ID: {id(request):10d} {threading.current_thread()}")

    MyModel.objects.create(current_time=int(time.time()))
    asgiref_local = Local(thread_critical=True)
    # asgiref_local.foo = 1

    if request.GET.get("safe"):
        # If requested, perform request in pure sync context
        logging.info(f"REQUEST ID: {id(request):10d}   safe option set")
        response = HttpResponse(sync_response(request, asgiref_local))
        logging.info(
            f"REQUEST ID: {id(request):10d}   done - local value: {getattr(asgiref_local, 'foo', 'notset')}"
        )
        return response

    if request.GET.get("notask"):
        # If requested, perform request in async thread without creating a separate task
        logging.info(f"REQUEST ID: {id(request):10d}   no task option set")
        response = HttpResponse(async_response(request, asgiref_local))
        logging.info(
            f"REQUEST ID: {id(request):10d}   done - local value: {getattr(asgiref_local, 'foo', 'notset')}"
        )
        return response

    # Default: we wrap the sync_response work function in:
    #  -> async_to_sync(task_runner)   === running in a thread created by async_to_sync
    #  -> asyncio.create_task()        === creates a new asyncio.Task instance
    #  -> sync_to_async(sync_response) === should run in this thread (sync_to_async finds the sync thread above it in the stack)
    response = HttpResponse(task_runner(request, asgiref_local))
    logging.info(
        f"REQUEST ID: {id(request):10d}   done - local value: {getattr(asgiref_local, 'foo', 'notset')}"
    )
    return response
