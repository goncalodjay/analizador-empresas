"""Service-layer tests for strategy_service.

Covers: create, list, get, update, delete, set_active, set_primary,
ownership scoping, and single-primary invariant.

Spec refs: R10.1, S2, S4, S5, S6, S7
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.base import Base
from app.models.user import User
from app.schemas.strategies import StrategyCreate, StrategyRules, StrategyStyle, StrategyUpdate
from app.services import strategy_service


TEST_DATABASE_URL = "sqlite+aiosqlite://"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
async def db():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        yield session

    await engine.dispose()


async def _make_user(db: AsyncSession, email: str = "user@example.com") -> User:
    import uuid
    from app.core.security import get_password_hash

    user = User(
        id=uuid.uuid4(),
        email=email,
        password_hash=get_password_hash("password"),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


def _create_payload(
    name: str = "Growth 2025",
    style: StrategyStyle = StrategyStyle.GROWTH,
    rules: dict | None = None,
    is_primary: bool = False,
    is_active: bool = True,
) -> StrategyCreate:
    rules_obj = StrategyRules(**(rules or {}))
    return StrategyCreate(
        name=name,
        style=style,
        rules=rules_obj,
        is_primary=is_primary,
        is_active=is_active,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_strategy_defaults(db):
    user = await _make_user(db)
    payload = _create_payload()

    strategy = await strategy_service.create_strategy(db, payload, str(user.id))

    assert strategy.is_active is True
    assert strategy.is_primary is False
    assert strategy.is_training_ready is False
    assert strategy.name == "Growth 2025"


@pytest.mark.asyncio
async def test_create_strategy_as_primary_clears_other(db):
    """S4: creating with is_primary=True clears any existing primary."""
    user = await _make_user(db)
    existing = await strategy_service.create_strategy(
        db, _create_payload(name="Old", is_primary=True), str(user.id)
    )
    assert existing.is_primary is True

    await strategy_service.create_strategy(
        db, _create_payload(name="New", is_primary=True), str(user.id)
    )

    # Reload the existing strategy and verify it was cleared
    refreshed = await strategy_service.get_strategy(db, str(existing.id), str(user.id))
    assert refreshed is not None
    assert refreshed.is_primary is False


@pytest.mark.asyncio
async def test_get_strategies_own_only(db):
    """S2: list only returns strategies owned by the requesting user."""
    user_a = await _make_user(db, "a@example.com")
    user_b = await _make_user(db, "b@example.com")

    await strategy_service.create_strategy(db, _create_payload(name="A1"), str(user_a.id))
    await strategy_service.create_strategy(db, _create_payload(name="A2"), str(user_a.id))
    await strategy_service.create_strategy(db, _create_payload(name="B1"), str(user_b.id))

    strategies_a = await strategy_service.get_strategies(db, str(user_a.id))
    assert len(strategies_a) == 2
    names = {s.name for s in strategies_a}
    assert names == {"A1", "A2"}


@pytest.mark.asyncio
async def test_get_strategy_foreign_returns_none(db):
    """S6 / R5.1: fetching a strategy owned by another user returns None."""
    user_a = await _make_user(db, "a@example.com")
    user_b = await _make_user(db, "b@example.com")

    strategy = await strategy_service.create_strategy(
        db, _create_payload(), str(user_a.id)
    )

    result = await strategy_service.get_strategy(db, str(strategy.id), str(user_b.id))
    assert result is None


@pytest.mark.asyncio
async def test_update_strategy_preserves_flags(db):
    """update_strategy must not alter is_active or is_primary."""
    user = await _make_user(db)
    strategy = await strategy_service.create_strategy(
        db, _create_payload(is_primary=True, is_active=True), str(user.id)
    )

    update_data = StrategyUpdate(name="Renamed")
    updated = await strategy_service.update_strategy(
        db, str(strategy.id), update_data, str(user.id)
    )

    assert updated is not None
    assert updated.name == "Renamed"
    assert updated.is_primary is True
    assert updated.is_active is True


@pytest.mark.asyncio
async def test_update_strategy_strips_training_ready(db):
    """S7: is_training_ready must remain False after an update."""
    user = await _make_user(db)
    strategy = await strategy_service.create_strategy(
        db, _create_payload(), str(user.id)
    )
    assert strategy.is_training_ready is False

    # StrategyUpdate does not expose is_training_ready, so it cannot be set.
    update_data = StrategyUpdate(name="Updated")
    updated = await strategy_service.update_strategy(
        db, str(strategy.id), update_data, str(user.id)
    )

    assert updated is not None
    assert updated.is_training_ready is False


@pytest.mark.asyncio
async def test_delete_strategy_success(db):
    user = await _make_user(db)
    strategy = await strategy_service.create_strategy(
        db, _create_payload(), str(user.id)
    )

    result = await strategy_service.delete_strategy(db, str(strategy.id), str(user.id))
    assert result is True

    gone = await strategy_service.get_strategy(db, str(strategy.id), str(user.id))
    assert gone is None


@pytest.mark.asyncio
async def test_delete_strategy_foreign_returns_false(db):
    """S6: deleting another user's strategy returns False."""
    user_a = await _make_user(db, "a@example.com")
    user_b = await _make_user(db, "b@example.com")

    strategy = await strategy_service.create_strategy(
        db, _create_payload(), str(user_a.id)
    )

    result = await strategy_service.delete_strategy(db, str(strategy.id), str(user_b.id))
    assert result is False


@pytest.mark.asyncio
async def test_set_active_false_keeps_primary(db):
    """S5: deactivating a primary strategy leaves is_primary unchanged."""
    user = await _make_user(db)
    strategy = await strategy_service.create_strategy(
        db, _create_payload(is_primary=True, is_active=True), str(user.id)
    )

    updated = await strategy_service.set_active(db, str(strategy.id), str(user.id), False)

    assert updated is not None
    assert updated.is_active is False
    assert updated.is_primary is True


@pytest.mark.asyncio
async def test_set_primary_clears_others(db):
    """S4: promoting Y to primary clears X's is_primary."""
    user = await _make_user(db)

    strategy_x = await strategy_service.create_strategy(
        db, _create_payload(name="X", is_primary=True), str(user.id)
    )
    strategy_y = await strategy_service.create_strategy(
        db, _create_payload(name="Y", is_primary=False), str(user.id)
    )

    await strategy_service.set_primary(db, str(strategy_y.id), str(user.id))

    refreshed_x = await strategy_service.get_strategy(db, str(strategy_x.id), str(user.id))
    refreshed_y = await strategy_service.get_strategy(db, str(strategy_y.id), str(user.id))

    assert refreshed_x is not None
    assert refreshed_x.is_primary is False
    assert refreshed_y is not None
    assert refreshed_y.is_primary is True


@pytest.mark.asyncio
async def test_set_primary_clear_leaves_none(db):
    """R3.3: after promoting to primary, the old primary has zero primaries if only one existed."""
    user = await _make_user(db)

    strategy_a = await strategy_service.create_strategy(
        db, _create_payload(name="A", is_primary=True), str(user.id)
    )
    strategy_b = await strategy_service.create_strategy(
        db, _create_payload(name="B"), str(user.id)
    )

    # Promote B — A should lose its primary
    await strategy_service.set_primary(db, str(strategy_b.id), str(user.id))

    all_strategies = await strategy_service.get_strategies(db, str(user.id))
    primaries = [s for s in all_strategies if s.is_primary]
    assert len(primaries) == 1
    assert primaries[0].name == "B"


@pytest.mark.asyncio
async def test_rules_validation_rejects_unknown_key(db):
    """S3-style: StrategyRules with unknown key raises ValidationError."""
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        StrategyRules.model_validate({"unknown_key": 1})


@pytest.mark.asyncio
async def test_get_strategy_ownership_scoping(db):
    """R5.1: service-layer always filters by user_id."""
    user_a = await _make_user(db, "a@example.com")
    user_b = await _make_user(db, "b@example.com")

    strategy = await strategy_service.create_strategy(
        db, _create_payload(), str(user_a.id)
    )

    # User B cannot access user A's strategy
    result_b = await strategy_service.get_strategy(db, str(strategy.id), str(user_b.id))
    assert result_b is None

    # User A can access it
    result_a = await strategy_service.get_strategy(db, str(strategy.id), str(user_a.id))
    assert result_a is not None
    assert result_a.id == strategy.id
