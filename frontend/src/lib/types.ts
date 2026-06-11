export interface UserOut {
  id: string;
  email: string;
  timezone: string;
  risk_tolerance: string;
  email_notifications: boolean;
}

export interface UserCreate {
  email: string;
  password: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface PortfolioPosition {
  id: string;
  ticker: string;
  shares: string;
  avg_buy_price: string;
  sector: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface PortfolioPositionCreate {
  ticker: string;
  shares: string;
  avg_buy_price: string;
  sector?: string;
  notes?: string;
}

export interface PortfolioPositionUpdate {
  ticker?: string;
  shares?: string;
  avg_buy_price?: string;
  sector?: string;
  notes?: string;
}

export interface Watchlist {
  id: string;
  name: string;
  description: string | null;
  ticker_count: number;
  created_at: string;
}

export interface WatchlistDetail extends Watchlist {
  tickers: WatchlistTicker[];
}

export interface WatchlistTicker {
  ticker: string;
  added_at: string;
}

export interface WatchlistCreate {
  name: string;
  description?: string;
}

export interface WatchlistUpdate {
  name?: string;
  description?: string;
}

// --- Strategy Management (Deliverable 6) ---

export type StrategyStyle = 'value' | 'growth' | 'momentum' | 'dividend' | 'hybrid';

export interface StrategyRules {
  // Fundamental thresholds
  max_pe?: string;
  min_roe?: string;
  min_dividend_yield?: string;
  max_debt_to_equity?: string;
  min_revenue_growth?: string;
  // Technical thresholds
  rsi_entry_max?: string;
  rsi_exit_min?: string;
  ema_crossover?: boolean;
  macd_bullish?: boolean;
  // Position / risk sizing
  max_position_pct?: string;
  stop_loss_pct?: string;
  take_profit_pct?: string;
}

export interface Strategy {
  id: string;
  name: string;
  style: StrategyStyle;
  description: string | null;
  rules: StrategyRules;
  is_active: boolean;
  is_primary: boolean;
  is_training_ready: boolean;
  created_at: string;
  updated_at: string;
}

export interface StrategyCreate {
  name: string;
  style: StrategyStyle;
  rules: StrategyRules;
  description?: string;
  is_active?: boolean;
  is_primary?: boolean;
}

export interface StrategyUpdate {
  name?: string;
  style?: StrategyStyle;
  description?: string;
  rules?: StrategyRules;
}

// --- Price History (Deliverable 8) ---

export interface PricePoint {
  date: string; // ISO 8601 date string YYYY-MM-DD
  open: string;
  high: string;
  low: string;
  close: string;
  volume: number | null;
}

export interface PriceSeriesResponse {
  ticker: string;
  points: PricePoint[];
  from_date: string;
  to_date: string;
  count: number;
  source: string;
  freshness: string;
  fetched_at: string | null;
}

// --- News Feed (Deliverable 7) ---

export interface NewsItemOut {
  headline: string;
  summary: string | null;
  source_name: string;
  url: string | null;
  published_at: string | null;
}

export interface NewsFeedResponse {
  ticker: string;
  available: boolean;
  source: string | null;
  items: NewsItemOut[];
  cached_at: string | null;
  freshness: 'live' | 'stale' | null;
  count: number;
}
