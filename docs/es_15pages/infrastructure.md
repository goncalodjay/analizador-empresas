# Infrastructure

## Archivos fuente relevantes

### .env.example
Este archivo contiene variables de entorno de ejemplo para configurar la aplicación localmente. Define las conexiones a la base de datos PostgreSQL, Redis, la clave secreta y la URL de la API. Las variables se usan en el backend y frontend para conectarse a servicios externos.

**Ejemplo de uso:**
```bash
DATABASE_URL=postgresql+asyncpg://analyzer:analyzer@localhost:5432/analyzer
REDIS_URL=redis://localhost:6379/0
```

### docker-compose.yml
Define servicios Docker para desplegar la infraestructura localmente. Incluye:
- PostgreSQL (con pgvector para vectores de embeddings)
- Redis (para caché y cola)
- Backend (API en Python con Uvicorn)
- Frontend (aplicación React con Vite)

**Relación entre servicios:**
- El backend depende de PostgreSQL y Redis estar saludables
- El frontend depende del backend estar en ejecución
- Todos los servicios usan variables de entorno definidas en el archivo .env

### backend/Dockerfile
Configura el entorno de desarrollo para el backend:
- Usa Python 3.11
- Instala dependencias desde requirements.txt
- Ejecuta la aplicación con Uvicorn
- Exponen puerto 8000 para acceder a la API

### frontend/Dockerfile
Configura el entorno de desarrollo para el frontend:
- Usa Node.js 18
- Instala dependencias npm
- Ejecuta el servidor de desarrollo de Vite
- Exponen puerto 3000 para acceder a la interfaz web

### .gitignore
Lista de archivos y directorios a ignorar en el repositorio:
- Entornos virtuales (venv, env)
- Archivos de configuración sensibles (.env)
- Directorios de IDE (.vscode, .idea)
- Archivos generados por herramientas (node_modules, .next)

## Configuración local
Para ejecutar la infraestructura:
```bash
docker-compose up --build
```
Este comando:
1. Construye imágenes Docker para backend/frontend
2. Inicia servicios PostgreSQL, Redis, backend y frontend
3. Asigna puertos:
   - Backend: http://localhost:8000
   - Frontend: http://localhost:3000
   - PostgreSQL: localhost:5432
   - Redis: localhost:6379

## Variables de entorno
Las variables se definen en:
- .env.example (para desarrollo)
- .env (para producción)
- docker-compose.yml (para servicios Docker)

**Ejemplo de conexión a base de datos:**
```python
DATABASE_URL=postgresql+asyncpg://analyzer:analyzer@postgres:5432/analyzer
```
Este valor se usa en el backend para conectarse a PostgreSQL a través de Docker.