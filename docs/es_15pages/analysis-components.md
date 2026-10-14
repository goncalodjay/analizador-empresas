# Análisis de los Archivos Fuente

## Descripción de los Archivos

### `technical_service.py`
Implementa un servicio para:
- Obtener datos históricos (OHLCV) de acciones usando yfinance
- Calcular indicadores técnicos (RSI, MACD, EMA, Bollinger Bands)
- Devolver un objeto `TechnicalIndicators` con los cálculos

Ejemplo de uso:
```python
service = TechnicalService()
indicators = await service.compute("AAPL")
```

### `technical_indicators.py`
Maneja la persistencia de señales técnicas en la base de datos:
- Almacena valores numéricos de indicadores (RSI, MACD, EMA, Bollinger Bands)
- Guarda etiquetas de señales (golden cross, oversold, etc.)
- Maneja errores de persistencia sin detener el proceso

Ejemplo de uso:
```python
persist_technical_signals("AAPL", indicators, db, logger)
```

### `health_score.py`
Calcula el "Health Score" de una acción basado en:
1. Calidad fundamental (PE, PB, DE)
2. Momentum de ganancias
3. Sentimiento de analistas
4. Momentum técnico

Ejemplo de uso:
```python
engine = HealthScoreEngine()
score = await engine.compute("AAPL")
print(score.verdict)  # "Strong Buy" o "Avoid"
```

## Relación entre Componentes

1. **Flujo de Datos**
- `TechnicalService` obtiene datos históricos → `compute_indicators` → `persist_technical_signals`
- `HealthScoreEngine` usa:
  - `FundamentalService` para métricas fundamentales
  - `CacheService` para sentimiento de analistas
  - Datos técnicos persistidos para momentum técnico

2. **Arquitectura**
- Capa de acceso a datos: yfinance
- Capa de cálculo: `compute_indicators` (no mostrado)
- Capa de persistencia: SQLAlchemy
- Capa de análisis: HealthScoreEngine

3. **Dependencias**
- `HealthScoreEngine` depende de:
  - `FundamentalService` (para datos fundamentales)
  - `CacheService` (para datos de analistas)
- `TechnicalService` depende de:
  - yfinance (para datos históricos)
  - `compute_indicators` (para cálculos técnicos)

## Estructura de Datos

### Objeto `TechnicalIndicators`
Contiene:
- Valores de indicadores (RSI, MACD, EMA, Bollinger Bands)
- Señales de cruzamiento (golden cross, death cross)
- Zona de RSI (oversold/overbought)

### Objeto `HealthScoreResult`
Incluye:
- Puntuación compuesta (0-100)
- Verdict final ("Strong Buy", "Avoid")
- Puntuaciones individuales:
  - Calidad fundamental
  - Momentum de ganancias
  - Sentimiento de analistas
  - Momentum técnico
- Timestamp de cálculo

## Flujo de Ejecución
1. `TechnicalService.compute()` obtiene datos históricos
2. `compute_indicators()` calcula indicadores técnicos
3. `persist_technical_signals()` guarda los datos en la base de datos
4. `HealthScoreEngine.compute()`:
   - Obtiene métricas fundamentales
   - Calcula puntuaciones individuales
   - Combina resultados en un score compuesto
   - Devuelve `HealthScoreResult` con análisis completo