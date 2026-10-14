# Configuration and Environment

## Overview
This document explains the configuration files and environment setup for the project. These files define how the application connects to databases, caches, and external services, and how the Dockerized environment is structured.

---

## `.env.example`
This file provides example environment variables for local development. It serves as a template for configuring the application.

### Variables
- `DATABASE_URL`: PostgreSQL connection string using asyncpg (for async database operations).
- `REDIS_URL`: Redis connection string for caching and message brokering.
- `SECRET_KEY`: Secret key for cryptographic operations (e.g., JWT signing).
- `DEBUG`: Enables debug mode for detailed logs.
- `NEXT_PUBLIC_API_URL`: Public URL for the backend API (used by the frontend).

### Example Usage
```bash
DATABASE_URL=postgresql+asyncpg://analyzer:analyzer@localhost:5432/analyzer
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
DEBUG=true
NEXT_PUBLIC_API
```

---

## `docker-compose.yml`
This file defines the Docker services for the application, including PostgreSQL, Redis, backend, and frontend.

### Services
1. **PostgreSQL**  
   - Image: `pgvector/pgvector:pg15` (PostgreSQL with vector extension support)  
   - Ports: `5432`  
   - Healthcheck: Ensures the database is ready before starting the backend.

2. **Redis**  
   - Image: `redis:7-alpine`  
   - Ports: `6379`  
   - Healthcheck: Validates Redis connectivity.

3. **Backend**  
   - Uses `fastapi` and `uvicorn` for the API server.  
   - Connects to PostgreSQL via `postgresql+asyncpg://analyzer:analyzer@postgres:5432/analyzer` and Redis via `redis://redis:6379/0`.  
   - Depends on PostgreSQL and Redis being healthy.

4. **Frontend**  
   - Uses Next.js for the React frontend.  
   - Depends on the backend service being ready.

### Example Command
```bash
docker-compose up --build
```

---

## `.env` Files
- **`frontend/.env`**: Not found. The frontend uses environment variables defined in `docker-compose.yml` and `NEXT_PUBLIC_API_URL` in `frontend/package.json`.
- **`backend/.env`**: Not found. The backend uses environment variables defined in `docker-compose.yml` and `python-dotenv` for `.env` files (if present).

---

## `frontend/package.json`
Defines the frontend project structure and dependencies.

### Key Features
- **Next.js**: React framework for server-rendered pages.
- **Dev Script**: `npm run dev` starts the development server with hot-reloading.
- **Dependencies**: Includes React, TailwindCSS, and TypeScript.

---

## `backend/requirements.txt`
Lists Python dependencies for the backend.

### Key Packages
- **`fastapi`**: Asynchronous web framework for APIs.
- **`sqlalchemy[asyncio]`**: ORM for PostgreSQL with async support.
- **`redis`**: Redis client for caching.
- **`pgvector`**: PostgreSQL extension for vector embeddings (used in AI models).
- **`aiosqlite`**: Async SQLite database support.

---

## Relationships Between Files
- `.env.example` provides default values for environment variables used in `docker-compose.yml`.
- `docker-compose.yml` defines the Docker services, including environment variables for the backend and frontend.
- `requirements.txt` and `package.json` define the runtime dependencies for the backend and frontend, respectively.