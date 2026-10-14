# Configuración

## Archivo `.env.example`
Este archivo contiene variables de entorno que definen la configuración del proyecto. Proporciona ejemplos de cómo configurar servicios como PostgreSQL, Redis, claves secretas y URLs de API.

### Variables clave
- `DATABASE_URL`: Configura la conexión a la base de datos PostgreSQL (usando `asyncpg` para asincronía).
- `REDIS_URL`: Define la conexión al servidor Redis.
- `SECRET_KEY`: Clave secreta para encriptación y seguridad (debe ser única y aleatoria).
- `DEBUG`: Activa el modo de depuración (útil para desarrollo).
- `NEXT_PUBLIC_API_URL`: URL pública de la API para el frontend (por ejemplo, `http://localhost:8000`).

**Ejemplo de uso:**
```bash
# Copiar a .env y ajustar valores
DATABASE_URL=postgresql+asyncpg://analyzer:analyzer@localhost:5432/analyzer
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
DEBUG=true
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Archivo `.gitignore`
Este archivo especifica qué archivos y directorios deben ignorarse por Git para evitar commits innecesarios o sensibles.

### Directorios ignorados
- **Python**: Carpeta `__pycache__`, archivos de entorno virtual (`env/`, `venv/`) y archivos generados.
- **Node.js**: Directorios de dependencias (`node_modules/`) y archivos de build.
- **Entornos**: Archivos de configuración (`env`, `env.local`, `env.*.local`) para evitar exponer claves.
- **IDE**: Carpeta `.vscode/` y `.idea/` para configuraciones específicas de editores.
- **Sistema operativo**: Archivos como `.DS_Store` (macOS) o `Thumbs.db` (Windows).
- **Docker**: Datos de volumenes (`postgres_data/`).

**Ejemplo de uso:**
```bash
# Ignorar archivos de entorno
.env
.env.local
.env.*.local
```

---

## Archivo `.claude/settings.local.json`
Este archivo define permisos para herramientas locales, como el uso de comandos Bash en contenedores Docker o plugins específicos.

### Permisos clave
- `Bash(docker compose exec backend python -c ' *)`: Permite ejecutar comandos en contenedores Docker.
- `mcp__plugin_engram_engram__mem_save`, `mcp__plugin_engram_engram__mem_search`: Permisos para plugins de memoria en un sistema de habilidades (posiblemente para un registro local de habilidades).

**Ejemplo de uso:**
```json
{
  "permissions": {
    "allow": [
      "Bash(docker compose exec backend python -c ' *)",
      "mcp__plugin_engram_engram__mem_save"
    ]
  }
}
```

---

## Notas adicionales
- Los directorios `openspec/changes/iol-trading-and-ux-overhaul` y `.atl/**/*` no existen en el repositorio, pero podrían ser relevantes para futuras extensiones o documentación.