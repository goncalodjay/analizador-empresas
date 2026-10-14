# Authentication

## Descripción general
La implementación de autenticación maneja el registro, inicio de sesión, y gestión de sesión para el sistema. Combina un contexto de estado en el frontend con endpoints seguros en el backend, utilizando cookies HTTP-only para la autenticación.

## Componentes clave

### 1. Contexto de autenticación (frontend)
El archivo `auth-context.tsx` define un contexto para gestionar el estado de autenticación:

```typescript
// frontend/src/lib/auth-context.tsx
const AuthContext = createContext<AuthContextType | undefined>(undefined);
```

Proporciona funcionalidades:
- `login(email, password)`: Autentica al usuario y actualiza el estado
- `register(email, password)`: Crea un nuevo usuario
- `logout()`: Finaliza la sesión
- `user`: Estado actual del usuario autenticado
- `loading`: Indica si se está cargando el estado

**Ejemplo de uso:**
```typescript
const { user, login } = useAuth();
if (user) {
  return <WelcomePage user={user} />;
}
```

### 2. Modelo de usuario (backend)
El archivo `user.py` define la estructura de la tabla de usuarios en la base de datos:

```python
# backend/app/models/user.py
class User(Base):
    id: Mapped[uuid.UUID]
    email: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str]
    # ... otros campos
```

Relaciones importantes:
- `portfolio_positions`: Posiciones de cartera
- `watchlists`: Listas de seguimiento
- `strategies`: Estrategias de inversión

### 3. Endpoints de autenticación
El archivo `auth.py` define las rutas de autenticación:

```python
# backend/app/api/auth.py
router = APIRouter(prefix="/auth")

@router.post("/register")
async def register(payload: UserCreate, db: AsyncSession):
    # Crea un nuevo usuario
    return created_user

@router.post("/login")
async def login(payload: UserLogin, db: AsyncSession):
    # Valida credenciales y crea cookie
    return user_data

@router.post("/logout")
async def logout():
    # Elimina la cookie de autenticación
    return Response(status_code=204)

@router.get("/me")
async def me(current_user: User = Depends(get_current_user)):
    # Devuelve datos del usuario autenticado
    return current_user
```

### 4. Gestión de cookies
Los endpoints de login y logout manejan cookies seguras:

```python
response.set_cookie(
    key="access_token",
    value=token,
    httponly=True,
    secure=settings.SECURE_COOKIE_ENABLED,
    samesite="lax"
)
```

### 5. Validaciones
El sistema incluye validaciones para:
- Email duplicado en registro
- Contraseñas demasiado cortas
- Credenciales inválidas
- Tokens expirados

## Flujo de autenticación
1. El usuario ingresa sus credenciales
2. El backend valida las credenciales y genera un token
3. El token se almacena en una cookie HTTP-only
4. El frontend verifica el estado de autenticación mediante el contexto
5. Los endpoints protegidos requieren la cookie para acceder

## Pruebas
El archivo `test_auth.py` incluye pruebas para:
- Registro exitoso y duplicado
- Inicio de sesión correcto y con credenciales inválidas
- Verificación de tokens expirados
- Gestión correcta de cookies HTTP-only

## Seguridad
- Las contraseñas se almacenan en hash
- Las cookies son HTTP-only y seguras
- Los tokens tienen expiración definida
- Se manejan correctamente los errores de autenticación