import pytest


REGISTER_URL = "/auth/register"
LOGIN_URL = "/auth/login"
LOGOUT_URL = "/auth/logout"
ME_URL = "/auth/me"

VALID_USER = {"email": "test@example.com", "password": "securepassword123"}
VALID_USER_2 = {"email": "other@example.com", "password": "anotherpassword456"}
SHORT_PASSWORD = {"email": "short@example.com", "password": "short"}
INVALID_EMAIL = {"email": "not-an-email", "password": "securepassword123"}


@pytest.mark.asyncio
async def test_register_creates_user(async_client):
    response = await async_client.post(REGISTER_URL, json=VALID_USER)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == VALID_USER["email"]
    assert "id" in data
    assert data["timezone"] == "America/Argentina/Buenos_Aires"
    assert data["risk_tolerance"] == "moderate"
    assert data["email_notifications"] is True


@pytest.mark.asyncio
async def test_register_duplicate_email(async_client):
    await async_client.post(REGISTER_URL, json=VALID_USER)
    response = await async_client.post(REGISTER_URL, json=VALID_USER)

    assert response.status_code == 409
    assert response.json()["detail"] == "Email already registered"


@pytest.mark.asyncio
async def test_register_short_password(async_client):
    response = await async_client.post(REGISTER_URL, json=SHORT_PASSWORD)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_invalid_email(async_client):
    response = await async_client.post(REGISTER_URL, json=INVALID_EMAIL)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success(async_client):
    await async_client.post(REGISTER_URL, json=VALID_USER)

    response = await async_client.post(LOGIN_URL, json=VALID_USER)

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == VALID_USER["email"]
    assert "access_token" in response.cookies


@pytest.mark.asyncio
async def test_login_wrong_password(async_client):
    await async_client.post(REGISTER_URL, json=VALID_USER)

    response = await async_client.post(
        LOGIN_URL,
        json={"email": VALID_USER["email"], "password": "wrongpassword"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


@pytest.mark.asyncio
async def test_login_nonexistent_email(async_client):
    response = await async_client.post(
        LOGIN_URL,
        json={"email": "nobody@example.com", "password": "somepassword"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_authenticated(async_client):
    await async_client.post(REGISTER_URL, json=VALID_USER)
    login_resp = await async_client.post(LOGIN_URL, json=VALID_USER)

    response = await async_client.get(
        ME_URL,
        cookies=dict(login_resp.cookies),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == VALID_USER["email"]


@pytest.mark.asyncio
async def test_me_unauthenticated(async_client):
    response = await async_client.get(ME_URL)

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_expired_token(async_client):
    response = await async_client.get(
        ME_URL,
        cookies={"access_token": "garbage.token.here"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout(async_client):
    await async_client.post(REGISTER_URL, json=VALID_USER)
    login_resp = await async_client.post(LOGIN_URL, json=VALID_USER)

    response = await async_client.post(
        LOGOUT_URL,
        cookies=dict(login_resp.cookies),
    )

    assert response.status_code == 204
    assert response.cookies.get("access_token") == '""' or not response.cookies.get("access_token")


@pytest.mark.asyncio
async def test_me_after_logout(async_client):
    await async_client.post(REGISTER_URL, json=VALID_USER)
    login_resp = await async_client.post(LOGIN_URL, json=VALID_USER)
    await async_client.post(LOGOUT_URL, cookies=dict(login_resp.cookies))

    response = await async_client.get(ME_URL)

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_http_only_cookie(async_client):
    await async_client.post(REGISTER_URL, json=VALID_USER)
    response = await async_client.post(LOGIN_URL, json=VALID_USER)

    set_cookie_header = response.headers.get("set-cookie")
    assert set_cookie_header is not None
    assert "HttpOnly" in set_cookie_header or "httponly" in set_cookie_header
