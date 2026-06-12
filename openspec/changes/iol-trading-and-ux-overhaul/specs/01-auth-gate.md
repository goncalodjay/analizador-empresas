# Spec: Authentication Gate

**Capability**: auth-gate  
**Status**: Pending Implementation  
**Scope**: Authentication UX redesign  
**Out of Scope**: Multi-user/multi-account, session migration from manual auth  

---

## Delta Requirements

### DeltaR1: Initial App State — Authentication Required
**Requirement**: The app MUST enforce authentication at the entry point. Until a user is authenticated, no navigation, sidebar, menu, or app shell components are visible or interactive.

**Rationale**: Current state allows unauthenticated navigation to dashboard, portfolio, and strategy pages. We must gate access at the application root.

**Acceptance Criteria**:
- On first load (no JWT cookie), the app renders the login screen in full viewport
- Login/register pages are the only screens accessible to unauthenticated users
- All other routes (dashboard, analysis, portfolio, strategy, watchlist) return a 302 redirect to /login if the user has no valid JWT
- No sidebar, navigation menu, or header app shell is rendered until JWT is present and valid

### DeltaR2: Post-Login App Shell Visibility
**Requirement**: After successful login (JWT obtained), the full app shell MUST appear: sidebar, header, navigation, and the requested route loads normally.

**Rationale**: After authentication, the user expects standard app navigation to be present.

**Acceptance Criteria**:
- POST /auth/login returns a JWT in httpOnly cookie (existing behavior, no change)
- After login, the app shell (sidebar, header, navigation) is mounted and visible
- Unauthenticated route navigation is no longer possible; all protected routes check JWT validity before render
- User can navigate between dashboard, analysis, portfolio, strategy, and watchlist via sidebar/header

### DeltaR3: JWT Validation Before Route Render
**Requirement**: Protected routes MUST validate the JWT before rendering. Invalid, expired, or missing JWTs MUST redirect to /login with an optional `next` query parameter for post-login redirect.

**Rationale**: Prevents authenticated session bypass and ensures consistent security posture across all protected routes.

**Acceptance Criteria**:
- Middleware or layout-level validator checks JWT on every protected route
- Expired or malformed JWT returns 302 redirect to /login?next=/previous-route
- Valid JWT allows route render
- User is redirected to `next` parameter URL after re-login if `next` is present and on-origin

### DeltaR4: Session Persistence
**Requirement**: Valid JWT cookies MUST persist across page refreshes and browser restarts (within the 30-min TTL).

**Rationale**: Maintains authentication state across user sessions.

**Acceptance Criteria**:
- httpOnly, Secure, and SameSite flags are set correctly on the JWT cookie
- User can refresh the browser (F5) on a protected route and remain authenticated
- User remains authenticated after closing and reopening the browser (if within 30-min TTL)
- Token expires after 30 minutes of issuance (existing behavior, no change)

---

## Acceptance Scenarios

### Scenario 1: Unauthenticated User Visits App

**Given** a user is not logged in (no JWT cookie)  
**When** they visit the app root or any protected route  
**Then** the login screen renders in full viewport and the app shell is not visible

---

### Scenario 2: User Logs In

**Given** the user is on the login screen  
**When** they enter valid credentials and submit  
**Then** the backend validates credentials, returns a JWT in httpOnly cookie, and the frontend navigates to /dashboard  
**And** the app shell (sidebar, header) is now visible  
**And** the dashboard page renders with IOL account data

---

### Scenario 3: User Navigates Protected Route

**Given** the user is authenticated (valid JWT)  
**When** they click "Analysis" in the sidebar  
**Then** the analysis page loads without re-checking authentication (JWT is already validated at app mount)

---

### Scenario 4: Session Expires

**Given** the user has been idle for more than 30 minutes (JWT TTL)  
**When** they try to navigate to a new page or perform an action  
**Then** the middleware detects an expired JWT, redirects to /login?next=/current-route  
**And** after re-login, they are redirected to the previous route

---

### Scenario 5: JWT Validation Fails (Malformed/Tampered Cookie)

**Given** the user has a malformed or tampered JWT cookie  
**When** they refresh the app or navigate to a protected route  
**Then** the middleware rejects the JWT, clears the cookie, and redirects to /login

---

## Implementation Notes

- **Existing JWT Auth**: Reuse the current cookie-based JWT auth (30-min TTL, bcrypt password hashing). No changes to the JWT generation/validation logic.
- **Route Protection**: Use Next.js middleware or layout-level guards (e.g., `next-auth` adapter or custom middleware) to enforce authentication at the route level.
- **UI Components**: Auth gate logic in the root layout or middleware; app shell components (sidebar, header) are conditional on JWT validity.
- **Onboarding**: IOL credential setup (Q6 decision) happens post-login, before dashboard access — covered in iol-connection spec.

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| JWT bypass or forgery | Validate JWT signature and TTL on every protected route; use httpOnly cookies |
| Session fixation | Regenerate session ID on login; set appropriate cookie flags (Secure, SameSite) |
| Redirect loop (login → next → login) | Validate `next` URL is same-origin before redirect; fail gracefully if `next` is invalid |
