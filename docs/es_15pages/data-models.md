# Data Models

Esta documentación describe los modelos de datos definidos en el proyecto, que se utilizan para estructurar la información en el frontend y en las interacciones con el backend.

## Archivos fuente relevantes
- **frontend/src/lib/types.ts**: Contiene las definiciones de tipos y interfaces que representan los datos del sistema. Estos modelos se utilizan para validar datos de entrada/salida, estructurar respuestas de APIs y manejar estados en la aplicación.

Los archivos del backend no están disponibles para análisis, pero los modelos definidos aquí son los que se utilizan para comunicar la lógica del frontend con las funcionalidades del backend.

---

## Modelos de datos principales

### Usuarios
**`UserOut`**  
Representa los datos de un usuario cuando se devuelve como respuesta.  
```ts
{
  id: string;
  email: string;
  timezone: string;
  risk_tolerance: string;
  email_notifications: boolean;
}
```
**`UserCreate`**  
Datos necesarios para crear un nuevo usuario.  
```ts
{
  email: string;
  password: string;
}
```
**`UserLogin`**  
Datos para autenticar a un usuario.  
```ts
{
  email: string;
  password: string;
}
```

### Posiciones en Portafolio
**`PortfolioPosition`**  
Datos de una posición en el portafolio (lectura).  
```ts
{
  id: string;
  ticker: string;
  shares: string;
  avg_buy_price: string;
  sector: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}
```
**`PortfolioPositionCreate`**  
Datos para crear una nueva posición.  
```ts
{
  ticker: string;
  shares: string;
  avg_buy_price: string;
  sector?: string;
  notes?: string;
}
```
**`PortfolioPositionUpdate`**  
Datos para actualizar una posición existente.  
```ts
{
  ticker?: string;
  shares?: string;
  avg_buy_price?: string;
  sector?: string;
  notes?: string;
}
```

### Listas de Seguimiento
**`Watchlist`**  
Información básica de una lista de seguimiento.  
```ts
{
  id: string;
  name: string;
  description: string | null;
  ticker_count: number;
  created_at: string;
}
```
**`WatchlistDetail`**  
Extiende `Watchlist` con información de los tickers incluidos.  
```ts
{
  ...Watchlist;
  tickers: WatchlistTicker[];
}
```
**`WatchlistTicker`**  
Detalles de un ticker en una lista de seguimiento.  
```ts
{
  ticker: string;
  added_at: string;
}
```

### Estrategias de Inversión
**`Strategy`**  
Define una estrategia de inversión con reglas y configuración.  
```ts
{
  id: string;
  name: string;
  style: 'value' | 'growth' | 'momentum' | 'dividend' | 'hybrid';
  rules: StrategyRules;
  is_active: boolean;
  is_primary: boolean;
  created_at: string;
  updated_at: string;
}
```
**`StrategyRules`**  
Reglas fundamentales y técnicas para la estrategia.  
```ts
{
  max_pe?: string;
  min_roe?: string;
  min_dividend_yield?: string;
  max_debt_to_equity?: string;
  min_revenue_growth?: string;
  rsi_entry_max?: string;
  rsi_exit_min?: string;
  ema_crossover?: boolean;
  macd_bullish?: boolean;
  max_position_pct?: string;
  stop_loss_pct?: string;
  take_profit_pct?: string;
}
```

### Historial de Precios
**`PricePoint`**  
Datos de un punto en la serie histórica de precios.  
```ts
{
  date: string; // YYYY-MM-DD
  open: string;
  high: string;
  low: string;
  close: string;
  volume: number | null;
}
```
**`PriceSeriesResponse`**  
Respuesta de una consulta de serie histórica.  
```ts
{
  ticker: string;
  points: PricePoint[];
  from_date: string;
  to_date: string;
  count: number;
  source: string;
  freshness: string;
  fetched_at: string | null;
}
```

### Integración con IOL
**`IOLHolding`**  
Datos de una posición en la cuenta de IOL.  
```ts
{
  ticker: string;
  quantity: number;
  avg_buy_price: number;
  currency: 'ARS' | 'USD';
}
```
**`IOLStatus`**  
Estado de la conexión con la cuenta de IOL.  
```ts
{
  connected: boolean;
  iol_username?: string;
  account_name?: string;
  cash_balance?: number;
  currency?: string;
  last_sync?: string;
  needs_reauth?: boolean;
}
```

### Noticias
**`NewsItemOut`**  
Datos de una noticia relacionada con un ticker.  
```ts
{
  headline: string;
  summary: string | null;
  source_name: string;
  url: string | null;
  published_at: string | null;
}
```
**`NewsFeedResponse`**  
Respuesta de la consulta de noticias.  
```ts
{
  ticker: string;
  available: boolean;
  source: string | null;
  items: NewsItemOut[];
  cached_at: string | null;
  freshness: 'live' | 'stale' | null;
  count: number;
}
```