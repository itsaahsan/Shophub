# Shophub

![Shophub Screenshot](frontend/public/screenshot-with-background.png)

Shophub is a production-grade e-commerce platform built with modern technologies. It features an **AI Shopping Assistant**, seamless Stripe **Subscriptions**, a high-performance Redis-cached catalog, and JWT-based authentication. There's also a comprehensive admin dashboard with sales analytics, user management, and full inventory control.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19 + TypeScript + Vite |
| Styling | Tailwind CSS |
| State Management | Zustand + TanStack Query |
| Backend | FastAPI (Python) |
| Database | PostgreSQL (async via SQLAlchemy) |
| Caching | Redis via Upstash |
| AI | OpenAI GPT-3.5 (Discovery & Recs) |
| Payments | Stripe (One-time & Subscriptions) |
| Auth | JWT with httpOnly cookies |

---

## Key Features

- **AI Shopping Assistant** — Floating chat widget for natural language product discovery
- **Subscription System** — Tiered membership plans (Pro/Business) with recurring Stripe billing
- **Advanced Admin Dashboard** — Comprehensive views for Users, Orders, and Inventory
- **Stripe Payments** — Secure checkout for both one-time purchases and subscriptions
- **Redis Caching** — High-performance product catalog via Upstash
- **JWT Authentication** — Secure httpOnly cookies with password hashing
- **Async Backend** — FastAPI with SQLAlchemy for non-blocking PostgreSQL operations
- **Fully Responsive** — Modern design optimized for all screen sizes
- **Advanced Search & Filters** — Full-text search, category/price sorting with debounced queries
- **Order Tracking** — Real-time status updates and purchase history
- **Comprehensive Testing** — Pytest backend + Vitest frontend validation
- **Type-Safe APIs** — Full OpenAPI schema with Pydantic models + TypeScript interfaces

---

## Getting Started

### Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1        # Windows
source venv/bin/activate            # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Setup environment
copy .env.example .env             # Fill in your PostgreSQL credentials

# Run server
uvicorn app.main:app --reload
```

API available at: `http://127.0.0.1:8000`
Interactive docs: `http://127.0.0.1:8000/docs`

---

### Frontend

```bash
cd frontend

npm install

copy .env.example .env             # Set VITE_API_URL

npm run dev
```

UI available at: `http://localhost:5173`

---

## Environment Variables

### Backend `.env`

```env
POSTGRESQL_URI=postgresql+asyncpg://user:password@localhost:5432/shophub
REDIS_URL=your-upstash-redis-url
STRIPE_SECRET_KEY=sk_test_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
```

### Frontend `.env`

```env
VITE_API_URL=http://127.0.0.1:8000/api/v1
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_xxxxx
```

---

## API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Testing

```bash
# Full test suite
cd backend && pytest

# Quick sanity check
python health_check.py
```

---

## Deployment

### Vercel Frontend

Create a Vercel project with:

```text
Root Directory: frontend
Build Command: npm run build
Output Directory: dist
```

Set:

```env
VITE_API_URL=https://your-api-domain.example.com/api/v1
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_xxxxx
VITE_GOOGLE_CLIENT_ID=your-google-client-id
```

---

*Built for portfolio demonstration purposes.*
