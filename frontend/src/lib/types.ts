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
