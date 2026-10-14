# Data Ingestion

## Descripción general
El módulo `data-ingestion` se encarga de la ingestión y persistencia de datos financieros, incluyendo precios de activos, fundamentales, noticias y historial de precios. Utiliza proveedores externos para obtener datos, los almacena en caché y actualiza registros en la base de datos. La lógica principal se implementa en `ingestion_service.py`, que coordina la obtención de datos, la validación y la persistencia.

---

## Archivos fuente relevantes

### `ingestion_service.py`
Implementa la lógica central para la ingestión de datos:
- **`ingest_ticker`**: Obtiene el precio de un ticker específico usando el proveedor y actualiza el caché.
- **`ingest_ticker_with_currency`**: Determina la moneda asociada al portafolio del usuario y obtiene datos con el proveedor correspondiente. También persiste noticias y datos históricos de precios.
- **`ingest_portfolio`**: Ingestiona todos los tickers asociados a un usuario desde su portafolio.
- **`_ingest_news`**: Obtiene y persiste noticias relacionadas con un ticker en la base de datos.
- **`_persist_price_history`**: Almacena datos OHLC (Open/High/Low/Close) históricos de precios.
- **`get_cache_status`**: Verifica el estado de caché para un ticker específico.

**Relación con otros módulos**:
- Usa `ProviderFactory` para seleccionar proveedores según la moneda.
- Depende de `CacheService` para manejar el almacenamiento en caché.
- Accede a modelos como `NewsItem` y `PriceHistory` para persistir datos.

---

## Ejemplos de uso

### 1. Ingestión de un ticker específico
```python
result = await ingestion_service.ingest_ticker("AAPL", "user123")
# Resultado: objeto IngestionResult con precio y estado de caché
```

### 2. Ingestión con moneda específica
```python
result = await ingestion_service.ingest_ticker_with_currency("AAPL", "user123", currency="ARS")
# Resultado: incluye precio en ARS y datos de noticias
```

### 3. Ingestión de portafolio completo
```python
results = await ingestion_service.ingest_portfolio("user123")
# Resultado: lista de IngestionResult para cada ticker en el portafolio
```

### 4. Verificación de estado de caché
```python
status = ingestion_service.get_cache_status("AAPL")
# Resultado: objeto CacheStatus con información de caché
```

---

## Flujo de datos
1. **Obtención de datos**: Proveedores externos (ej. yfinance) devuelven datos en formato estructurado.
2. **Validación y normalización**: Los datos se normalizan en modelos como `NormalizedPriceData` o `NormalizedFundamentals`.
3. **Persistencia**: Los datos se guardan en la base de datos (ej. `PriceHistory`, `NewsItem`).
4. **Caching**: Resultados se almacenan en caché para evitar reconsultas repetidas.

---

## Consideraciones
- La moneda usada para la ingestión se determina automáticamente desde el portafolio del usuario.
- Los datos históricos de precios se almacenan con un período configurable ("1y" para primer ingreso, "7d" por defecto).
- Las noticias se persisten en la base de datos con metadatos como fecha de publicación y fuente.