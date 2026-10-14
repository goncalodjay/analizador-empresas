# Deployment

Este documento describe cómo desplegar la aplicación utilizando Docker y docker-compose. Los archivos fuente definidos son esenciales para configurar y ejecutar los servicios de la aplicación.

## Archivo docker-compose.yml
Este archivo define los servicios de la aplicación:
- **PostgreSQL**: Base de datos con soporte para vectores (pgvector). Usa el contenedor `pgvector/pgvector:pg15` y establece variables de entorno para autenticación.
- **Redis**: Almacenamiento en caché con contenedor `redis:7-alpine`. Verifica la salud mediante el comando `redis-cli ping`.
- **Backend**: Servidor principal construido desde el directorio `./backend` usando el Dockerfile correspondiente. Configura variables de entorno para conexiones a BD, Redis y API, y usa `uvicorn` para ejecutar la aplicación.
- **Frontend**: Servidor de frontend construido desde `./frontend` con Node.js. Depende del backend y ejecuta `npm run dev` para desarrollo.

Los contenedores se conectan entre sí mediante nombres de red interna (ej: `postgres` para la base de datos). Los puertos `5432`, `6379`, `8000` y `3000` están mapeados para acceso externo.

## Archivo backend/Dockerfile
Configura la imagen del backend:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```
- Instala dependencias Python desde `requirements.txt`.
- Copia el código fuente y ejecuta el servidor Uvicorn en el puerto 8000.

## Archivo frontend/Dockerfile
Configura la imagen del frontend:
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev"]
```
- Instala dependencias Node.js desde `package.json`.
- Ejecuta el servidor de desarrollo de React/Vue en el puerto 3000.

## Notas importantes
- Los archivos en `openspec/changes/iol-trading-and-ux-overhaul/**/*` no están disponibles en el contexto actual y no se incluyen en este despliegue.
- Para usar la API, asegúrate de reemplazar `NEWSAPI_API_KEY` en el archivo `.env` del backend.
- El modo `--reload` en Uvicorn y `npm run dev` permiten actualizaciones en caliente durante el desarrollo.