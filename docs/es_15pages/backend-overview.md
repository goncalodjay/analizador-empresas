# Backend Overview

## Dockerfile
El archivo Dockerfile define la configuración del entorno de desarrollo y ejecución del backend. Crea una imagen Docker basada en Python 3.11, instala las dependencias desde `requirements.txt`, copia el código fuente y configura el servidor Uvicorn para ejecutar la aplicación FastAPI en el puerto 8000.

**Ejemplo de uso:**
```bash
docker build -t backend-app .
docker run -d -p 8000:8000 backend-app
```

## requirements.txt
Lista todas las dependencias necesarias para el proyecto, incluyendo:
- **FastAPI** y **Uvicorn**: Framework para desarrollo de APIs REST.
- **SQLAlchemy** y **asyncpg**: Para manejo de bases de datos PostgreSQL con soporte asincrónico.
- **Alembic**: Herramienta para gestión de migraciones de bases de datos.
- **Pydantic** y **pydantic-settings**: Validación de datos y manejo de configuraciones.
- **redis** y **aiosqlite**: Para integración con cachés y bases de datos SQLite asincrónicas.
- **pytest** y **pytest-asyncio**: Para pruebas unitarias y de integración.

## Directorios vacíos
Los directorios `alembic`, `app` y `tests` no contienen archivos en este momento. Estos deberían incluir:
- **alembic**: Archivos de migraciones para la base de datos.
- **app**: Código principal de la aplicación FastAPI (rutas, modelos, lógica de negocio).
- **tests**: Casos de prueba para validar funcionalidades.

**Nota:** Estos directorios están en blanco y requieren implementación adicional para completar el backend.