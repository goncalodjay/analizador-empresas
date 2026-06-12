# Spec: Base Strategy Templates

**Capability**: strategy-templates  
**Status**: Pending Implementation  
**Scope**: Pre-seeded validated base strategy templates (3–5 templates), template structure (description, how it works, recommended timeframe), read-only display in MVP  
**Out of Scope**: Custom strategy creation, strategy backtesting or simulation, performance tracking, strategy comparison tools, ML-based recommendations  

---

## Delta Requirements

### DeltaR1: Base Strategy Templates Definition
**Requirement**: The app MUST include 3–5 pre-seeded, validated base investment strategy templates. Each template is a structured document with: (1) strategy name, (2) description, (3) how it works (plain English rules), (4) recommended timeframe, (5) best suited for (investor profile).

**Rationale**: Proposal Q5 decision: strategies in MVP are template-based, read-only. Templates serve as educational reference and example investment approaches. Custom creation and backtesting are deferred to Phase 2.

**Acceptance Criteria**:
- Backend includes a `strategy_templates` table or static seed data with the following schema:
  ```
  id: integer (primary key)
  name: string (strategy name, e.g., "Value Investing")
  description: text (1–2 paragraph summary of the strategy)
  how_it_works: text (step-by-step rules in plain English)
  recommended_timeframe: string (e.g., "6–12 months", "1–3 years")
  best_suited_for: string (e.g., "Long-term investors seeking undervalued stocks")
  risk_level: enum ["low", "medium", "high"]
  created_at: timestamp
  ```
- At minimum, 3 base templates are seeded:
  1. **Value Investing**
  2. **Growth Investing**
  3. **Dividend/Income Investing**
- Optional additional templates (Proposal suggests 3–5):
  4. **Dollar-Cost Averaging (DCA)**
  5. **Quality Growth** or similar
- Each template is immutable (read-only); users cannot edit or delete templates

### DeltaR2: Strategy Template Display
**Requirement**: The frontend MUST display all base strategy templates in a "Strategies" page or section. Each template is shown as a card or expandable section with the template details. Users can view templates but cannot create custom strategies in MVP.

**Rationale**: Templates serve as educational reference for users exploring investment approaches.

**Acceptance Criteria**:
- Strategies page (/strategies or /dashboard/strategies) lists all base templates
- Each template is displayed as a card with:
  - **Title**: Strategy name (e.g., "Value Investing")
  - **Description**: 1–2 paragraph summary (visible on card or click-to-expand)
  - **How It Works**: Collapsible section with step-by-step rules
  - **Recommended Timeframe**: e.g., "6–12 months"
  - **Best Suited For**: e.g., "Long-term investors seeking undervalued stocks"
  - **Risk Level**: Badge or label (Low, Medium, High)
- Cards are arranged in a grid (desktop) or list (mobile)
- Clicking a card expands/collapses the "How It Works" section
- No "Create Custom Strategy" button is visible (deferred to Phase 2)
- No backtesting or comparison tools are visible (deferred to Phase 2)

### DeltaR3: Template Seed Data
**Requirement**: At application startup, the backend MUST seed the strategy templates table with 3–5 predefined templates. If templates already exist (idempotent), the seed operation skips them.

**Rationale**: Ensures templates are available immediately after deployment without manual data entry.

**Acceptance Criteria**:
- Backend includes a seed script or database migration that inserts base templates
- Templates are seeded on app startup (or via a manual command: `python manage.py seed_strategies`)
- If templates already exist (checked by name), seed is skipped (idempotent)
- Seed operation logs success: "Seeded 3 base strategy templates"
- Seed operation can be re-run without duplicating templates

### DeltaR4: Strategy List Endpoint
**Requirement**: The backend MUST provide a GET /strategies endpoint that returns all base strategy templates. Endpoint is public (no authentication required) or requires JWT for future filtering (deferred).

**Rationale**: Frontend fetches templates on page load; public endpoint reduces complexity for MVP.

**Acceptance Criteria**:
- GET /strategies (public or JWT-required, TBD by design phase)
- Returns:
  ```json
  {
    "strategies": [
      {
        "id": 1,
        "name": "Value Investing",
        "description": "A strategy focused on finding undervalued stocks...",
        "how_it_works": "1. Screen for low P/E ratios...\n2. Analyze fundamentals...",
        "recommended_timeframe": "6–12 months",
        "best_suited_for": "Long-term investors seeking undervalued stocks",
        "risk_level": "medium"
      },
      ...
    ]
  }
  ```
- Response is cached for 24 hours (Redis) since templates are static
- Endpoint completes within 100ms

### DeltaR5: Template Content (Detailed)
**Requirement**: Each base template MUST include detailed, plain-English content that is pedagogical and actionable. Content MUST NOT include backtesting results, performance claims, or financial advice.

**Rationale**: Templates are educational references; they inform the user without promising returns.

**Acceptance Criteria**:
- Each template's "How It Works" section includes 3–5 numbered steps
- Steps are written in plain English (no jargon, or jargon is defined)
- Steps are actionable (user can understand what to do if they follow the strategy)
- Content does NOT include backtesting results or performance claims (e.g., no "historically returned X% per year")
- Content does NOT include financial advice (e.g., no "you should buy low-P/E stocks")
- Content is reviewed for accuracy by domain experts (deferred to design/review phase)

### DeltaR6: Risk Level Classification
**Requirement**: Each template MUST be classified as low, medium, or high risk. Risk level is displayed in the UI and helps users self-select strategies aligned with their risk tolerance.

**Rationale**: Users can quickly understand strategy risk and filter/browse accordingly.

**Acceptance Criteria**:
- Each template has a `risk_level` enum field: "low", "medium", "high"
- Risk level is displayed as a badge on the template card (e.g., "Medium Risk")
- Badge color: low = green, medium = yellow, high = red
- Risk classification is based on volatility, diversification, and typical holding periods of the strategy

---

## Base Template Specifications

### Template 1: Value Investing

**Name**: Value Investing  
**Risk Level**: Medium  
**Recommended Timeframe**: 6–12 months to 2+ years  
**Best Suited For**: Patient investors seeking undervalued stocks with strong fundamentals  

**Description**:  
Value Investing is a strategy that focuses on finding stocks trading below their intrinsic (true) value. By analyzing a company's fundamentals—earnings, book value, cash flow—investors aim to identify overlooked opportunities with margin of safety. This approach requires discipline to buy when prices fall and to hold through market volatility.

**How It Works**:
1. Screen for stocks with low valuation multiples (P/E ratio, Price/Book ratio)
2. Analyze the company's financial statements: earnings, revenue growth, debt levels
3. Estimate the company's intrinsic value using fundamental metrics
4. Buy when the stock price is trading below estimated intrinsic value (margin of safety)
5. Hold for 6+ months to 2+ years; sell when price reaches fair value or fundamentals deteriorate

---

### Template 2: Growth Investing

**Name**: Growth Investing  
**Risk Level**: High  
**Recommended Timeframe**: 2–5+ years  
**Best Suited For**: Investors willing to accept volatility for potential capital appreciation  

**Description**:  
Growth Investing targets companies with strong potential for earnings growth. These companies may trade at premium valuations because the market expects rapid expansion. Growth stocks are typically more volatile than the broader market, but investors accept this volatility in exchange for potential capital gains over a longer time horizon.

**How It Works**:
1. Identify companies with strong historical earnings growth (>15% annually)
2. Analyze the company's competitive advantages, market opportunity, and management quality
3. Look for companies in expanding industries or niches (tech, healthcare, etc.)
4. Buy stocks of companies with momentum and strong future prospects, even if valuations seem high
5. Hold for 2–5+ years; expect significant price volatility along the way
6. Sell when growth slows, competitive advantage weakens, or valuation becomes unsustainable

---

### Template 3: Dividend/Income Investing

**Name**: Dividend/Income Investing  
**Risk Level**: Low  
**Recommended Timeframe**: 2–5+ years (long-term income stream)  
**Best Suited For**: Income-seeking investors (retirees, conservative investors)  

**Description**:  
Dividend Investing focuses on buying stocks of mature, profitable companies that distribute a portion of earnings to shareholders as dividends. This strategy provides a steady income stream while you own the stock, making it attractive for investors prioritizing cash flow over capital gains. Dividend-paying stocks tend to be less volatile than growth stocks.

**How It Works**:
1. Screen for companies with a history of stable, consistent dividend payments (5+ years)
2. Check dividend yield (annual dividend / stock price) and ensure it's sustainable (not unsustainably high)
3. Analyze the company's profitability and cash flow to ensure dividend is safe
4. Build a portfolio of dividend-paying stocks across different sectors
5. Hold for the long term (2–5+ years) to collect dividends; reinvest dividends to compound returns
6. Monitor payout ratios; avoid companies that cut or eliminate dividends frequently

---

### Template 4: Dollar-Cost Averaging (DCA)

**Name**: Dollar-Cost Averaging  
**Risk Level**: Low–Medium  
**Recommended Timeframe**: 1+ years (ongoing, monthly or quarterly)  
**Best Suited For**: Investors with a fixed income who want to reduce timing risk  

**Description**:  
Dollar-Cost Averaging is a disciplined investing method where you invest a fixed amount of money at regular intervals (monthly, quarterly) regardless of the stock price or market conditions. This approach reduces the impact of market volatility and removes the need to time market entries perfectly. By investing consistently over time, you buy more shares when prices are low and fewer shares when prices are high.

**How It Works**:
1. Decide on a fixed investment amount (e.g., ARS 10,000 per month)
2. Choose stocks or a diversified set of holdings to invest in
3. Invest the fixed amount at regular intervals (monthly, quarterly) regardless of price or market conditions
4. Continue the pattern for 1+ years (or longer) to smooth out price volatility
5. Monitor your average cost per share over time; do NOT panic sell if prices fall (prices may recover)
6. Rebalance or adjust your regular investment amount annually based on your financial situation

---

## Database Schema

```sql
CREATE TABLE IF NOT EXISTS strategy_templates (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE,
  description TEXT NOT NULL,
  how_it_works TEXT NOT NULL,
  recommended_timeframe VARCHAR(100) NOT NULL,
  best_suited_for VARCHAR(200) NOT NULL,
  risk_level VARCHAR(20) NOT NULL CHECK (risk_level IN ('low', 'medium', 'high')),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Seed data (SQL)
INSERT INTO strategy_templates (name, description, how_it_works, recommended_timeframe, best_suited_for, risk_level)
VALUES
  ('Value Investing', '...', '1. Screen for...\n2. Analyze...', '6-12 months to 2+ years', 'Patient investors seeking undervalued stocks', 'medium'),
  ('Growth Investing', '...', '1. Identify companies...\n2. Analyze...', '2-5+ years', 'Investors willing to accept volatility', 'high'),
  ('Dividend/Income Investing', '...', '1. Screen for...\n2. Check...', '2-5+ years', 'Income-seeking investors', 'low'),
  ('Dollar-Cost Averaging', '...', '1. Decide on...\n2. Choose...', '1+ years', 'Investors with fixed income', 'low');
```

---

## Acceptance Scenarios

### Scenario 1: User Visits Strategies Page

**Given** a user navigates to /strategies  
**When** the page loads  
**Then** 4 base strategy template cards are displayed:
- Value Investing (Medium Risk)
- Growth Investing (High Risk)
- Dividend/Income Investing (Low Risk)
- Dollar-Cost Averaging (Low–Medium Risk)  

---

### Scenario 2: User Reads Strategy Details

**Given** the user is on the strategies page  
**When** they click the "Value Investing" card  
**Then** the card expands to show:
- Full description
- "How It Works" with 5 numbered steps
- Recommended timeframe: "6–12 months to 2+ years"
- Best suited for: "Patient investors seeking undervalued stocks with strong fundamentals"
- Risk level badge: "Medium Risk" (yellow)  

---

### Scenario 3: Strategies are Read-Only

**Given** the user is on the strategies page  
**When** they look for a "Create Custom Strategy" button  
**Then** no such button is visible  
**And** no strategy cards have "Edit" or "Delete" buttons  
**And** templates cannot be modified (read-only)  

---

### Scenario 4: Strategies Cached on Backend

**Given** the app is running  
**When** the frontend calls GET /strategies for the first time  
**Then** the backend returns 4 templates (200 OK) and caches the response for 24 hours  
**When** the frontend calls GET /strategies again (within 24 hours)  
**Then** the backend returns the cached response (no database query)  

---

### Scenario 5: User Filters Strategies by Risk Level (Deferred)

**Given** the strategies page is displayed  
**When** the user clicks a "Filter by Risk" dropdown (deferred to Phase 2)  
**Then** only strategies with the selected risk level are shown  
**And** the filter is not implemented in MVP (shown in design but non-functional)  

---

## Implementation Notes

- **Seed Data**: Include SQL migration or Python seed script; store in `migrations/` directory for reproducibility
- **Endpoint**: GET /strategies is public (no JWT required for MVP); add authentication if future phases require user-specific filtering
- **Caching**: Cache entire template list for 24 hours in Redis; invalidate on deploy if templates change
- **Content Length**: Each template's "How It Works" section is 150–300 words; description is 50–150 words
- **Frontend Display**: Use collapsible sections (accordion) or card expand/collapse for clean UX
- **Translations**: Content is in English (MVP); translations deferred to Phase 2

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Templates contain inaccurate or misleading content | Content reviewed by domain experts; avoid performance claims or financial advice |
| Users expect backtesting or live performance data | Clearly mark MVP as templates only; set expectations in UI ("Educational templates, not investment advice") |
| Users attempt to create custom strategies (not yet available) | Hide custom creation UI; display message: "Custom strategies coming in Phase 2" |
| Seed data not applied on deployment | Automate seed via migration; log seed execution; verify templates exist post-deploy |
