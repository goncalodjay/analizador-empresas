# Performance & Caching

## Redis Configuration
El archivo `redis.py` establece la conexión con Redis, un sistema de caché en memoria. Proporciona funciones asíncronas para:
- `get_redis()`: Obtener la conexión Redis (se crea una vez)
- `close_redis()`: Cerrar la conexión
- `ping_redis()`: Verificar la conectividad

Este módulo es utilizado por `cache_service.py` para implementar el sistema de caché.

## Cache Service
El servicio `CacheService` maneja la persistencia temporal de datos con TTL (Time To Live) específicos:

### Configuración de TTL
```python
CACHE_TTLS = {
    "price": 900,              # 15 minutos
    "fundamentals": 21600,    # 6 horas
    "dividends": 21600,       # 6 horas
    "company_info": 86400,    # 24 horas
    "analyst_ratings": 86400, # 24 horas
    "insider": 86400,         # 24 horas
    "earnings": 86400,        # 24 horas
    "news": 1800,             # 30 minutos
    "technical": 900          # 15 minutos
}
```

### Métodos clave
```python
async def get(self, key: str) -> dict | None:
    """Obtener datos del caché"""
    client = await get_redis()
    raw = await client.get(key)
    return json.loads(raw) if raw else None

async def set(self, key: str, value: dict, data_type: str):
    """Almacenar datos con TTL"""
    ttl = CACHE_TTLS.get(data_type, 300)
    value["_cached_at"] = datetime.now(timezone.utc).isoformat()
    await client.setex(key, ttl, json.dumps(value, default=str))

async def get_or_fetch(
    self,
    key: str,
    data_type: str,
    fetch_fn,
) -> dict:
    """Obtener datos del caché o fetchear nuevos"""
    cached = await self.get(key)
    if cached:
        return cached
    
    return await fetch_fn()
```

## Modelos y Caching
Los modelos de la base de datos (ej: `FundamentalSnapshot`, `TechnicalSignal`) son cacheados utilizando claves basadas en:
- Tipo de dato (`fundamentals`, `technical`, etc.)
- Identificador único del registro

Ejemplo de clave:
```
"fundamentals:NASDAQ:MSFT:2023-10-01"
```

## Ejemplos de Uso
```python
from cache_service import CacheService
from models import FundamentalSnapshot

async def fetch_fundamentals(ticker):
    # Lógica para obtener datos desde la base de datos
    return FundamentalSnapshot.find_by_ticker(ticker)

cache = CacheService()
data = await cache.get_or_fetch(
    key="fundamentals:NASDAQ:MSFT",
    data_type="fundamentals",
    fetch_fn=fetch_fundamentals
)
```

Este sistema optimiza el rendimiento al reducir la carga en la base de datos mientras mantiene la actualidad de los datos.