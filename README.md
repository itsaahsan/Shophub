# Shophub — Full-Stack AI E-Commerce Platform

![Shop Hub Screenshot](frontend/public/Screenshot%202026-03-02%20005850.png)

Shop Hub is a production-grade AI-powered e-commerce platform built with modern technologies. It features AI-driven product recommendations using OpenAI GPT-3.5, seamless Stripe payments, and a high-performance Redis-cached catalog. The platform includes JWT-based authentication with httpOnly cookies, Google OAuth, and secure password hashing. There's also a comprehensive admin dashboard with sales analytics and full inventory management.

The frontend is built with React 19, TypeScript, Vite, Tailwind CSS, Zustand, and TanStack Query, while the backend uses FastAPI with Motor for async MongoDB and Redis caching through Upstash. The design is fully responsive and modern.

To get started, navigate to the backend folder and create a virtual environment with `python -m venv venv`, then activate it with `.\venv\Scripts\Activate.ps1` on Windows or `source venv/bin/activate` on Mac/Linux. Install dependencies with `pip install -r requirements.txt`, then copy the `.env.example` file to `.env` and fill in your credentials for MongoDB, Redis, Stripe, OpenAI, and other services. Run the backend with `uvicorn app.main:app --reload` and it will be available at `http://127.0.0.1:8000` with interactive docs at `/docs`.

For the frontend, go to the frontend folder and run `npm install`, then copy `.env.example` to `.env` and set the `VITE_API_URL` to your backend URL. Start the development server with `npm run dev` and the UI will be available at `http://localhost:5173`.

For deployment, you can use MongoDB Atlas for the database (free tier available), Upstash for Redis caching, Render for the backend API, and Vercel for the frontend. Simply connect your GitHub repository to each platform, configure the environment variables, and set the appropriate build commands.

The API documentation is available at `http://localhost:8000/docs` for interactive testing or `http://localhost:8000/redoc` for an alternative format. For backend tests, run `pytest` in the backend folder, or use `python health_check.py` for a quick sanity check.

This project is built with care for portfolio demonstration purposes.
