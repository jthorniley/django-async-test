import asyncio
import time
from django.http import HttpResponse
from asgiref.sync import sync_to_async, async_to_sync
from app.models import MyModel


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
    if request.GET.get("safe"):
        return HttpResponse(sync_response())
    return HttpResponse(task_runner())
