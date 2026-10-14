# Modelo de Datos y Relaciones

## Descripción general
Los archivos definidos implementan un modelo de datos para un sistema de trading y análisis financiero. Los modelos están organizados en entidades relacionadas que manejan usuarios, estrategias de inversión, modelos de machine learning, señales de trading, estados de cuenta y portafolios.

## Entidades principales y relaciones

### 1. `User` (relación central)
- **Modelo**: `models/user.py`
- **Campos clave**: `id`, `email`, `created_at`
- **Relaciones**:
  - `model_versions`: 1:N (un usuario puede tener múltiples versiones de modelos)
  - `daily_digests`: 1:N (digestos diarios por usuario)
  - `generated_signals`: 1:N (señales generadas por usuario)
  - `account_status`: 1:1 (estado de cuenta único por usuario)
  - `portfolio_holdings`: 1:N (posiciones en portafolio)

### 2. `InvestmentStrategy` (estrategias de inversión)
- **Modelo**: `models/investment_strategy.py`
- **Campos clave**: `id`, `name`, `description`
- **Relaciones**:
  - `model_versions`: 1:N (una estrategia puede tener múltiples versiones de modelos)
  - `generated_signals`: 1:N (señales generadas usando esta estrategia)

### 3. `ModelVersion` (versiones de modelos ML)
- **Modelo**: `models/ml.py`
- **Campos clave**: `id`, `base_model`, `version_tag`, `status`
- **Uso**: Rastrea versiones de modelos de machine learning asociados a usuarios y estrategias
- **Ejemplo**:
  ```python
  model_version = ModelVersion(
      user_id=user.id,
      base_model="bert-base",
      version_tag="v1.0",
      status="active"
  )
  ```

### 4. `BacktestResult` (resultados de backtests)
- **Modelo**: `models/backtest_result.py`
- **Campos clave**: `id`, `backtest_id`, `metrics`, `created_at`
- **Relaciones**:
  - `backtest`: N:1 (resultados asociados a un backtest específico)
  - `user`: N:1 (resultados pertenecientes a un usuario)

### 5. `DailyDigest` (digestos diarios)
- **Modelo**: `models/digest.py`
- **Campos clave**: `id`, `digest_date`, `content`, `email_sent`
- **Restricciones**: Único por usuario y fecha (`UniqueConstraint`)
- **Ejemplo**:
  ```python
  digest = DailyDigest(
      user_id=user.id,
      digest_date=datetime.now().date(),
      content={"summary": "Resumen diario de operaciones"},
      email_sent=False
  )
  ```

### 6. `GeneratedSignal` (señales de trading)
- **Modelo**: `models/signal.py`
- **Campos clave**: `id`, `ticker`, `signal_type`, `generated_at`
- **Campos numéricos**: Precios, tamaños de posición, confianza
- **Ejemplo**:
  ```python
  signal = GeneratedSignal(
      user_id=user.id,
      ticker="AAPL",
      signal_type="long",
      entry_price_low=150.0,
      take_profit_1=160.0,
      confidence=0.95
  )
  ```

### 7. `AccountStatus` (estado de cuenta)
- **Modelo**: `models/account_status.py`
- **Campos clave**: `id`, `cash_balance`, `buying_power`, `synced_at`
- **Relación**: 1:1 con `User` (estado único por usuario)

### 8. `PortfolioHolding` (posiciones en portafolio)
- **Modelo**: `models/portfolio_holdings.py`
- **Campos clave**: `id`, `ticker`, `quantity`, `avg_buy_price`
- **Índices**: Único por `user_id` y `ticker`
- **Ejemplo**:
  ```python
  holding = PortfolioHolding(
      user_id=user.id,
      ticker="TSLA",
      quantity=100,
      avg_buy_price=250.0
  )
  ```

## Relaciones clave
- **Usuario central**: El modelo `User` es la entidad raíz que conecta todos los componentes:
  ```
  User
  ├── model_versions
  ├── daily_digests
  ├── generated_signals
  ├── account_status
  └── portfolio_holdings
  ```
- **Estrategias y modelos**: Las estrategias de inversión (`InvestmentStrategy`) pueden tener múltiples versiones de modelos ML y generar señales de trading.
- **Backtests**: Los resultados de backtests (`BacktestResult`) están vinculados a un `Backtest` específico y a un usuario.

## Ejemplo de flujo de datos
1. Un usuario crea una estrategia de inversión
2. Se entrena una versión de modelo ML asociada a la estrategia
3. Se genera una señal de trading usando la estrategia y el modelo
4. Se registra el estado de cuenta y las posiciones en el portafolio
5. Se genera un digesto diario con resumen de operaciones