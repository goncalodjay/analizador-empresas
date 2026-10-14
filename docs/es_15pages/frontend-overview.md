# Frontend Overview

## Configuración de Next.js
El archivo `next.config.js` configura la aplicación con Next.js 14.2.4 y habilita el modo estricto de React (`reactStrictMode`). Este modo ayuda a detectar problemas comunes en componentes React al renderizar en el servidor y el cliente.

**Ejemplo de uso:**
```bash
npm run dev
```

## Dependencias y Scripts
El `package.json` define las dependencias necesarias para el proyecto:
- **Next.js 14.2.4**: Framework para desarrollo de aplicaciones React.
- **React 18.3.1**: Biblioteca principal de React.
- **Tailwind CSS 3.4.4**: Para estilizado de componentes.
- **TypeScript 5.4.5**: Tipado estático para JavaScript.

Los scripts permiten:
- `dev`: Iniciar el servidor de desarrollo.
- `build`: Compilar la aplicación para producción.
- `start`: Ejecutar la aplicación en producción.

**Ejemplo de uso:**
```bash
npm install
npm run dev
```

## Docker
El `Dockerfile` permite empaquetar la aplicación en un contenedor con Node.js 18. Esto facilita la despliegue y el desarrollo en entornos consistentes.

**Ejemplo de uso:**
```bash
docker build -t stock-analyzer-frontend .
docker run -p 3000:3000 stock-analyzer-frontend
```

## TypeScript
El `tsconfig.json` configura TypeScript con:
- **Modulo de resolución**: `bundler` para compatibilidad con Next.js.
- **Rutas personalizadas**: `@/*` apunta a `./src/*` para modularizar el código.
- **Configuración de lints**: `strict` para validación estricta de tipos.

**Ejemplo de uso:**
```typescript
import { useState } from 'react';

export default function Example() {
  const [count, setCount] = useState(0);
  return <div>{count}</div>;
}
```

## Estilizado con Tailwind CSS
El `tailwind.config.ts` define colores personalizados, espaciados, fuentes y sombras. Estos estilos se aplican globalmente en la aplicación.

**Ejemplo de uso:**
```html
<div class="bg-primary-500 text-white p-4 rounded-lg shadow-prominent">
  Bienvenido
</div>
```

## Estructura del Proyecto
La estructura de archivos está organizada en:
- `src/`: Carpeta principal con componentes, páginas y lógica.
- `components/`: Contiene componentes reutilizables (aunque no se muestran archivos en este caso).
- `app/`: Carpeta para páginas y componentes de Next.js (aunque no se muestran archivos en este caso).
- `lib/`: Contiene lógica de negocio o utilidades (aunque no se muestran archivos en este caso).

Los archivos mencionados anteriormente se integran para crear una aplicación funcional con Next.js, TypeScript y Tailwind CSS.