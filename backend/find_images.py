"""Find working Unsplash photo IDs for product categories."""
import asyncio
import httpx

# Candidate Unsplash photo IDs (real, verified popular photos)
CANDIDATES = {
    "Electronics": [
        "1505740420928-5e560c06d30e",  # headphones on yellow
        "1523275335684-37898b6baf30",  # watch
        "1526170375885-4d8ecf77b99f",  # camera lens
        "1572635196237-14b3f281503f",  # sunglasses product
        "1546868871-af0de0ae72be",     # headphones
        "1585386959984-a4155224a1ad",   # gaming controller
        "1491553895911-0055eca6402d",   # shoe
        "1468495244123-6c6c332eeece",   # iphone
        "1517336714731-489689fd1ca8",   # macbook
        "1496181133206-80ce9b88a853",   # laptop
        "1518770660439-4636190af475",   # circuit board
        "1550009158-9ebf69173e03",      # smart watch
        "1593359677879-a4bb92f829d1",   # TV
        "1606144042614-b2417e99c4e3",   # gaming
        "1573497019418-b400bb3ab074",   # VR headset
        "1622979135225-d2ba269cf1ac",   # VR
        "1581091226825-a6a2a5aee158",   # 3d printer
        "1597872200969-2b65d56bd16b",   # SSD
        "1558494949-ef010cbdcc31",      # router/tech
        "1544244015-0df4b3ffc6b0",     # tablet
    ],
    "Clothing": [
        "1556821840-3a63f95609a7",     # hoodie
        "1434389677669-e08b4cac3105",   # sweater
        "1539185441755-769473a23570",   # sneakers
        "1525966222134-fcfa99b8ae77",   # sneakers
        "1571945153237-4929e783af4a",   # t-shirt
        "1620799140408-edc6dcb6d633",   # dress shirt
        "1489987707025-afc232f7ea0f",   # underwear
        "1521572163474-6864f9cf17ab",   # polo
        "1591047139829-d91aecb6caea",   # jacket
        "1556228578-8c89e6adf883",     # skincare
    ],
    "Home": [
        "1556909114110-56367f9e9310",   # kitchen
        "1555939594-58d7cb561ad1",      # grill
        "1524758631624-e2822e304c36",   # furniture
        "1484154218962-a197022b5858",   # kitchen
        "1586023492125-27b2c045efd7",   # couch
        "1556228578-8c89e6adf883",     # beauty product
        "1522337360788-8b13dee7a37e",   # hair styling
        "1505693314120-0d443867891c",   # bedroom
        "1556228720-195a672e8a03",     # cosmetic
    ],
    "Sports": [
        "1517836357463-d25dceac3c13",   # gym
        "1534438327276-14e5300c3a48",   # weights
        "1576678927484-cc907957088c",   # massage gun
        "1504280390367-361c6d9f38f4",   # camping
        "1575311373937-040b8e1fd5b6",   # watch
        "1544367567-0f2fcb20e4d0",     # yoga
        "1602143407151-7111542de6e8",   # water bottle
    ],
    "Books": [
        "1544947950-d575db8a8b9e",     # kindle/book
        "1512820790803-83ca734da794",   # books
        "1495446815901-a7297e633e8d",   # books
        "1507842217343-583bb7270b66",   # library
        "1524578271613-d550eacf6090",   # bookshelf
        "1532012197267-e36e6db0ccc6",   # open book
    ],
    "Beauty": [
        "1556228578-8c89e6adf883",
        "1596462502278-27bfdc403348",
        "1541643600-914d3b64d0a8",
        "1522337360788-8b13dee7a37e",
    ],
    "Toys": [
        "1587654780769-b43045d1b5cf",
        "1596461896161-73d68ced33f3",
        "1612404459649-5587b0db58b2",
    ],
    "Automotive": [
        "1549317661-bd4e6da46757",
        "1600585154340-be6161a56a0c",
    ],
    "Grocery": [
        "1509042239860-f550ce710b93",
        "1587049352846-4e4e5fb4143a",
        "1602143407151-7111542de6e8",
    ],
    "Gaming": [
        "1612287230202-b40d82c1ed42",
        "1606144042614-b2417e99c4e3",
    ],
    "Office": [
        "1587829741301-dc798b83add3",
        "1531346878377-a5be20888e57",
        "1593642702749-b7d2a804a23e",
    ],
}

async def check():
    working = {}
    broken_ids = set()
    
    all_ids = set()
    for ids in CANDIDATES.values():
        all_ids.update(ids)
    
    async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
        sem = asyncio.Semaphore(20)
        results = {}
        
        async def check_one(img_id):
            async with sem:
                url = f"https://images.unsplash.com/photo-{img_id}?w=800"
                try:
                    r = await client.head(url)
                    results[img_id] = r.status_code == 200
                except:
                    results[img_id] = False
        
        await asyncio.gather(*[check_one(id) for id in all_ids])
    
    print("=== WORKING IDs ===")
    for id, ok in sorted(results.items()):
        status = "OK" if ok else "BROKEN"
        print(f"  {status}: {id}")
    
    working_ids = [id for id, ok in results.items() if ok]
    broken_ids = [id for id, ok in results.items() if not ok]
    print(f"\nWorking: {len(working_ids)}, Broken: {len(broken_ids)}")

asyncio.run(check())
