# Frontend Layout and Routing

This documentation explains the structure and relationship of frontend routing and layout components in the application.

## Page Structure
The application uses a pages-based routing system where each file in the `frontend/src/pages/` directory corresponds to a route:
- `index.tsx`: Homepage component (root route `/`)
- `strategy.tsx`: Strategy page (`/strategy`)
- `portfolio.tsx`: Portfolio page (`/portfolio`)
- `analysis.tsx`: Analysis page (`/analysis`)
- `auth.tsx`: Authentication page (`/auth`)
- `404.tsx`: Custom 404 error page for unmatched routes

## Layout System
The `_app.tsx` file serves as the main layout container, providing a consistent structure across all pages. It typically includes:
- Global styles
- Navigation menu
- Layout containers for different page types

## Routing Behavior
- All pages are accessible via their respective routes (e.g., `/strategy`, `/portfolio`)
- The `404.tsx` page handles invalid routes and provides a custom error experience
- The layout defined in `_app.tsx` wraps all page components

## Example Navigation Flow
1. User visits root route (`/`) → rendered by `index.tsx`
2. User navigates to `/strategy` → rendered by `strategy.tsx` within the layout
3. User accesses non-existent route (e.g., `/unknown`) → displays `404.tsx`

The routing system follows standard Next.js conventions for client-side navigation and server-side rendering.