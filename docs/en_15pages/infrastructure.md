# Infrastructure and Deployment

## Frontend Overview
The frontend is a Next.js application built with React 18 and TypeScript. It uses TailwindCSS for styling and includes development scripts for local testing (`npm run dev`) and production builds (`npm run build`). The Dockerfile sets up a Node.js environment to run the app, exposing port 3000.

**Key Dependencies:**
- Next.js (14.2.4)
- React (18.3.1)
- TypeScript (5.4.5)
- TailwindCSS (3.4.4)

**Relationship with Backend:**  
The frontend connects to the backend API via the `NEXT_PUBLIC_API_URL` environment variable, which is set to `http://localhost:8000` in development.

---

## Backend Overview
The backend is a FastAPI application using Python 3.11. It supports asynchronous PostgreSQL (via asyncpg) and Redis for caching. The `requirements.txt` includes tools for database migrations (Alembic), data validation (Pydantic), and testing (pytest-asyncio). The Dockerfile installs dependencies and runs the app with Uvicorn.

**Key Dependencies:**
- FastAPI (0.111.0)
- SQLAlchemy (with async support)
- asyncpg (PostgreSQL async driver)
- Redis (for caching)
- Alembic (database migrations)
- Pydantic (data validation)

**Relationship with Database:**  
The backend connects to PostgreSQL via `DATABASE_URL`, which is configured to use the `pgvector` image for vector search capabilities.

---

## Docker Compose Setup
The `docker-compose.yml` defines a multi-container environment for local development:

1. **PostgreSQL (with pgvector):**  
   - Image: `pgvector/pgvector:pg15`  
   - Ports: `5432`  
   - Volumes: Persistent data storage  
   - Healthcheck: Ensures the database is ready before starting other services

2. **Redis:**  
   - Image: `redis:7-alpine`  
   - Ports: `6379`  
   - Healthcheck: Verifies Redis connectivity

3. **Backend Service:**  
   - Builds from `backend/Dockerfile`  
   - Environment variables:  
     - `DATABASE_URL` (points to PostgreSQL)  
     - `REDIS_URL` (points to Redis)  
     - `NEXT_PUBLIC_API_URL` (exposes backend to frontend)  
   - Runs with hot-reloading (`--reload`)

4. **Frontend Service:**  
   - Builds from `frontend/Dockerfile`  
   - Depends on the backend service  
   - Runs in development mode (`npm run dev`)

**Command to start:**  
```bash
docker-compose up --build
```

---

## Environment Variables
The `.env.example` file provides default values for configuration:

```env
DATABASE_URL=postgresql+asyncpg://analyzer:analyzer@localhost:5432/analyzer
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
DEBUG=true
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Usage Example:**  
In the backend, `DATABASE_URL` is used to connect to PostgreSQL, while `NEXT_PUBLIC_API_URL` is injected into the frontend to point to the backend API.

---

## Deployment Notes
- **Production:** Replace `localhost` with actual hostnames/IPs in environment variables. Use `npm run build` for frontend and `uvicorn` with production settings for the backend.
- **Scaling:** The Docker Compose setup is ideal for local development. For production, consider using orchestration tools like Kubernetes or cloud providers (AWS/ECS, GCP, etc.).