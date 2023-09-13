from httpx import AsyncClient
import asyncio
import pathlib


async def run_test():
    async with AsyncClient(timeout=40) as client:
        requests = [client.request("GET", "http://localhost:8000/") for _ in range(200)]
        results = await asyncio.gather(*requests)

        for result in results:
            if result.status_code != 200:
                pathlib.Path("error.html").write_text(result.text)


asyncio.run(run_test())
