# Estructura de Archivos Fuente y Relaciones

## Archivos Backend (Python)
Los archivos backend definen modelos de base de datos usando SQLAlchemy:

### `user.py`
Modelo de usuario con campos como `id`, `email`, `timezone`, `risk_tolerance` y `email_notifications`. Relacionado con `AccountStatus` y `generated_signals`.

**Ejemplo de uso:**
```python
user = User(id="1", email="user@example.com", timezone="UTC", risk_tolerance="moderate")
```

### `generated_signal.py`
Modelo de señales de trading con campos como `take_profit_1`, `position_size_pct`, `reasoning` y `confidence`. Relacionado con `User` y `InvestmentStrategy`.

**Ejemplo de uso:**
```python
signal = GeneratedSignal(
    user_id="1",
    strategy_id="1",
    take_profit_1=5.5,
    position_size_pct=2.5,
    reasoning="Bullish momentum detected"
)
```

### `account_status.py`
Modelo de estado de cuenta con balances en moneda (ARS/USD) y sincronización con IOL. Relacionado con `User`.

**Ejemplo de uso:**
```python
status = AccountStatus(
    user_id="1",
    cash_balance=100000.00,
    buying_power=200000.00,
    currency="USD",
    synced_at=datetime.now()
)
```

### `portfolio_holdings.py`
Modelo de posiciones en portafolio con detalles de activos, precios promedio y sincronización. Relacionado con `User`.

**Ejemplo de uso:**
```python
holding = PortfolioHolding(
    user_id="1",
    ticker="AAPL",
    quantity=100,
    avg_buy_price=150.25,
    currency="USD"
)
```

## Archivos Frontend (TypeScript)
Los archivos frontend definen interfaces para representar datos en la UI:

### `types.ts`
Define interfaces para datos de usuarios, portafolios, estrategias y noticias. Coincide con modelos backend:

**Ejemplo de uso:**
```typescript
const user: UserOut = {
  id: "1",
  email: "user@example.com",
  timezone: "UTC",
  risk_tolerance: "moderate",
  email_notifications: true
};
```

**Relaciones clave:**
- `UserOut` ↔ `User` (backend)
- `PortfolioPosition` ↔ `PortfolioHolding` (backend)
- `IOLHolding` ↔ `PortfolioHolding` (backend)
- `Strategy` ↔ `InvestmentStrategy` (backend)

## Relaciones entre Backend y Frontend
- **Datos de usuario:** `User` (backend) → `UserOut` (frontend)
- **Posiciones de portafolio:** `PortfolioHolding` (backend) → `PortfolioPosition` (frontend)
- **Señales de trading:** `GeneratedSignal` (backend) → `Strategy` (frontend)
- **Estado de cuenta:** `AccountStatus` (backend) → `IOLStatus` (frontend)

## Notas
- El archivo `interfaces.ts` (no encontrado) probablemente contendría interfaces adicionales para componentes específicos.
- Todos los modelos y interfaces usan tipos consistentes (ej: `Decimal` ↔ `number`, `datetime` ↔ `string`).