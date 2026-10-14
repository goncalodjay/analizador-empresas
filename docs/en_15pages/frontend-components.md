# Explicación de los archivos fuente

## `PriceHistoryChart.tsx`
Este componente renderiza un gráfico de historia de precios personalizado usando SVG. Muestra datos de precios históricos con:
- Línea de tendencia azul
- Relleno con gradiente
- Etiquetas de fechas y precios
- Indicador de frescura de los datos

### Props clave:
- `ticker`: Simbolo del activo (ej: "AAPL")
- `points`: Array de datos de precios con campo `date` y `close`
- `freshness`: Estado de los datos ("fresh", "stale", "eod")
- `fetchedAt`: Fecha de obtención de los datos

### Ejemplo de uso:
```tsx
<PriceHistoryChart 
  ticker="BTCUSD" 
  points={priceData} 
  freshness="fresh" 
  fetchedAt="2023-10-15"
/>
```

## `TradingViewChart.tsx`
Este componente integra el widget de TradingView para mostrar gráficos de precios en tiempo real. Permite:
- Visualización de gráficos técnicos
- Personalización de intervalos (ej: "D" para diario)
- Temas oscuro/claro

### Props clave:
- `ticker`: Simbolo del activo (ej: "AAPL")
- `theme`: Tema ("light" o "dark")
- `interval`: Intervalo temporal (ej: "1D", "1W")

### Ejemplo de uso:
```tsx
<TradingViewChart 
  ticker="AAPL" 
  theme="dark" 
  interval="1D"
/>
```

## Relación entre los archivos
Ambos componentes muestran datos de precios pero:
- `PriceHistoryChart` es una solución personalizada para mostrar datos históricos con metadatos de frescura
- `TradingViewChart` integra un widget externo para visualización avanzada en tiempo real
- Comparten el mismo propósito de mostrar precios pero usan diferentes tecnologías (SVG vs. widget externo)