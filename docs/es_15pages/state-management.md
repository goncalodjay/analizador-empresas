# Gestión de Estado

## Contexto de Autenticación

El archivo `auth-context.tsx` define un contexto para la gestión de autenticación en la aplicación. Este contexto maneja el estado del usuario, incluyendo su autenticación, registro y cierre de sesión. Utiliza `React Context` para proporcionar acceso global al estado de autenticación.

### Funcionalidades principales
- **`AuthProvider`**: Proporciona el contexto de autenticación a toda la aplicación. Carga el estado del usuario al montar el componente.
- **`useAuth`**: Hook personalizado para acceder al contexto de autenticación en componentes.
- **`login`/`register`/`logout`**: Funciones que interactúan con el backend para manejar la autenticación del usuario.

### Ejemplo de uso
```tsx
// Componente que requiere autenticación
export default function ProtectedPage() {
  const { user, loading } = useAuth();
  
  if (loading) return <div>Cargando...</div>;
  if (!user) return <div>No autenticado</div>;

  return <div>Bienvenido, {user.email}</div>;
}
```

## Cliente de API

El archivo `api.ts` implementa un cliente de API reutilizable para comunicarse con el backend. Maneja errores, autenticación y solicitudes HTTP, y proporciona clientes específicos para diferentes endpoints.

### Funcionalidades principales
- **`apiFetch`**: Función principal para realizar solicitudes HTTP. Maneja errores y respuestas, lanzando `ApiError` en caso de fallos.
- **Clientes específicos**:
  - **Estrategias**: `getStrategies`, `createStrategy`, etc.
  - **Historial de precios**: `getPriceHistory`
  - **Feed de noticias**: `getNews`

### Ejemplo de uso
```ts
// Ejemplo de llamada a la API para obtener estrategias
async function fetchStrategies() {
  try {
    const strategies = await getStrategies();
    console.log('Estrategias:', strategies);
  } catch (error) {
    if (error instanceof ApiError) {
      console.error(`Error ${error.status}: ${error.message}`);
    }
  }
}
```

## Relación entre los archivos

- **`auth-context.tsx`** utiliza `apiFetch` desde `api.ts` para realizar solicitudes al backend (ej: `/auth/login`, `/auth/register`).
- **`api.ts`** proporciona la infraestructura para todas las solicitudes HTTP, incluyendo manejo de errores y autenticación.
- **`AuthProvider`** carga el estado del usuario al montar, usando `apiFetch` para solicitar `/auth/me`.