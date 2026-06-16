# Spec: UX Overhaul — Design System and Performance

**Capability**: ux-overhaul  
**Status**: Pending Implementation  
**Scope**: Design system foundations (tokens, components), performance requirements (no layout regressions, fast loads), applies across all pages  
**Out of Scope**: Dark mode, custom theme customization, advanced animations, mobile app, design system libraries (component library development is deferred to Phase 2)  

---

## Delta Requirements

### DeltaR1: Design System Tokens
**Requirement**: The frontend MUST establish a consistent design system using design tokens for colors, typography, spacing, and shadows. Tokens MUST be defined in a centralized location (Tailwind config or CSS variables) and applied consistently across all pages.

**Rationale**: Current state has ad-hoc Tailwind classes with no centralized design language. A token system ensures consistency and simplifies future UX updates.

**Acceptance Criteria**:
- Design tokens are defined in Tailwind configuration (`tailwind.config.ts`) or CSS variables file (e.g., `styles/tokens.css`)
- Token categories:
  1. **Colors**: Primary, secondary, success, warning, error, neutral (grayscale)
  2. **Typography**: Font families, sizes, weights, line heights
  3. **Spacing**: Scale (4px, 8px, 12px, 16px, 24px, 32px, etc.)
  4. **Shadows**: Subtle, medium, prominent
  5. **Borders**: Radius (0, 4px, 8px, 16px)
  6. **Transitions**: Duration, easing
- Tokens follow a naming convention (e.g., `color-primary-500`, `spacing-md`)
- All existing pages (login, dashboard, portfolio, analysis, strategy, watchlist) use tokens consistently
- Tokens are applied to 80%+ of UI elements by the end of the phase
- Documentation of tokens is included (e.g., Storybook or design-tokens.md file)

### DeltaR2: Consistent Component Library (Base)
**Requirement**: The frontend MUST establish a base set of reusable, styled components: Button, Input, Card, Modal, Badge, Alert, Table, etc. Components MUST use design tokens and follow the design system. Custom component development is deferred; MVP uses Tailwind + radix-ui or similar headless library.

**Rationale**: Reusable components reduce duplication and ensure consistent UX across pages.

**Acceptance Criteria**:
- Base components are created in a `components/` directory structure:
  - `Button.tsx` (primary, secondary, danger variants)
  - `Input.tsx` (text, password, email, number)
  - `Card.tsx` (container for grouped content)
  - `Modal.tsx` (dialog/overlay)
  - `Badge.tsx` (status/tag display)
  - `Alert.tsx` (success, warning, error messages)
  - `Table.tsx` (data display with sorting, deferred pagination)
  - `Select.tsx` (dropdown selection)
  - `Checkbox.tsx` and `Radio.tsx` (form controls)
- Each component accepts design token-based styling props (e.g., `variant`, `size`, `color`)
- Components are composed from headless UI library (e.g., radix-ui) or Tailwind utilities
- Components include basic accessibility (ARIA labels, focus states, keyboard navigation)
- All pages use these components instead of raw Tailwind classes

### DeltaR3: Page Layout Consistency
**Requirement**: All pages MUST follow a consistent layout structure: header (with nav), sidebar, main content area, footer (optional). The auth gate applies to the entire layout (sidebar and nav hidden until authenticated).

**Rationale**: Consistent layout reduces cognitive load and improves navigation.

**Acceptance Criteria**:
- Root layout defines:
  1. **Header**: Logo, title, connection status (IOL), user menu (logout)
  2. **Sidebar**: Navigation links (Dashboard, Analysis, Portfolio, Strategies, Watchlist, Settings) with icons
  3. **Main Content**: Page-specific content area
  4. **Footer**: Optional legal/links (deferred to Phase 2)
- Layout is responsive:
  - Desktop: Sidebar left, main content right (sidebar is 250px, collapsible)
  - Tablet: Sidebar collapses to icon-only or hamburger menu
  - Mobile: Hamburger menu, full-width main content (mobile display deferred)
- All pages (dashboard, analysis, portfolio, strategy, watchlist) use the same layout
- Consistent spacing and padding across pages (using design tokens)

### DeltaR4: Performance Baselines
**Requirement**: All pages MUST meet performance baselines: page load < 2 seconds (Core Web Vitals), no Cumulative Layout Shift (CLS) regressions, fast interactive (TTI < 3 seconds). Performance is measured using Lighthouse or similar tools.

**Rationale**: Slow pages frustrate users and reduce engagement. Baselines ensure the UX remains snappy as features are added.

**Acceptance Criteria**:
- **Page Load Time**: < 2 seconds (time to first contentful paint, FCP)
- **Time to Interactive (TTI)**: < 3 seconds
- **Cumulative Layout Shift (CLS)**: < 0.1 (no major layout regressions)
- **First Input Delay (FID)**: < 100ms
- Performance is measured on a throttled 4G connection (simulated, using DevTools or Lighthouse)
- Each page is profiled at the end of the phase; regressions are identified and fixed
- No images are unoptimized (lazy loading, responsive sizes, WebP format if available)
- Code splitting is used to reduce bundle size (route-based splitting in Next.js)
- CSS and JS are minified and bundled efficiently

### DeltaR5: Color Palette and Typography
**Requirement**: The app MUST use a modern, accessible color palette with sufficient contrast (WCAG AA minimum). Typography MUST be legible and use a consistent font stack.

**Rationale**: Accessible design benefits all users; good typography improves readability.

**Acceptance Criteria**:
- **Color Palette**:
  - Primary: Blue or similar (e.g., `#0066cc`)
  - Secondary: Neutral or complementary
  - Success: Green (e.g., `#00aa00`)
  - Warning: Yellow/Orange (e.g., `#ff8800`)
  - Error: Red (e.g., `#cc0000`)
  - Neutral: Grayscale (white, light gray, medium gray, dark gray, black)
  - All colors meet WCAG AA contrast ratio (4.5:1 minimum for text)
- **Typography**:
  - Font Family: Sans-serif (e.g., Inter, -apple-system, Segoe UI)
  - Font Sizes: 12px, 14px, 16px, 18px, 24px, 32px (scale)
  - Font Weights: 400 (regular), 600 (semibold), 700 (bold)
  - Line Heights: 1.4, 1.5, 1.6 (for readability)
  - Heading Hierarchy: h1–h6 with consistent sizing and weight

### DeltaR6: Responsive Design Breakpoints
**Requirement**: The app MUST be responsive across desktop, tablet, and mobile viewports. Breakpoints are consistent and follow Tailwind defaults (or custom tailored breakpoints).

**Rationale**: Users access the app on different devices; responsive design ensures usability everywhere.

**Acceptance Criteria**:
- Breakpoints (aligned with Tailwind):
  - Mobile: < 640px (sm)
  - Tablet: 640px–1024px (md, lg)
  - Desktop: > 1024px (lg, xl)
- Each page is tested on:
  - Desktop (1920x1080, 1366x768)
  - Tablet (768x1024, 834x1112)
  - Mobile (375x667, 414x896) — basic responsive layout only in MVP
- No horizontal scrolling on any viewport
- Touch targets (buttons, links) are ≥ 44px on mobile
- Text is readable without zoom on all viewports
- Mobile display is deferred to Phase 2; MVP is desktop-first with responsive layout but not full mobile UX

### DeltaR7: Accessibility Standards
**Requirement**: The app MUST meet WCAG 2.1 AA accessibility standards for all interactive elements. Minimum requirements: keyboard navigation, ARIA labels, semantic HTML, color contrast.

**Rationale**: Accessibility ensures the app is usable by all users, including those with disabilities.

**Acceptance Criteria**:
- **Keyboard Navigation**: All interactive elements (buttons, links, inputs) are reachable via Tab key; tab order is logical
- **ARIA Labels**: Buttons and form inputs have descriptive labels or aria-label attributes
- **Semantic HTML**: Use `<button>`, `<a>`, `<label>` instead of `<div>` for interactive elements
- **Color Contrast**: Text colors meet WCAG AA (4.5:1 for regular text, 3:1 for large text)
- **Focus Indicators**: All interactive elements have visible focus styles (not just outline, custom focus rings acceptable)
- **Form Accessibility**: All form inputs have associated `<label>` elements; error messages are linked via aria-describedby
- **Image Alt Text**: All images have descriptive alt text (or alt="" if decorative)
- **Heading Structure**: Pages use a logical h1–h6 hierarchy; no skipped levels
- Accessibility is tested using tools like axe DevTools, WAVE, or Lighthouse

---

## Design System File Structure

```
src/
├── styles/
│   ├── globals.css (reset, global styles)
│   ├── tokens.css (design tokens: colors, spacing, typography)
│   └── tailwind.css (Tailwind imports)
├── components/
│   ├── Button.tsx
│   ├── Input.tsx
│   ├── Card.tsx
│   ├── Modal.tsx
│   ├── Badge.tsx
│   ├── Alert.tsx
│   ├── Table.tsx
│   ├── Select.tsx
│   ├── Checkbox.tsx
│   ├── Radio.tsx
│   └── [other base components]
├── layouts/
│   ├── RootLayout.tsx (header, sidebar, main)
│   └── AuthLayout.tsx (login/register, no sidebar)
├── pages/
│   ├── dashboard.tsx (uses RootLayout, base components)
│   ├── analysis/[ticker].tsx
│   ├── portfolio.tsx
│   ├── strategies.tsx
│   ├── watchlist.tsx
│   └── login.tsx (uses AuthLayout)
└── tailwind.config.ts (design tokens configuration)
```

---

## Tailwind Configuration Example

```typescript
// tailwind.config.ts
export default {
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f7ff',
          500: '#0066cc',
          600: '#0052a3',
          700: '#003d7a',
        },
        success: '#00aa00',
        warning: '#ff8800',
        error: '#cc0000',
      },
      spacing: {
        xs: '4px',
        sm: '8px',
        md: '12px',
        lg: '16px',
        xl: '24px',
      },
      typography: {
        fontFamily: {
          sans: ['Inter', '-apple-system', 'Segoe UI'],
        },
        fontSize: {
          xs: '12px',
          sm: '14px',
          base: '16px',
          lg: '18px',
          xl: '24px',
          '2xl': '32px',
        },
      },
      borderRadius: {
        sm: '4px',
        md: '8px',
        lg: '16px',
      },
    },
  },
};
```

---

## Acceptance Scenarios

### Scenario 1: Consistent Header and Sidebar on All Pages

**Given** a user is logged in and on the dashboard  
**When** they click "Analysis" in the sidebar  
**Then** the Analysis page loads with the same header and sidebar visible  
**And** the layout, spacing, and typography are consistent with the dashboard  

---

### Scenario 2: Design Tokens Applied to All Pages

**Given** the design system is implemented  
**When** a designer or developer needs to change the primary color (e.g., from blue to teal)  
**Then** they update the token in `tailwind.config.ts` (one place)  
**And** all pages reflect the new color without manual updates  

---

### Scenario 3: Responsive Layout on Tablet

**Given** a user accesses the dashboard on a tablet (1024px width)  
**When** the page loads  
**Then** the sidebar is collapsed to an icon-only menu (or visible but narrower)  
**And** the main content area expands to fill the available width  
**And** all interactive elements are still accessible (touch targets ≥ 44px)  

---

### Scenario 4: Keyboard Navigation

**Given** a user is on the login page  
**When** they press Tab repeatedly  
**Then** the focus moves through: Email Input → Password Input → Login Button → "Forgot Password" Link  
**And** each element shows a clear focus indicator (e.g., blue outline)  

---

### Scenario 5: Performance Baseline

**Given** the dashboard page is loaded  
**When** measured using Lighthouse on throttled 4G  
**Then** the page achieves:
- First Contentful Paint (FCP): < 2 seconds
- Time to Interactive (TTI): < 3 seconds
- Cumulative Layout Shift (CLS): < 0.1  

---

### Scenario 6: Color Contrast Meets WCAG AA

**Given** a designer applies text colors from the design palette  
**When** tested with a contrast checker  
**Then** all text colors meet WCAG AA minimum (4.5:1 for regular text, 3:1 for large text)  

---

### Scenario 7: Button Component Variants

**Given** the Button component is used across pages  
**When** rendered with variant="primary"  
**Then** it displays with primary color, primary size, and primary hover state  
**When** rendered with variant="secondary"  
**Then** it displays with secondary color and styling  

---

## Implementation Notes

- **Tailwind CSS**: Use Tailwind as the primary styling approach; custom CSS for complex layouts or animations
- **Headless UI**: Radix UI, Headless UI, or Shadcn/ui for unstyled, accessible components
- **Component Library**: Component source of truth is in `src/components/`; document each component with props and examples
- **Design Tokens**: Keep tokens DRY; avoid duplicate color or spacing definitions
- **Performance Optimization**:
  - Use Next.js Image component for images (automatic optimization)
  - Enable static generation for pages that don't change frequently
  - Code-split route-based (Next.js automatic)
  - Minify CSS and JS (Next.js automatic in production)
- **Accessibility Testing**: Use axe DevTools browser extension during development; run automated checks in CI/CD
- **Design Documentation**: Create a design-tokens.md or Storybook page documenting the design system (deferred to Phase 2 if Storybook is not in MVP)

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Design tokens not adopted consistently | Code review; use linting rules to enforce token usage |
| Performance regressions as features are added | Continuous Lighthouse testing in CI/CD; alert on regressions |
| Accessibility issues missed | Automated axe checks in CI/CD; manual accessibility audit pre-launch |
| Component API conflicts or duplication | Clear component directory structure; document component props |
| Mobile UX is suboptimal (deferred to Phase 2) | Focus on desktop/tablet in MVP; document mobile gaps for Phase 2 |
| Layout shifts during page load | Use fixed dimensions for images; avoid font-swap janky behavior |
