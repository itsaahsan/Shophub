import asyncio, httpx

# More candidates for broken categories
CANDIDATES = [
    # Sports/fitness
    "1534438327276-14e5300c3a48",  # dumbbells (known working)
    "1517963879433-6ad2b056d712",  # gym
    "1571019613454-1cb2f99b2d8b",  # running
    "1540497077202-7c8a3999166f",  # fitness
    "1599058917212-d750089bc07e",  # yoga mat
    # Books
    "1512820790803-83ca734da794",  # books (known)
    "1495446815901-a7297e633e8d",  # books (known)
    "1507842217343-583bb7270b66",  # library (known)
    "1524578271613-d550eacf6090",  # bookshelf (known)
    "1497633762265-9d179a990aa6",  # books stack
    "1544716278-ca5e3f4abd8c",    # reading
    "1476275466078-f5ba73f3145c",  # book pages
    # Beauty/perfume
    "1596462502278-27bfdc403348",  # makeup (known)
    "1556228578-8c89e6adf883",    # skincare (known)
    "1522337360788-8b13dee7a37e",  # hair styling (known)
    "1571781926291-c477ebfd024b",  # perfume
    "1588405748880-12d1d2a59f75",  # perfume bottles
    "1512496015851-a90fb38ba796",  # cosmetics
    # Automotive
    "1600585154340-be6161a56a0c",  # car (known)
    "1494976388531-d1058494cdd8",  # car
    "1503376780353-7e6692767b70",  # car interior
    "1549399542-7e3f8b79c341",    # car
    # Kitchen/home
    "1484154218962-a197022b5858",  # kitchen (known)
    "1556228578-8c89e6adf883",    # (known)
    "1556909172-54557c7e4fb7",    # cooking
    "1556910103-1c02745aae4d",    # kitchen tools
    "1585771724684-38930d459fd2",  # air purifier  
    "1507089947368-19c1da9775ae",  # kitchen
    "1556909211-36987daf7b4d",    # kitchen items
    # Toys/games
    "1585386959984-a4155224a1ad",  # controller (known)
    "1606144042614-b2417e99c4e3",  # PS5 (known)
    "1558060106-2d2d64f9eaaf",    # board game
    "1566576912321-d58ddd7a6088",  # toys
    "1563396983906-b3795482a59a",  # lego
    # Gaming
    "1606144042614-b2417e99c4e3",  # PS5 (known)
    "1585386959984-a4155224a1ad",  # controller (known)
    "1542751371-adc38448a05e",    # gaming setup
    "1593305841991-05c297ba4575",  # PC gaming
    # Office
    "1531346878377-a5be20888e57",  # notebook (known)
    "1587829741301-dc798b83add3",  # keyboard (known)
    "1558494949-ef010cbdcc31",    # tech (known)
    "1497032628192-86f99bcd76bc",  # desk
    "1519219788971-8d9797e0928e",  # office
    # Grocery
    "1509042239860-f550ce710b93",  # coffee (known)
    "1602143407151-7111542de6e8",  # water bottle (known)
    "1506905925346-21bda4d32df4",  # food
    "1498837167922-ddd27525d352",  # fruits
    "1504674900247-0877df9cc836",  # food platter
]

async def check():
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
        unique_ids = list(set(CANDIDATES))
        await asyncio.gather(*[check_one(id) for id in unique_ids])
    
    for id in sorted(results.keys()):
        status = "OK" if results[id] else "BROKEN"
        print(f"  {status}: {id}")

asyncio.run(check())
