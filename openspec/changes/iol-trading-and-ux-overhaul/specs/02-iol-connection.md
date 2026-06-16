# Spec: IOL OAuth2 Connection and Credential Management

**Capability**: iol-connection  
**Status**: Pending Implementation  
**Scope**: IOL OAuth2 authentication, encrypted credential storage, backend token lifecycle, onboarding flow  
**Out of Scope**: Trading endpoints (buy/sell), IOL sandbox/testing, multi-account support, credential rotation UI  

---

## Delta Requirements

### DeltaR1: IOL Credentials Onboarding on First Login
**Requirement**: Immediately after a user logs in via email/password, they MUST be prompted to enter their IOL username and password (OAuth2 Resource Owner Password Credentials setup). The app MUST NOT allow access to the dashboard until IOL credentials are validated and stored.

**Rationale**: IOL credentials are required to fetch portfolio and account data. Deferring setup creates a broken user experience (dashboard without data). Early validation ensures credentials are correct before storing.

**Acceptance Criteria**:
- POST /auth/login succeeds; user is authenticated with JWT
- Frontend detects first-time IOL setup (e.g., `user.iol_connected == false` flag in JWT or user object)
- User is redirected to /onboarding/iol-setup (not /dashboard)
- /onboarding/iol-setup displays a form: "IOL Username" and "IOL Password" text inputs, submit button
- User enters IOL credentials and clicks submit
- Frontend POSTs to POST /iol/setup with `{iol_username: "...", iol_password: "..."}`
- Backend validates credentials by calling IOL /token endpoint
- If validation succeeds, backend encrypts and stores credentials securely (encrypted env var, vault, or secrets manager)
- Backend sets `user.iol_connected = true` in the JWT
- Frontend redirects to /dashboard
- If validation fails, backend returns 400/401 with error message; frontend displays error and allows retry

### DeltaR2: Backend IOL OAuth2 Client (Resource Owner Password Flow)
**Requirement**: The backend MUST implement an IOL OAuth2 client using the Resource Owner Password Credentials flow. The client MUST obtain a bearer token (15-min TTL) and a refresh token from IOL. The backend MUST store the refresh token securely and use it to proactively refresh the bearer token before expiry.

**Rationale**: IOL's tight 15-min TTL requires backend-only token management; the frontend never holds IOL tokens. Proactive refresh prevents token expiry mid-request.

**Acceptance Criteria**:
- Backend FastAPI service includes an `IOLClient` class
- `IOLClient.authenticate(username, password)` calls POST /token at IOL API and obtains:
  - `access_token` (bearer token, 15-min TTL)
  - `refresh_token` (long-lived)
  - Token expiry timestamp
- `IOLClient.refresh_token(refresh_token)` calls POST /token with refresh token grant type and obtains a new access_token
- Refresh token is stored in encrypted form in the database (encrypted column in `user.iol_refresh_token` or similar)
- Access token is held in memory (Redis) with expiry tracking; not persisted to disk
- Backend runs a background job every 13 minutes to refresh all users' access tokens that are within 2 minutes of expiry

### DeltaR3: Proactive Token Refresh Job
**Requirement**: The backend MUST run a periodic background job (every ~13 minutes) to proactively refresh IOL access tokens for all authenticated users. The job MUST check token expiry and refresh tokens within 2 minutes of expiry. The job MUST handle refresh failures gracefully (log, alert, but do not crash).

**Rationale**: Prevents token expiry during active user requests. A 13-min interval ensures refresh completes before the 15-min TTL.

**Acceptance Criteria**:
- Background job is implemented as a FastAPI background task or Celery task (depending on deployment model)
- Job runs every 13 minutes (configurable interval)
- For each user with an active IOL connection, the job checks the access token expiry in Redis
- If expiry is within 2 minutes, the job calls `IOLClient.refresh_token()` with the user's stored refresh token
- New access token is stored in Redis with updated expiry
- If refresh fails (e.g., IOL API down, refresh token expired), the job logs the error and marks the user's IOL connection as `needs_reauth = true` (optional, for later recovery UI)
- Job does not raise exceptions; failures are logged and reported via monitoring

### DeltaR4: Encrypted Credential Storage
**Requirement**: IOL credentials (username and refresh token) MUST be encrypted at rest. Encryption keys MUST NOT be derived from user passwords. The backend MUST use industry-standard encryption (AES-256 or equivalent) and secure key management.

**Rationale**: IOL credentials grant access to real money; encryption at rest protects against database breaches and accidental exposure.

**Acceptance Criteria**:
- IOL credentials (username, refresh token) are encrypted before insertion into the database
- Encryption key is stored securely (environment variable, AWS Secrets Manager, HashiCorp Vault, or similar)
- Encryption key is NOT derived from or stored alongside user password
- Decryption happens in-memory only; credentials are never logged or exposed in error messages
- Encryption algorithm is AES-256-GCM or equivalent; key size is 256 bits
- Rotation of encryption keys does not break existing encrypted data (e.g., envelope encryption pattern)

### DeltaR5: IOL Connection Status Endpoint
**Requirement**: The backend MUST provide a GET /iol/status endpoint that returns the current connection status (connected/disconnected/needs_reauth), account summary from IOL, and metadata. The frontend MUST display connection status in the dashboard or settings.

**Rationale**: Users need to know if their IOL connection is active and valid. Status endpoint provides a single source of truth for connection health.

**Acceptance Criteria**:
- GET /iol/status (requires JWT) returns:
  ```json
  {
    "connected": true,
    "account_name": "Usuario IOL",
    "cash_balance": 50000.00,
    "currency": "ARS",
    "last_sync": "2026-06-12T17:30:00Z",
    "needs_reauth": false
  }
  ```
- If connection is not active, `connected: false` and optional `reason: "token_expired" | "credentials_invalid"`
- Endpoint caches the response for 5 minutes (Redis) to avoid hammering IOL API
- If IOL API is unreachable, endpoint returns cached last-known state (graceful degradation)
- Frontend displays connection status in the dashboard header or settings; shows "Connected to IOL" with account name, or "IOL Connection Required" if not connected

---

## Acceptance Scenarios

### Scenario 1: New User Logs In, Completes IOL Setup

**Given** a user is new (no prior IOL connection)  
**When** they complete email/password login  
**Then** they are redirected to /onboarding/iol-setup  
**And** the form displays "IOL Username" and "IOL Password" fields  
**When** they enter valid IOL credentials and click "Connect to IOL"  
**Then** the backend validates credentials by calling IOL /token endpoint  
**And** the backend encrypts and stores the refresh token  
**And** the backend sets `iol_connected = true` in the user's JWT  
**And** the frontend redirects to /dashboard  

---

### Scenario 2: IOL Credential Validation Fails

**Given** the user is on the IOL setup form  
**When** they enter invalid IOL credentials and click "Connect to IOL"  
**Then** the backend calls IOL /token and receives a 401  
**And** the backend returns 401 Unauthorized to the frontend  
**And** the frontend displays an error message: "Invalid IOL username or password. Please try again."  
**And** the form remains on /onboarding/iol-setup for retry  

---

### Scenario 3: Token Refresh Job Runs Successfully

**Given** a user has an active IOL connection with an access token that expires in 5 minutes  
**When** the background refresh job runs (every 13 minutes)  
**Then** the job detects that the token is within 2 minutes of expiry  
**And** the job calls IOL /token with the user's refresh token  
**And** IOL returns a new access token  
**And** the job stores the new access token in Redis with a new expiry timestamp  
**And** subsequent requests to IOL endpoints use the new token without interruption  

---

### Scenario 4: Token Refresh Fails (IOL API Down)

**Given** the background refresh job is running  
**And** a user's token is within 2 minutes of expiry  
**When** the job calls IOL /token to refresh  
**Then** IOL API is unreachable (500 error)  
**And** the job logs the error but does NOT crash  
**And** the job marks the user's connection as `needs_reauth = true` (optional, for dashboard warning)  
**And** subsequent requests to IOL endpoints use the expired token  
**And** if the expired token is used, the endpoint returns a 401 and the user is prompted to re-authenticate  

---

### Scenario 5: Check IOL Connection Status

**Given** a user is logged in and their IOL connection is active  
**When** the frontend calls GET /iol/status  
**Then** the backend returns:
```json
{
  "connected": true,
  "account_name": "Juan Pérez",
  "cash_balance": 125000.50,
  "currency": "ARS",
  "last_sync": "2026-06-12T17:45:00Z",
  "needs_reauth": false
}
```
**And** the frontend displays "Connected to IOL: Juan Pérez" in the dashboard header  

---

## Implementation Notes

- **Encryption Library**: Use `cryptography` (Python) for AES-256-GCM; store encryption key in `ENCRYPTION_KEY` environment variable or Secrets Manager
- **Token Storage**: Access tokens in Redis with key `iol:access_token:{user_id}` and expiry set to token TTL minus 2 minutes
- **Refresh Token Storage**: Encrypt and store in PostgreSQL `user.iol_refresh_token` column (encrypted text)
- **Onboarding Flow**: POST /iol/setup endpoint validates, encrypts, and stores credentials; returns 200/401
- **Background Job**: FastAPI `BackgroundTasks` or Celery task; runs on app startup or via scheduler
- **Error Handling**: Token expiry mid-request returns 401; frontend catches and redirects to /onboarding/iol-setup or /settings/iol-reconnect
- **OAuth2 Scopes**: IOL Resource Owner Password flow does not use scopes; request bearer token with no scope parameter

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| IOL credentials exposed in logs | Never log credentials; use structured logging with sanitization |
| Token expiry during request | Proactive refresh job ensures tokens are valid within a 2-min buffer |
| Encryption key compromise | Store key in Secrets Manager, rotate regularly, use envelope encryption pattern |
| Refresh token invalidation | Monitor refresh failures; alert user and prompt re-authentication |
| IOL API unavailability | Cache last-known connection state; degrade gracefully; provide manual reconnect option |
