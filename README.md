# Shophub — Full-Stack AI E-Commerce Platform

![Shop Hub Screenshot](frontend/public/Screenshot%202026-03-02%20005850.png)

Shophub is a production-grade e-commerce platform built with modern technologies. It features seamless Stripe payments, a high-performance Redis-cached catalog, and JWT-based authentication with httpOnly cookies and secure password hashing. There's also a comprehensive admin dashboard with sales analytics and full inventory management.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19 + TypeScript + Vite |
| Styling | Tailwind CSS |
| State Management | Zustand + TanStack Query |
| Backend | FastAPI (Python) |
| Database | MongoDB (async via Motor) |
| Caching | Redis via Upstash |
| Payments | Stripe |
| Auth | JWT with httpOnly cookies |

---

## Key Features

- **Stripe Payments** — seamless checkout integration
- **Redis Caching** — high-performance product catalog via Upstash
- **JWT Authentication** — secure httpOnly cookies with password hashing
- **Admin Dashboard** — sales analytics and inventory management
- **Async Backend** — FastAPI with Motor for non-blocking MongoDB operations
- **Fully Responsive** — modern design on all screen sizes

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
copy .env.example .env             # Fill in your credentials

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
MONGODB_URL=your-mongodb-atlas-url
REDIS_URL=your-upstash-redis-url
STRIPE_SECRET_KEY=sk_test_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
```

### Frontend `.env`

```env
VITE_API_URL=http://127.0.0.1:8000
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

| Service | Platform | Notes |
|---|---|---|
| Database | MongoDB Atlas | Free tier available |
| Redis Cache | Upstash | Free tier available |
| Backend API | Render | Connect GitHub repo |
| Frontend | Vercel | Auto-deploy on push |

Connect your GitHub repository to each platform, configure the environment variables, and set the appropriate build commands.

---

*Built for portfolio demonstration purposes.*
