# Security

## Descripción general
La seguridad del sistema se implementa mediante tres componentes principales: manejo de contraseñas, autenticación con JWT y pruebas de seguridad de cookies. Estos elementos trabajan juntos para garantizar la protección de los datos y la autenticación de los usuarios.

## Archivo: backend/app/core/security.py
Este archivo implementa la lógica de seguridad fundamental del sistema:

### Funcionalidades clave
1. **Hashing de contraseñas**  
   - `get_password_hash`: Cifra contraseñas usando bcrypt
   - `verify_password`: Valida contraseñas en texto plano contra su hash

2. **Autenticación con JWT**  
   - `create_access_token`: Genera tokens de acceso con expiración configurable
   - `decode_access_token`: Valida y decodifica tokens JWT

### Ejemplo de uso
```python
# Crear token de acceso
token = create_access_token({
    "sub": "user@example.com",
    "scope": "read:prices"
}, timedelta(hours=2))

# Decodificar token
payload = decode_access_token(token)
print(payload["sub"])  # user@example.com
```

## Archivo: backend/tests/test_auth_secure_cookie.py
Este archivo contiene pruebas para verificar la seguridad de las cookies de sesión:

### Funcionalidades clave
1. **Configuración de cookies seguras**  
   - Verifica que las cookies de sesión tengan el atributo `Secure` cuando el entorno lo requiera
   - Asegura que las cookies sean `HttpOnly` y `SameSite=lax` por defecto

2. **Manejo de cierre de sesión**  
   - Verifica que el cierre de sesión elimine correctamente el token de sesión

### Ejemplo de prueba
```python
# Prueba de cierre de sesión
logout_resp = await async_client.post("/auth/logout")
assert "Max-Age=0" in logout_resp.headers.get("set-cookie", "")
```

## Relación entre componentes
- El módulo `security.py` proporciona la infraestructura para autenticar usuarios y generar tokens
- Las pruebas en `test_auth_secure_cookie.py` aseguran que los tokens se manejen de forma segura en el navegador
- El sistema de proveedores en `base.py` utiliza estos tokens para autorizar acceso a datos sensibles

## Consideraciones importantes
1. Los tokens JWT son firmados con la clave secreta configurada en `settings.SECRET_KEY`
2. La expiración de tokens se controla mediante `settings.ACCESS_TOKEN_EXPIRE_MINUTES`
3. La seguridad de cookies depende de la variable de entorno `SECURE_COOKIE_ENABLED`