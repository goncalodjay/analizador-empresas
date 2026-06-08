import pytest

REGISTER_URL = "/auth/register"
LOGIN_URL = "/auth/login"
WATCHLISTS_URL = "/watchlists"

VALID_USER = {"email": "test@example.com", "password": "securepassword123"}
VALID_USER_2 = {"email": "other@example.com", "password": "anotherpassword456"}

WATCHLIST = {"name": "Tech Giants", "description": "Mega-cap tech companies"}


async def register_and_login(client, user=VALID_USER):
    await client.post(REGISTER_URL, json=user)
    return await client.post(LOGIN_URL, json=user)


@pytest.mark.asyncio
async def test_list_watchlists_empty(async_client):
    login_resp = await register_and_login(async_client)
    cookies = dict(login_resp.cookies)

    response = await async_client.get(WATCHLISTS_URL, cookies=cookies)

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_watchlist(async_client):
    login_resp = await register_and_login(async_client)
    cookies = dict(login_resp.cookies)

    response = await async_client.post(WATCHLISTS_URL, json=WATCHLIST, cookies=cookies)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Tech Giants"
    assert data["description"] == "Mega-cap tech companies"
    assert data["ticker_count"] == 0
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_get_watchlist_with_tickers(async_client):
    login_resp = await register_and_login(async_client)
    cookies = dict(login_resp.cookies)

    create_resp = await async_client.post(
        WATCHLISTS_URL, json=WATCHLIST, cookies=cookies
    )
    watchlist_id = create_resp.json()["id"]

    await async_client.post(
        f"{WATCHLISTS_URL}/{watchlist_id}/tickers",
        json={"ticker": "AAPL"},
        cookies=cookies,
    )
    await async_client.post(
        f"{WATCHLISTS_URL}/{watchlist_id}/tickers",
        json={"ticker": "MSFT"},
        cookies=cookies,
    )

    response = await async_client.get(
        f"{WATCHLISTS_URL}/{watchlist_id}", cookies=cookies
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Tech Giants"
    assert data["ticker_count"] == 2
    assert len(data["tickers"]) == 2
    tickers = {t["ticker"] for t in data["tickers"]}
    assert tickers == {"AAPL", "MSFT"}


@pytest.mark.asyncio
async def test_get_watchlist_not_found(async_client):
    login_resp = await register_and_login(async_client)
    cookies = dict(login_resp.cookies)

    response = await async_client.get(
        f"{WATCHLISTS_URL}/00000000-0000-0000-0000-000000000000", cookies=cookies
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_watchlist(async_client):
    login_resp = await register_and_login(async_client)
    cookies = dict(login_resp.cookies)

    create_resp = await async_client.post(
        WATCHLISTS_URL, json=WATCHLIST, cookies=cookies
    )
    watchlist_id = create_resp.json()["id"]

    response = await async_client.put(
        f"{WATCHLISTS_URL}/{watchlist_id}",
        json={"name": "Dividend Kings"},
        cookies=cookies,
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Dividend Kings"


@pytest.mark.asyncio
async def test_delete_watchlist(async_client):
    login_resp = await register_and_login(async_client)
    cookies = dict(login_resp.cookies)

    create_resp = await async_client.post(
        WATCHLISTS_URL, json=WATCHLIST, cookies=cookies
    )
    watchlist_id = create_resp.json()["id"]

    response = await async_client.delete(
        f"{WATCHLISTS_URL}/{watchlist_id}", cookies=cookies
    )

    assert response.status_code == 204

    list_resp = await async_client.get(WATCHLISTS_URL, cookies=cookies)
    assert list_resp.json() == []


@pytest.mark.asyncio
async def test_add_ticker_to_watchlist(async_client):
    login_resp = await register_and_login(async_client)
    cookies = dict(login_resp.cookies)

    create_resp = await async_client.post(
        WATCHLISTS_URL, json=WATCHLIST, cookies=cookies
    )
    watchlist_id = create_resp.json()["id"]

    response = await async_client.post(
        f"{WATCHLISTS_URL}/{watchlist_id}/tickers",
        json={"ticker": "AAPL"},
        cookies=cookies,
    )

    assert response.status_code == 200
    assert response.json()["ticker_count"] == 1


@pytest.mark.asyncio
async def test_add_duplicate_ticker_ignored(async_client):
    login_resp = await register_and_login(async_client)
    cookies = dict(login_resp.cookies)

    create_resp = await async_client.post(
        WATCHLISTS_URL, json=WATCHLIST, cookies=cookies
    )
    watchlist_id = create_resp.json()["id"]

    await async_client.post(
        f"{WATCHLISTS_URL}/{watchlist_id}/tickers",
        json={"ticker": "AAPL"},
        cookies=cookies,
    )
    response = await async_client.post(
        f"{WATCHLISTS_URL}/{watchlist_id}/tickers",
        json={"ticker": "AAPL"},
        cookies=cookies,
    )

    assert response.status_code == 200
    assert response.json()["ticker_count"] == 1


@pytest.mark.asyncio
async def test_remove_ticker(async_client):
    login_resp = await register_and_login(async_client)
    cookies = dict(login_resp.cookies)

    create_resp = await async_client.post(
        WATCHLISTS_URL, json=WATCHLIST, cookies=cookies
    )
    watchlist_id = create_resp.json()["id"]

    await async_client.post(
        f"{WATCHLISTS_URL}/{watchlist_id}/tickers",
        json={"ticker": "AAPL"},
        cookies=cookies,
    )

    response = await async_client.delete(
        f"{WATCHLISTS_URL}/{watchlist_id}/tickers/AAPL", cookies=cookies
    )

    assert response.status_code == 204

    detail_resp = await async_client.get(
        f"{WATCHLISTS_URL}/{watchlist_id}", cookies=cookies
    )
    assert detail_resp.json()["ticker_count"] == 0


@pytest.mark.asyncio
async def test_watchlists_require_auth(async_client):
    response = await async_client.get(WATCHLISTS_URL)
    assert response.status_code == 401

    response = await async_client.post(WATCHLISTS_URL, json=WATCHLIST)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_cross_user_isolation_watchlist(async_client):
    login_resp_a = await register_and_login(async_client, VALID_USER)
    cookies_a = dict(login_resp_a.cookies)

    create_resp = await async_client.post(
        WATCHLISTS_URL, json=WATCHLIST, cookies=cookies_a
    )
    watchlist_id = create_resp.json()["id"]

    login_resp_b = await register_and_login(async_client, VALID_USER_2)
    cookies_b = dict(login_resp_b.cookies)

    response = await async_client.get(
        f"{WATCHLISTS_URL}/{watchlist_id}", cookies=cookies_b
    )
    assert response.status_code == 404

    list_resp = await async_client.get(WATCHLISTS_URL, cookies=cookies_b)
    assert list_resp.json() == []
