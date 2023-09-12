import asyncio
import time
from django.http import HttpResponse
from asgiref.sync import sync_to_async, async_to_sync
from app.models import MyModel


@sync_to_async
def sub_task():
    instance = MyModel.objects.create(current_time=int(time.time()))
    return instance.current_time


@async_to_sync
async def task_runner():
    return await asyncio.create_task(sub_task())


# Create your views here.
def foo(request):
    return HttpResponse(task_runner())
