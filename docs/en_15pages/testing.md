# Análisis de Archivos de Pruebas en el Proyecto

## Descripción General
Los archivos de pruebas implementan tests unitarios y de integración para validar el comportamiento del `IngestionService` y sus dependencias. Estos tests aseguran que el sistema calcule correctamente el puntaje compuesto, determine el veredicto adecuado y route correctamente a proveedores de precios según la moneda.

## Archivo: `test_services.py`
**Propósito:**  
Valida la lógica de cálculo del puntaje compuesto y el veredicto del `IngestionService`.

**Ejemplo de uso:**  
```python
assert result.composite == 72
assert result.verdict == "Accumulate"
```
- Simula una entrada con valores predefinidos
- Verifica que el cálculo del puntaje compuesto (72) y el veredicto ("Accumulate") sean correctos
- Usa mocks para simular la obtención de datos externos

## Archivo: `conftest.py`
**Propósito:**  
Configura el entorno de pruebas para todos los tests.

**Componentes clave:**
1. **Configuración de bases de datos:**  
   - Usa SQLite en memoria para tests
   - Crea tablas de la base de datos al iniciar
2. **Configuración de Redis:**  
   - Establece una conexión local para tests
3. **Cliente HTTP async:**  
   - Crea un cliente para probar endpoints de la API
   - Usa `ASGITransport` para integración con FastAPI

**Ejemplo de uso:**  
```python
async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
    yield client
```

## Archivo: `test_ingestion_currency_routing.py`
**Propósito:**  
Valida la lógica de routing basada en la moneda de los activos.

**Casos de prueba:**
1. **Moneda ARS:**  
   - Usa proveedor IOL para ticker "GGAL"
   - Verifica que se llame al proveedor correcto
2. **Moneda USD:**  
   - Usa proveedor yfinance para ticker "AAPL"
3. **Moneda por defecto:**  
   - Si no se especifica moneda, usa USD
4. **Moneda desde portafolio:**  
   - Si no se pasa moneda, la obtiene del portafolio

**Ejemplo de uso:**  
```python
mock_factory.assert_called_with(currency="ARS")
```

## Archivo: `test_strategies.py` (Faltante)
Este archivo no existe en el código proporcionado, pero debería contener tests para:
- Validar estrategias de inversión
- Verificar cálculos de rendimiento
- Probar lógica de recomendaciones

## Relación entre Archivos
- `conftest.py` proporciona la infraestructura para todos los tests
- `test_services.py` y `test_ingestion_currency_routing.py` usan el entorno configurado por `conftest.py`
- Todos los tests usan mocks para simular dependencias externas (proveedores de precios)