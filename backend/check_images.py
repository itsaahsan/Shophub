"""Check which Unsplash image URLs in the seed data are valid (HTTP 200)."""
import asyncio
import httpx
from seed_products import PRODUCTS

async def check():
    broken = []
    async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
        sem = asyncio.Semaphore(20)
        async def check_one(i, url):
            async with sem:
                try:
                    r = await client.head(url)
                    if r.status_code != 200:
                        broken.append((i, url, r.status_code))
                except Exception as e:
                    broken.append((i, url, str(e)))
        tasks = []
        for i, p in enumerate(PRODUCTS):
            if p["images"]:
                tasks.append(check_one(i, p["images"][0]))
        await asyncio.gather(*tasks)
    
    print(f"\nTotal products: {len(PRODUCTS)}")
    print(f"Broken images: {len(broken)}")
    # Collect unique broken image IDs
    ids = set()
    for i, url, code in broken:
        img_id = url.split("photo-")[1].split("?")[0] if "photo-" in url else url
        ids.add(img_id)
    print(f"Unique broken photo IDs: {len(ids)}")
    for img_id in sorted(ids):
        print(f"  {img_id}")

asyncio.run(check())
