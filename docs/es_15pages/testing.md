# Testing

## Archivos fuente y su relación

### `backend/pytest.ini`
Configura pytest para ejecutar pruebas asincrónicas y especifica el directorio de pruebas.  
- `asyncio_mode = auto`: Permite pruebas asincrónicas con `async/await`.  
- `testpaths = tests`: Indica que las pruebas están en el directorio `tests`.

### `backend/tests/conftest.py`
Proporciona configuración compartida para pruebas, incluyendo:
- **Variables de entorno**:  
  - `DATABASE_URL`: URL de la base de datos SQLite para pruebas.  
  - `REDIS_URL`: URL de Redis para pruebas.  
  - `SECRET_KEY`: Clave secreta para pruebas.  
- **Fixture `async_client`**:  
  - Crea una base de datos SQLite en memoria.  
  - Configura un cliente HTTP para probar la aplicación.  
  - Reinicia el estado después de cada prueba.  
  - Ejemplo de uso:  
    ```python
    async def test_example(async_client):
        response = await async_client.get("/api/endpoint")
        assert response.status_code == 200
    ```

### `backend/tests/**/*`
Directorio donde se colocan los archivos de prueba individuales (no encontrados en el contexto, pero esperados por `pytest`).  

## Relación entre archivos
- `pytest.ini` dirige pytest a `tests/`.  
- `conftest.py` prepara el entorno de pruebas (base de datos, cliente HTTP) para todos los archivos en `tests/`.  
- Los archivos de prueba en `tests/` usan `async_client` para acceder a la API.