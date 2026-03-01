import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
async def main():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        r = await client.get('/health')
        print(r.status_code, r.json())
asyncio.run(main())
