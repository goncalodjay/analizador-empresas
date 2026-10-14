# Código Fuente y Relaciones

## frontend/src/components/analysis/HealthScoreGauge.tsx
**Descripción:** Componente que muestra un indicador de salud con un gráfico circular que representa el puntaje compuesto, el veredicto (Strong Buy, Hold, etc.), subpuntajes y factores principales.  
**Relaciones:**  
- Usa `verdictColors` para colorear el veredicto (verde para "Strong Buy", rojo para "Avoid")  
- Muestra datos de `composite` (puntaje total), `verdict` (recomendación), `subScores` (subpuntajes) y `topDrivers` (factores clave)  
**Ejemplo de uso:**  
```tsx
<HealthScoreGauge 
  composite={85} 
  verdict="Strong Buy" 
  subScores={{ fundamental_quality: 22, ... }} 
  topDrivers={['Revenue Growth', 'Analyst Sentiment']} 
/>
```

## frontend/src/components/analysis/MetricCard.tsx
**Descripción:** Componente que muestra métricas financieras con categorías específicas (valoración, crecimiento, salud financiera, dividendos).  
**Relaciones:**  
- Usa `categoryColors` para colorear fondos según la categoría (azul para valoración, verde para crecimiento)  
- Muestra datos de `label` (nombre de la métrica), `value` (valor numérico), `nature` (si es calculada) y `source` (fecha de frescura)  
**Ejemplo de uso:**  
```tsx
<MetricCard 
  label="P/E Ratio" 
  value="15.2" 
  category="valuation" 
  nature="computed" 
  source="2023-10-05" 
/>
```

## frontend/src/components/analysis/PeerRankingTable.tsx
**Descripción:** Componente que compara métricas de una acción con sus pares (peers) y muestra rankings.  
**Relaciones:**  
- Muestra datos de `peers` (lista de acciones comparativas) y `rankings` (posiciones en métricas clave)  
- Muestra métricas como P/E, crecimiento de ingresos, ROE y D/E  
**Ejemplo de uso:**  
```tsx
<PeerRankingTable 
  ticker="AAPL" 
  peers={[{ ticker: "MSFT", pe_trailing: "35.2", ... }, ...]} 
  rankings={{ pe_trailing: 2, revenue_growth: 5 }} 
/>
```

## backend/app/services/price_history_service.py
**Descripción:** Servicio que consulta datos históricos de precios desde la base de datos.  
**Relaciones:**  
- Proporciona datos para los componentes frontend (HealthScoreGauge, MetricCard, PeerRankingTable)  
- Devuelve datos estructurados en `PriceSeriesResponse` con precios diarios, volumen y frescura  
**Ejemplo de uso:**  
```python
await PriceHistoryService().get_series(db, "AAPL", date(2023, 1, 1), date(2023, 10, 5))
```