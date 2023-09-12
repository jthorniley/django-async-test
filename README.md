# Django/asgiref sync deadlock test

This is a minimal django project that tests for an async deadlock bug.

The server has one view at the root level that returns the current time stamp.

When working, `http://localhost:8000/` should show the current unix time.

## Test set up

Assuming you have poetry installed

    poetry install
    poetry run python manage.py migate

## Run with WSGI

Using WSGI the server currently works:

    poetry run gunicorn --bind 0.0.0.0:8000 django_async_test.wsgi

Navigate to `http://localhost:8000/` and the current timestamp should be displayed

## Run with ASGI

The bug manifests with ASGI server. Use either the daphne or uvicorn ASGI process:

    poetry run daphne --bind 0.0.0.0 --port 8000 django_async_test.asgi:application

or

    poetry run uvicorn --host 0.0.0.0 --port 8000 django_async_test.asgi:application

Navigate to `http://localhost:8000/` the current behaviour (with the pinned dependencies
installed by poetry) should be that the page load hangs (nothing returns). Additionally
CTRL-C will fail to terminate the server (this is due to a deadlocked thread which
doesn't get cleaned up). You will need to send a SIGKILL to the server process (e.g.
`kill -9 <pid>` etc).
