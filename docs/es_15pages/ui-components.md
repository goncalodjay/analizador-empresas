# UI Components

Esta sección describe los componentes de interfaz de usuario (UI) y su relación con la estructura del proyecto.

## Estructura de archivos

### frontend/src/components/**
Este directorio contiene los componentes reutilizables de la interfaz de usuario. Aunque no se encontraron archivos específicos, típicamente incluiría elementos como:
- Botones personalizados
- Formularios con validación
- Componentes de navegación
- Elementos de visualización de datos

Estos componentes son importados y utilizados en diferentes partes de la aplicación para mantener la coherencia visual y la reutilización de código.

### frontend/src/app/**
Este directorio alberga la lógica principal de la aplicación. Aunque no se encontraron archivos específicos, generalmente incluiría:
- Configuración de rutas (routing)
- Gestión de estado (state management)
- Componentes de la interfaz principal
- Integración con servicios o APIs

La relación entre `components` y `app` es que los componentes definidos en `components` son importados y utilizados dentro de los archivos de `app` para construir la interfaz completa.

## Ejemplos de uso (estructura típica)

```tsx
// Ejemplo de un componente reutilizable (archivo: Button.tsx)
import React from 'react';

interface ButtonProps {
  label: string;
  onClick: () => void;
}

const Button: React.FC<ButtonProps> = ({ label, onClick }) => {
  return <button onClick={onClick}>{label}</button>;
};

export default Button;
```

```tsx
// Ejemplo de uso en la aplicación principal (archivo: App.tsx)
import React from 'react';
import Button from '../components/Button';

const App: React.FC = () => {
  const handleClick = () => {
    alert('Botón presionado!');
  };

  return (
    <div>
      <h1>Aplicación Principal</h1>
      <Button label="Haz clic aquí" onClick={handleClick} />
    </div>
  );
};

export default App;
```

Nota: Los archivos específicos no fueron encontrados en los directorios mencionados. La información proporcionada se basa en una estructura de proyecto estándar.