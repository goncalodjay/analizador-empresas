import uuid
from decimal import Decimal

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.strategy import InvestmentStrategy
from app.schemas.strategies import StrategyCreate, StrategyUpdate


def _rules_to_json(rules_model) -> dict:
    """Serialize a StrategyRules model to a JSON-safe dict (Decimal -> float)."""
    raw = rules_model.model_dump(exclude_none=True)
    return {
        k: float(v) if isinstance(v, Decimal) else v
        for k, v in raw.items()
    }


class StrategyNotFoundError(Exception):
    """Raised when a strategy is not found or does not belong to the requesting user."""


async def get_strategies(
    db: AsyncSession, user_id: str
) -> list[InvestmentStrategy]:
    """Return all strategies for ``user_id``, primary first then newest first."""
    result = await db.execute(
        select(InvestmentStrategy)
        .where(InvestmentStrategy.user_id == uuid.UUID(user_id))
        .order_by(
            InvestmentStrategy.is_primary.desc(),
            InvestmentStrategy.created_at.desc(),
        )
    )
    return list(result.scalars().all())


async def get_strategy(
    db: AsyncSession, strategy_id: str, user_id: str
) -> InvestmentStrategy | None:
    """Return the strategy owned by ``user_id`` or ``None``."""
    result = await db.execute(
        select(InvestmentStrategy).where(
            InvestmentStrategy.id == uuid.UUID(strategy_id),
            InvestmentStrategy.user_id == uuid.UUID(user_id),
        )
    )
    return result.scalar_one_or_none()


async def create_strategy(
    db: AsyncSession, data: StrategyCreate, user_id: str
) -> InvestmentStrategy:
    """Create a new strategy.

    If ``data.is_primary`` is ``True``, all other primaries for the user are
    cleared atomically in the same transaction.
    """
    if data.is_primary:
        await db.execute(
            update(InvestmentStrategy)
            .where(
                InvestmentStrategy.user_id == uuid.UUID(user_id),
                InvestmentStrategy.is_primary.is_(True),
            )
            .values(is_primary=False)
        )

    strategy = InvestmentStrategy(
        user_id=uuid.UUID(user_id),
        name=data.name,
        style=data.style.value,
        description=data.description,
        rules=_rules_to_json(data.rules),
        is_active=data.is_active,
        is_primary=data.is_primary,
    )
    db.add(strategy)
    await db.commit()
    await db.refresh(strategy)
    return strategy


async def update_strategy(
    db: AsyncSession, strategy_id: str, data: StrategyUpdate, user_id: str
) -> InvestmentStrategy | None:
    """Partial update — only fields present in ``data`` are applied.

    ``is_active``, ``is_primary``, and ``is_training_ready`` are never touched.
    """
    strategy = await get_strategy(db, strategy_id, user_id)
    if strategy is None:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "style" and value is not None:
            # Store the string value of the enum
            setattr(strategy, field, value.value if hasattr(value, "value") else value)
        elif field == "rules" and value is not None:
            # Serialize StrategyRules to JSON-safe dict (Decimal -> float)
            setattr(strategy, field, _rules_to_json(value))
        else:
            setattr(strategy, field, value)

    await db.commit()
    await db.refresh(strategy)
    return strategy


async def delete_strategy(
    db: AsyncSession, strategy_id: str, user_id: str
) -> bool:
    """Delete the strategy.  Returns ``False`` if not found / not owned."""
    strategy = await get_strategy(db, strategy_id, user_id)
    if strategy is None:
        return False

    await db.delete(strategy)
    await db.commit()
    return True


async def set_active(
    db: AsyncSession, strategy_id: str, user_id: str, is_active: bool
) -> InvestmentStrategy | None:
    """Toggle ``is_active``.  ``is_primary`` is intentionally unchanged."""
    strategy = await get_strategy(db, strategy_id, user_id)
    if strategy is None:
        return None

    strategy.is_active = is_active
    await db.commit()
    await db.refresh(strategy)
    return strategy


async def set_primary(
    db: AsyncSession, strategy_id: str, user_id: str
) -> InvestmentStrategy | None:
    """Promote ``strategy_id`` to primary.

    Atomic: clears all existing primaries for the user in a single bulk UPDATE,
    then sets the target.  Both writes share a single ``await db.commit()``.
    """
    strategy = await get_strategy(db, strategy_id, user_id)
    if strategy is None:
        return None

    # 1. Clear any existing primary for this user in one statement.
    await db.execute(
        update(InvestmentStrategy)
        .where(
            InvestmentStrategy.user_id == uuid.UUID(user_id),
            InvestmentStrategy.is_primary.is_(True),
        )
        .values(is_primary=False)
    )

    # 2. Set the target as primary.
    strategy.is_primary = True

    # 3. Commit once — both writes succeed or both roll back.
    await db.commit()
    await db.refresh(strategy)
    return strategy
