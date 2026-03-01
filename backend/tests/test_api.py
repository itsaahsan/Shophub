"""Comprehensive API tests for all Shop Hub endpoints."""

import pytest
from tests.conftest import auth_cookies


# ──────────── Health ────────────

@pytest.mark.asyncio
async def test_health_check(client):
    res = await client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"


# ──────────── Auth ────────────

@pytest.mark.asyncio
async def test_signup_success(client):
    res = await client.post("/api/v1/auth/signup", json={
        "name": "New User",
        "email": "newuser_signup_test@test.com",
        "password": "StrongPass1",
    })
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "New User"
    assert data["email"] == "newuser_signup_test@test.com"
    assert "access_token" in res.cookies or "id" in data
    # Cleanup
    from app.core.database import get_db
    db = get_db()
    await db.users.delete_one({"email": "newuser_signup_test@test.com"})


@pytest.mark.asyncio
async def test_signup_duplicate_email(client, test_user):
    res = await client.post("/api/v1/auth/signup", json={
        "name": "Dup",
        "email": test_user["email"],
        "password": "StrongPass1",
    })
    assert res.status_code == 409


@pytest.mark.asyncio
async def test_signup_weak_password(client):
    res = await client.post("/api/v1/auth/signup", json={
        "name": "Weak",
        "email": "weakpass@test.com",
        "password": "123",
    })
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client, test_user):
    res = await client.post("/api/v1/auth/login", json={
        "email": test_user["email"],
        "password": "TestPass123",
    })
    assert res.status_code == 200
    assert res.json()["email"] == test_user["email"]


@pytest.mark.asyncio
async def test_login_wrong_password(client, test_user):
    res = await client.post("/api/v1/auth/login", json={
        "email": test_user["email"],
        "password": "WrongPassword",
    })
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client):
    res = await client.post("/api/v1/auth/login", json={
        "email": "nonexistent@test.com",
        "password": "password",
    })
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_me_authenticated(client, test_user):
    res = await client.get("/api/v1/auth/me", cookies=auth_cookies(test_user["token"]))
    assert res.status_code == 200
    assert res.json()["id"] == test_user["id"]


@pytest.mark.asyncio
async def test_me_unauthenticated(client):
    res = await client.get("/api/v1/auth/me")
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_logout(client, test_user):
    res = await client.post("/api/v1/auth/logout", cookies=auth_cookies(test_user["token"]))
    assert res.status_code == 200


# ──────────── Products ────────────

@pytest.mark.asyncio
async def test_list_products(client):
    res = await client.get("/api/v1/products")
    assert res.status_code == 200
    data = res.json()
    assert "products" in data
    assert "total" in data
    assert "page" in data
    assert "pages" in data


@pytest.mark.asyncio
async def test_list_products_with_pagination(client):
    res = await client.get("/api/v1/products?page=1")
    assert res.status_code == 200
    assert res.json()["page"] == 1


@pytest.mark.asyncio
async def test_list_products_with_sort(client):
    res = await client.get("/api/v1/products?sort=price_asc")
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_list_products_invalid_sort(client):
    res = await client.get("/api/v1/products?sort=invalid")
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_get_product(client, test_product):
    res = await client.get(f"/api/v1/products/{test_product['id']}")
    assert res.status_code == 200
    assert res.json()["name"] == "Test Product for Tests"


@pytest.mark.asyncio
async def test_get_product_not_found(client):
    from bson import ObjectId
    fake_id = str(ObjectId())
    res = await client.get(f"/api/v1/products/{fake_id}")
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_get_categories(client):
    res = await client.get("/api/v1/products/categories")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


@pytest.mark.asyncio
async def test_create_product_as_admin(client, admin_user):
    res = await client.post("/api/v1/products", json={
        "name": "Admin Created Product",
        "description": "This product was created by an admin in a test.",
        "price": 29.99,
        "category": "TestCategory",
        "stock": 10,
        "images": [],
    }, cookies=auth_cookies(admin_user["token"]))
    assert res.status_code == 201
    product_id = res.json()["id"]
    # Cleanup
    from app.core.database import get_db
    db = get_db()
    from bson import ObjectId
    await db.products.delete_one({"_id": ObjectId(product_id)})


@pytest.mark.asyncio
async def test_create_product_as_user_forbidden(client, test_user):
    res = await client.post("/api/v1/products", json={
        "name": "Forbidden Product",
        "description": "This should not be created by a regular user.",
        "price": 10,
        "category": "Test",
        "stock": 5,
        "images": [],
    }, cookies=auth_cookies(test_user["token"]))
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_create_product_unauthenticated(client):
    res = await client.post("/api/v1/products", json={
        "name": "No Auth Product",
        "description": "This should fail due to no auth.",
        "price": 10,
        "category": "Test",
        "stock": 5,
        "images": [],
    })
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_update_product_as_admin(client, admin_user, test_product):
    res = await client.put(f"/api/v1/products/{test_product['id']}", json={
        "price": 59.99,
    }, cookies=auth_cookies(admin_user["token"]))
    assert res.status_code == 200
    assert res.json()["price"] == 59.99


@pytest.mark.asyncio
async def test_delete_product_as_admin(client, admin_user):
    from app.core.database import get_db
    db = get_db()
    result = await db.products.insert_one({
        "name": "To Delete",
        "description": "This product will be deleted in tests.",
        "price": 1,
        "category": "TestCategory",
        "stock": 1,
        "images": [],
        "average_rating": 0,
        "review_count": 0,
        "created_at": "2024-01-01T00:00:00+00:00",
    })
    pid = str(result.inserted_id)
    res = await client.delete(f"/api/v1/products/{pid}", cookies=auth_cookies(admin_user["token"]))
    assert res.status_code == 204


# ──────────── Cart ────────────

@pytest.mark.asyncio
async def test_get_cart_empty(client, test_user):
    res = await client.get("/api/v1/cart", cookies=auth_cookies(test_user["token"]))
    assert res.status_code == 200
    assert res.json()["items"] == []


@pytest.mark.asyncio
async def test_add_to_cart(client, test_user, test_product):
    res = await client.post("/api/v1/cart/items", json={
        "product_id": test_product["id"],
        "quantity": 2,
    }, cookies=auth_cookies(test_user["token"]))
    assert res.status_code == 200
    # Verify
    res = await client.get("/api/v1/cart", cookies=auth_cookies(test_user["token"]))
    assert len(res.json()["items"]) > 0
    # Cleanup
    from app.core.database import get_db
    db = get_db()
    await db.cart.delete_one({"user_id": test_user["id"]})


@pytest.mark.asyncio
async def test_remove_from_cart(client, test_user, test_product):
    # Add first
    await client.post("/api/v1/cart/items", json={
        "product_id": test_product["id"],
        "quantity": 1,
    }, cookies=auth_cookies(test_user["token"]))
    # Remove
    res = await client.delete(f"/api/v1/cart/items/{test_product['id']}", cookies=auth_cookies(test_user["token"]))
    assert res.status_code == 200
    # Cleanup
    from app.core.database import get_db
    db = get_db()
    await db.cart.delete_one({"user_id": test_user["id"]})


@pytest.mark.asyncio
async def test_clear_cart(client, test_user, test_product):
    await client.post("/api/v1/cart/items", json={
        "product_id": test_product["id"],
        "quantity": 1,
    }, cookies=auth_cookies(test_user["token"]))
    res = await client.delete("/api/v1/cart", cookies=auth_cookies(test_user["token"]))
    assert res.status_code == 200
    from app.core.database import get_db
    db = get_db()
    await db.cart.delete_one({"user_id": test_user["id"]})


@pytest.mark.asyncio
async def test_cart_unauthenticated(client):
    res = await client.get("/api/v1/cart")
    assert res.status_code == 401


# ──────────── Wishlist ────────────

@pytest.mark.asyncio
async def test_get_wishlist_empty(client, test_user):
    res = await client.get("/api/v1/wishlist", cookies=auth_cookies(test_user["token"]))
    assert res.status_code == 200
    assert res.json()["items"] == []


@pytest.mark.asyncio
async def test_add_to_wishlist(client, test_user, test_product):
    res = await client.post("/api/v1/wishlist/items", json={
        "product_id": test_product["id"],
    }, cookies=auth_cookies(test_user["token"]))
    assert res.status_code == 200
    from app.core.database import get_db
    db = get_db()
    await db.wishlist.delete_one({"user_id": test_user["id"]})


@pytest.mark.asyncio
async def test_remove_from_wishlist(client, test_user, test_product):
    await client.post("/api/v1/wishlist/items", json={
        "product_id": test_product["id"],
    }, cookies=auth_cookies(test_user["token"]))
    res = await client.delete(f"/api/v1/wishlist/items/{test_product['id']}", cookies=auth_cookies(test_user["token"]))
    assert res.status_code == 200
    from app.core.database import get_db
    db = get_db()
    await db.wishlist.delete_one({"user_id": test_user["id"]})


# ──────────── Reviews ────────────

@pytest.mark.asyncio
async def test_list_reviews_empty(client, test_product):
    res = await client.get(f"/api/v1/reviews/{test_product['id']}")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


@pytest.mark.asyncio
async def test_create_review(client, test_user, test_product):
    res = await client.post("/api/v1/reviews", json={
        "product_id": test_product["id"],
        "rating": 5,
        "comment": "Excellent test product, would test again!",
    }, cookies=auth_cookies(test_user["token"]))
    assert res.status_code == 201
    assert res.json()["rating"] == 5
    # Cleanup
    from app.core.database import get_db
    from bson import ObjectId
    db = get_db()
    await db.reviews.delete_one({"product_id": test_product["id"], "user_id": test_user["id"]})


@pytest.mark.asyncio
async def test_create_review_duplicate(client, test_user, test_product):
    # Create first review
    await client.post("/api/v1/reviews", json={
        "product_id": test_product["id"],
        "rating": 4,
        "comment": "First review that is a duplicate test.",
    }, cookies=auth_cookies(test_user["token"]))
    # Try duplicate
    res = await client.post("/api/v1/reviews", json={
        "product_id": test_product["id"],
        "rating": 3,
        "comment": "Second review should fail as duplicate.",
    }, cookies=auth_cookies(test_user["token"]))
    assert res.status_code == 400
    from app.core.database import get_db
    db = get_db()
    await db.reviews.delete_one({"product_id": test_product["id"], "user_id": test_user["id"]})


@pytest.mark.asyncio
async def test_create_review_invalid_rating(client, test_user, test_product):
    res = await client.post("/api/v1/reviews", json={
        "product_id": test_product["id"],
        "rating": 10,
        "comment": "Invalid rating value test.",
    }, cookies=auth_cookies(test_user["token"]))
    assert res.status_code == 422


# ──────────── Orders ────────────

@pytest.mark.asyncio
async def test_list_orders_empty(client, test_user):
    res = await client.get("/api/v1/orders", cookies=auth_cookies(test_user["token"]))
    assert res.status_code == 200
    assert "orders" in res.json()


@pytest.mark.asyncio
async def test_get_order_not_found(client, test_user):
    from bson import ObjectId
    fake_id = str(ObjectId())
    res = await client.get(f"/api/v1/orders/{fake_id}", cookies=auth_cookies(test_user["token"]))
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_cancel_nonexistent_order(client, test_user):
    from bson import ObjectId
    fake_id = str(ObjectId())
    res = await client.post(f"/api/v1/orders/{fake_id}/cancel", cookies=auth_cookies(test_user["token"]))
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_checkout_empty_cart(client, test_user):
    res = await client.post("/api/v1/orders/checkout", json={
        "shipping_address": {
            "full_name": "Test User",
            "address_line": "123 Test St",
            "city": "Test City",
            "state": "TS",
            "zip_code": "12345",
            "country": "US",
        }
    }, cookies=auth_cookies(test_user["token"]))
    assert res.status_code == 400


# ──────────── Recommendations ────────────

@pytest.mark.asyncio
async def test_recommendations_guest(client):
    res = await client.get("/api/v1/recommendations")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


@pytest.mark.asyncio
async def test_recommendations_authenticated(client, test_user):
    res = await client.get("/api/v1/recommendations", cookies=auth_cookies(test_user["token"]))
    assert res.status_code == 200
    assert isinstance(res.json(), list)


# ──────────── Admin ────────────

@pytest.mark.asyncio
async def test_admin_stats(client, admin_user):
    res = await client.get("/api/v1/admin/stats", cookies=auth_cookies(admin_user["token"]))
    assert res.status_code == 200
    data = res.json()
    assert "total_revenue" in data
    assert "total_sales" in data
    assert "total_users" in data
    assert "total_products" in data
    assert "recent_orders" in data
    assert "revenue_chart" in data


@pytest.mark.asyncio
async def test_admin_stats_forbidden_for_user(client, test_user):
    res = await client.get("/api/v1/admin/stats", cookies=auth_cookies(test_user["token"]))
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_admin_users(client, admin_user):
    res = await client.get("/api/v1/admin/users", cookies=auth_cookies(admin_user["token"]))
    assert res.status_code == 200
    assert isinstance(res.json(), list)


@pytest.mark.asyncio
async def test_admin_orders(client, admin_user):
    res = await client.get("/api/v1/admin/orders", cookies=auth_cookies(admin_user["token"]))
    assert res.status_code == 200
    assert isinstance(res.json(), list)
