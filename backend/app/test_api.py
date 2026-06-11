"""Test login + /me from inside the container using stdlib."""
import asyncio
import json
from urllib.parse import urlencode


async def test():
    import urllib.request

    data = json.dumps({"email": "admin@activia-trace.com", "password": "admin123"}).encode()

    req = urllib.request.Request(
        "http://localhost:8000/api/auth/login",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    loop = asyncio.get_event_loop()
    resp = await loop.run_in_executor(None, lambda: urllib.request.urlopen(req))
    body = json.loads(resp.read())
    if "access_token" in body:
        print(f"Login OK: token={body['access_token'][:50]}...")
    else:
        print(f"Login FAILED: {body}")
        return

    req2 = urllib.request.Request(
        "http://localhost:8000/api/auth/me",
        headers={
            "Authorization": f"Bearer {body['access_token']}",
            "Content-Type": "application/json",
        },
    )
    resp2 = await loop.run_in_executor(None, lambda: urllib.request.urlopen(req2))
    body2 = json.loads(resp2.read())
    print(f"Me response: {json.dumps(body2, indent=2)}")


asyncio.run(test())
