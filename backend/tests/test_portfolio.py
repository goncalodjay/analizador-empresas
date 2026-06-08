import pytest

REGISTER_URL = "/auth/register"
LOGIN_URL = "/auth/login"
POSITIONS_URL = "/portfolio/positions"

VALID_USER = {"email": "test@example.com", "password": "securepassword123"}
VALID_USER_2 = {"email": "other@example.com", "password": "anotherpassword456"}

POSITION = {"ticker": "AAPL", "shares": "50", "avg_buy_price": "175.50"}
POSITION_2 = {"ticker": "MSFT", "shares": "20", "avg_buy_price": "420.30"}


async def register_and_login(client, user=VALID_USER):
    await client.post(REGISTER_URL, json=user)
    return await client.post(LOGIN_URL, json=user)


@pytest.mark.asyncio
async def test_list_positions_empty(async_client):
    login_resp = await register_and_login(async_client)
    cookies = dict(login_resp.cookies)

    response = await async_client.get(POSITIONS_URL, cookies=cookies)

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_position(async_client):
    login_resp = await register_and_login(async_client)
    cookies = dict(login_resp.cookies)

    response = await async_client.post(POSITIONS_URL, json=POSITION, cookies=cookies)

    assert response.status_code == 201
    data = response.json()
    assert data["ticker"] == "AAPL"
    assert data["shares"] == "50.0000"
    assert data["avg_buy_price"] == "175.5000"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_create_position_duplicate_ticker(async_client):
    login_resp = await register_and_login(async_client)
    cookies = dict(login_resp.cookies)

    await async_client.post(POSITIONS_URL, json=POSITION, cookies=cookies)
    response = await async_client.post(POSITIONS_URL, json=POSITION, cookies=cookies)

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_list_positions_with_data(async_client):
    login_resp = await register_and_login(async_client)
    cookies = dict(login_resp.cookies)

    await async_client.post(POSITIONS_URL, json=POSITION, cookies=cookies)
    await async_client.post(POSITIONS_URL, json=POSITION_2, cookies=cookies)

    response = await async_client.get(POSITIONS_URL, cookies=cookies)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    tickers = {p["ticker"] for p in data}
    assert tickers == {"AAPL", "MSFT"}


@pytest.mark.asyncio
async def test_get_position(async_client):
    login_resp = await register_and_login(async_client)
    cookies = dict(login_resp.cookies)

    create_resp = await async_client.post(POSITIONS_URL, json=POSITION, cookies=cookies)
    position_id = create_resp.json()["id"]

    response = await async_client.get(f"{POSITIONS_URL}/{position_id}", cookies=cookies)

    assert response.status_code == 200
    assert response.json()["ticker"] == "AAPL"


@pytest.mark.asyncio
async def test_get_position_not_found(async_client):
    login_resp = await register_and_login(async_client)
    cookies = dict(login_resp.cookies)

    response = await async_client.get(
        f"{POSITIONS_URL}/00000000-0000-0000-0000-000000000000", cookies=cookies
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_position(async_client):
    login_resp = await register_and_login(async_client)
    cookies = dict(login_resp.cookies)

    create_resp = await async_client.post(POSITIONS_URL, json=POSITION, cookies=cookies)
    position_id = create_resp.json()["id"]

    response = await async_client.put(
        f"{POSITIONS_URL}/{position_id}",
        json={"shares": "100", "notes": "increased position"},
        cookies=cookies,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["shares"] == "100.0000"
    assert data["notes"] == "increased position"


@pytest.mark.asyncio
async def test_delete_position(async_client):
    login_resp = await register_and_login(async_client)
    cookies = dict(login_resp.cookies)

    create_resp = await async_client.post(POSITIONS_URL, json=POSITION, cookies=cookies)
    position_id = create_resp.json()["id"]

    response = await async_client.delete(
        f"{POSITIONS_URL}/{position_id}", cookies=cookies
    )

    assert response.status_code == 204

    list_resp = await async_client.get(POSITIONS_URL, cookies=cookies)
    assert list_resp.json() == []


@pytest.mark.asyncio
async def test_positions_require_auth(async_client):
    response = await async_client.get(POSITIONS_URL)
    assert response.status_code == 401

    response = await async_client.post(POSITIONS_URL, json=POSITION)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_cross_user_isolation(async_client):
    login_resp_a = await register_and_login(async_client, VALID_USER)
    cookies_a = dict(login_resp_a.cookies)

    create_resp = await async_client.post(
        POSITIONS_URL, json=POSITION, cookies=cookies_a
    )
    position_id = create_resp.json()["id"]

    login_resp_b = await register_and_login(async_client, VALID_USER_2)
    cookies_b = dict(login_resp_b.cookies)

    response = await async_client.get(
        f"{POSITIONS_URL}/{position_id}", cookies=cookies_b
    )
    assert response.status_code == 404

    list_resp = await async_client.get(POSITIONS_URL, cookies=cookies_b)
    assert list_resp.json() == []
