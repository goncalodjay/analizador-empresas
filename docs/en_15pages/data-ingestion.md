# Archivos Fuente y su Relación

## price_history_service.py
Implementa el servicio para obtener datos históricos de precios. Usa SQLAlchemy para consultar la base de datos y devuelve una respuesta estructurada. Ejemplo de uso:
```python
await PriceHistoryService().get_series(db, "AAPL", date(2023,1,1), date(2023,12,31))
```

## news_service.py
Maneja la obtención de noticias con estrategia cache-first (Redis → Postgres). Ejemplo de uso:
```python
await NewsService().get_news("TSLA", db, cache)
```

## cache_service.py
Proporciona servicios de caché para Redis. Ejemplo de uso:
```python
await CacheService().set("news:TSLA", {"articles": [...]}, "news")
```

## Relación entre archivos
- `PriceHistoryService` y `NewsService` usan `CacheService` para caché
- Ambos servicios consultan PostgreSQL como fuente de datos
- `CacheService` maneja temporizaciones (TTL) para diferentes tipos de datos
- Los servicios devuelven respuestas estructuradas con metadatos (frescura, fuente, etc.)