# Authentication and User Management

## Overview
This system implements user authentication and management with a frontend React context and a backend FastAPI service. The frontend handles user sessions via a context provider, while the backend manages user data and secure token-based authentication.

---

## Key Components

### 1. Frontend: `auth-context.tsx`
**Purpose:** Manages authentication state and provides login/register/logout functionality.

**Key Features:**
- `AuthProvider`: Wraps the app to provide authentication context
- `useAuth`: Hook for accessing auth state and functions
- Uses `apiFetch` to communicate with backend endpoints

**Usage Example:**
```tsx
// In a component
const { user, loading, login } = useAuth();

if (loading) return <div>Loading...</div>;

if (!user) {
  return <Login onLogin={login} />;
}

return <Dashboard />;
```

---

### 2. Backend: `auth.py` (Pydantic Models)
**Purpose:** Defines data models for authentication operations.

**Models:**
- `UserCreate`: For user registration (email + password)
- `UserLogin`: For login requests (email + password)
- `UserOut`: Response model for user data
- `TokenResponse`: Structure for JWT tokens

**Example:**
```python
# Registration request
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

---

### 3. Backend: `user_service.py`
**Purpose:** Handles database operations for user management.

**Key Functions:**
- `get_user_by_email`: Find user by email
- `create_user`: Create new user with password hashing
- `get_user_by_id`: Find user by ID

**Security Note:** Uses `get_password_hash` from security module (not shown) for password storage.

---

### 4. Backend: `auth.py` (FastAPI Routes)
**Purpose:** Implements authentication endpoints.

**Endpoints:**
| Route         | Method | Description                  |
|---------------|--------|------------------------------|
| `/auth/register` | POST   | User registration            |
| `/auth/login`   | POST   | User login with JWT cookie   |
| `/auth/logout`  | POST   | Clear authentication cookie  |
| `/auth/me`      | GET    | Get current user data        |

**Example Response:**
```json
{
  "email": "user@example.com",
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "timezone": "America/Argentina/Buenos_Aires"
}
```

---

### 5. Security Implementation
- **JWT Cookies:** Access tokens are stored in HTTP-only cookies
- **Secure Flags:** Cookies use secure flags based on environment settings
- **Password Policies:** Enforces minimum 8-character passwords

**Test Coverage:**
- Validates secure cookie behavior in different environments
- Tests duplicate email detection
- Verifies password strength requirements
- Checks token expiration and invalidation

---

## Architecture Flow
1. **Registration:** Frontend sends data to `/auth/register` → Backend creates user
2. **Login:** Frontend sends credentials to `/auth/login` → Backend issues JWT cookie
3. **Protected Routes:** Frontend checks auth state via context → Backend validates cookie
4. **Logout:** Frontend clears cookie → Backend removes session data

---

## Security Considerations
- HTTP-only cookies prevent XSS attacks
- Secure flags ensure cookies are only sent over HTTPS
- Passwords are hashed before storage
- Token expiration is enforced via cookie validation

---

## Testing
- **Unit Tests:** Validate business logic (e.g., duplicate email checks)
- **Integration Tests:** Verify full auth flow (register → login → logout)
- **Security Tests:** Confirm cookie security headers and token validation

---

## Dependencies
- **Frontend:** React, Axios (for `apiFetch`)
- **Backend:** FastAPI, Pydantic, SQLAlchemy
- **Security:** JWT library (not shown in code) for token generation

---

## Error Handling
| Code    | Description                     |
|---------|---------------------------------|
| 409     | Duplicate email during signup   |
| 422     | Invalid email format            |
| 401     | Unauthorized (invalid credentials/token) |
| 403     | Forbidden (missing permissions) |