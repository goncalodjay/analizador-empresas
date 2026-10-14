# Descripción de los archivos fuente

## `PriceHistoryChart.tsx`
Este componente renderiza un gráfico de línea personalizado en SVG que muestra la historia de precios de un activo financiero. Calcula escalas, posiciones y etiquetas para representar datos de precios y fechas. Incluye:
- Llenado de área con gradiente
- Línea de precios
- Etiquetas de fechas y precios
- Indicador de frescura de los datos

**Relación con otros archivos:**
- Usa `DataFreshnessTag` para mostrar el estado de frescura de los datos
- Requiere que `DataFreshnessTag` esté disponible en el mismo contexto

## `TradingViewChart.tsx`
Este componente incrusta un gráfico de TradingView (servicio externo) para mostrar datos de precios. Carga un script externo y configura el widget con:
- Simbolo de activo (ticker)
- Intervalo de tiempo (ej: "D" para diario)
- Tema (light/dark)

**Relación con otros archivos:**
- Comparte el mismo propósito de mostrar datos de precios
- Usa un enfoque diferente (widget externo vs gráfico SVG personalizado)
- Ambos pueden coexistir en una aplicación para mostrar datos de precios desde fuentes distintas

## Ejemplo de uso
```tsx
// Componente que muestra ambos gráficos
function PriceComparison({ ticker }: { ticker: string }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <PriceHistoryChart 
        ticker={ticker}
        points={priceData} 
        freshness="fresh"
        fetchedAt="2023-10-15"
      />
      <TradingViewChart 
        ticker={ticker}
        theme="dark"
        interval="1D"
      />
    </div>
  );
}
```