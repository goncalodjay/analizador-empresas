# Archivos Fuente y su Relación

## `auth.py`
Maneja endpoints de autenticación y conexión a IOL (Interactive Brokers):
- `/login`: Autenticación de usuarios con verificación en la base de datos
- `/register`: Registro de nuevos usuarios
- Gestiona el flujo OAuth2 para conectar con IOL
- Almacena credenciales de IOL en la base de datos

## `iol.py`
Gestiona operaciones relacionadas con la cuenta de IOL:
- `/connect`: Conexión a IOL con autenticación OAuth2
- `/status`: Verifica el estado de la conexión
- `/sync-now`: Sincroniza manualmente el portafolio
- Consulta datos de portafolio y estado de cuenta desde la base de datos
- Usa `PortfolioSyncService` para sincronizar datos con IOL

## `prices.py`
Proporciona datos históricos de precios:
- `/prices/{ticker}`: Obtiene series de precios históricos
- Usa `PriceHistoryService` para recuperar datos
- Requiere autenticación de usuario (aunque los datos de precios no estén vinculados a un usuario específico)

## Relación entre componentes
1. **Autenticación**: `auth.py` maneja la autenticación de usuarios que permite acceder a los endpoints de IOL y precios
2. **Conexión IOL**: `iol.py` requiere autenticación de usuario para acceder a datos de portafolio
3. **Sincronización**: Los datos sincronizados por `sync-now` se almacenan en la base de datos para ser consultados por `/holdings` y `/account-status`
4. **Precios históricos**: `prices.py` proporciona datos complementarios para análisis de portafolio

## Ejemplos de uso
1. **Autenticación**:
```http
POST /login
Content-Type: application/json

{
  "username": "usuario1",
  "password": "contraseña123"
}
```

2. **Conexión a IOL**:
```http
POST /iol/connect
Content-Type: application/json

{
  "iol_username": "iol_usuario",
  "iol_password": "iol_contraseña"
}
```

3. **Sincronización manual**:
```http
POST /iol/sync-now
```

4. **Consulta de portafolio**:
```http
GET /iol/holdings
```

5. **Datos históricos de precios**:
```http
GET /prices/AAPL?from=2023-01-01&to=2023-12-31
```