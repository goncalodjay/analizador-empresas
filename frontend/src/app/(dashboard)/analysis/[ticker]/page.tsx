'use client';
import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { apiFetch, getNews, getPriceHistory } from '@/lib/api';
import type { NewsFeedResponse, PriceSeriesResponse } from '@/lib/types';
import { MetricCard } from '@/components/analysis/MetricCard';
import { HealthScoreGauge } from '@/components/analysis/HealthScoreGauge';
import { PeerRankingTable } from '@/components/analysis/PeerRankingTable';
import { TradingViewChart } from '@/components/analysis/TradingViewChart';
import { TechnicalPanel, TechnicalIndicators } from '@/components/analysis/TechnicalPanel';
import { DataFreshnessTag } from '@/components/layout/DataFreshnessTag';
import { NewsFeed } from '@/components/analysis/NewsFeed';
import { PriceHistoryChart } from '@/components/analysis/PriceHistoryChart';

interface AnalysisData {
  ticker: string;
  company_name: string | null;
  sector: string | null;
  price: string | null;
  fundamentals: {
    pe_trailing: any; pe_forward: any; pb_ratio: any; eps: any;
    revenue_growth_yoy: any; debt_to_equity: any; current_ratio: any;
    free_cash_flow: any; market_cap: any; beta: any;
  } | null;
  health_score: {
    composite: number; verdict: string;
    fundamental_quality: number; earnings_momentum: number;
    analyst_sentiment: number; technical_momentum: number;
    top_drivers: string[];
  } | null;
  peers: { ticker: string; peers: any[]; rankings: Record<string, number> } | null;
  technical: TechnicalIndicators | null;
  cached_at: string | null;
}

export default function AnalysisPage() {
  const params = useParams();
  const ticker = (params.ticker as string).toUpperCase();
  const [data, setData] = useState<AnalysisData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [ingesting, setIngesting] = useState(false);

  // News state — independent from the analysis fetch; failures must not break the page
  const [newsData, setNewsData] = useState<NewsFeedResponse | null>(null);
  const [newsLoading, setNewsLoading] = useState(true);
  const [newsError, setNewsError] = useState('');

  // Price history state — independent section; failures must not break the page
  type RangeKey = '1M' | '3M' | '6M' | '1Y';
  const [priceData, setPriceData] = useState<PriceSeriesResponse | null>(null);
  const [priceLoading, setPriceLoading] = useState(true);
  const [priceError, setPriceError] = useState('');
  const [priceRange, setPriceRange] = useState<RangeKey>('1Y');

  const fetchData = async () => {
    setLoading(true);
    setError('');
    try {
      const result = await apiFetch<AnalysisData>(`/analysis/${ticker}`);
      setData(result);
    } catch (err: any) {
      setError(err?.message || 'Failed to load analysis');
    } finally {
      setLoading(false);
    }
  };

  const fetchNews = async () => {
    setNewsLoading(true);
    setNewsError('');
    try {
      const result = await getNews(ticker);
      setNewsData(result);
    } catch (err: any) {
      // News errors are isolated — they do not propagate to the page error boundary
      setNewsError(err?.message || 'Could not load news');
    } finally {
      setNewsLoading(false);
    }
  };

  const fetchPriceHistory = async (range: '1M' | '3M' | '6M' | '1Y') => {
    setPriceLoading(true);
    setPriceError('');
    try {
      const today = new Date();
      const to = today.toISOString().slice(0, 10);
      const fromDate = new Date(today);
      const months = range === '1M' ? 1 : range === '3M' ? 3 : range === '6M' ? 6 : 12;
      fromDate.setMonth(fromDate.getMonth() - months);
      const from = fromDate.toISOString().slice(0, 10);
      const result = await getPriceHistory(ticker, from, to);
      setPriceData(result);
    } catch (err: any) {
      // Price history errors are isolated — empty state shown in component
      if ((err as any)?.status === 404 || (err as any)?.status === 200) {
        setPriceData({ ticker, points: [], from_date: '', to_date: '', count: 0, source: 'yfinance', freshness: 'stale', fetched_at: null });
      } else {
        setPriceError(err?.message || 'Could not load price history');
      }
    } finally {
      setPriceLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    fetchNews();
    fetchPriceHistory('1Y');
  }, [ticker]);

  const runIngestion = async () => {
    setIngesting(true);
    setError('');
    try {
      await apiFetch(`/ingestion/trigger/${ticker}`, { method: 'POST' });
      await Promise.all([fetchData(), fetchNews()]);
    } catch (err: any) {
      setError(err?.message || 'Ingestion failed');
    } finally {
      setIngesting(false);
    }
  };

  if (loading) return <div className="text-neutral-500">Loading analysis for {ticker}...</div>;

  if (error) return (
    <div>
      <p className="mb-4 text-error">{error}</p>
      <button
        onClick={runIngestion}
        disabled={ingesting}
        className="rounded bg-primary-600 px-4 py-2 text-neutral-0 hover:bg-primary-700 disabled:opacity-50 transition-colors"
      >
        {ingesting ? 'Fetching data…' : `Fetch data for ${ticker}`}
      </button>
    </div>
  );

  if (!data) return <div className="text-neutral-500">No data available for {ticker}</div>;

  const f = data.fundamentals;

  return (
    <div>
      {/* TradingView Chart */}
      <div className="mb-6">
        <TradingViewChart ticker={ticker} />
      </div>

      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">
            {data.company_name || ticker} ({ticker})
          </h1>
          {data.sector && <p className="text-neutral-600">{data.sector}</p>}
          {data.price && <p className="mt-1 text-lg font-medium text-neutral-900">${Number(data.price).toFixed(2)}</p>}
        </div>
        <div className="flex items-center gap-3">
          <DataFreshnessTag status="live" timestamp={data.cached_at?.slice(0, 16) || undefined} />
          <button
            onClick={runIngestion}
            disabled={ingesting}
            className="rounded border border-neutral-300 px-3 py-1 text-sm text-neutral-600 hover:bg-neutral-100 disabled:opacity-50 transition-colors"
          >
            {ingesting ? 'Refreshing…' : 'Refresh data'}
          </button>
        </div>
      </div>

      {data.health_score && (
        <div className="mb-6">
          <HealthScoreGauge
            composite={data.health_score.composite}
            verdict={data.health_score.verdict}
            subScores={{
              fundamental_quality: data.health_score.fundamental_quality,
              earnings_momentum: data.health_score.earnings_momentum,
              analyst_sentiment: data.health_score.analyst_sentiment,
              technical_momentum: data.health_score.technical_momentum,
            }}
            topDrivers={data.health_score.top_drivers}
          />
        </div>
      )}

      {f && (
        <>
          <h2 className="mb-3 text-lg font-semibold text-neutral-900">Valuation</h2>
          <div className="mb-6 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
            {f.pe_trailing && <MetricCard {...f.pe_trailing} />}
            {f.pe_forward && <MetricCard {...f.pe_forward} />}
            {f.pb_ratio && <MetricCard {...f.pb_ratio} />}
            {f.eps && <MetricCard {...f.eps} />}
            {f.market_cap && <MetricCard {...f.market_cap} />}
            {f.beta && <MetricCard {...f.beta} />}
          </div>

          <h2 className="mb-3 text-lg font-semibold text-neutral-900">Growth & Financial Health</h2>
          <div className="mb-6 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
            {f.revenue_growth_yoy && <MetricCard {...f.revenue_growth_yoy} />}
            {f.debt_to_equity && <MetricCard {...f.debt_to_equity} />}
            {f.current_ratio && <MetricCard {...f.current_ratio} />}
            {f.free_cash_flow && <MetricCard {...f.free_cash_flow} />}
          </div>
        </>
      )}

      {data.peers && data.peers.peers.length > 0 && (
        <div className="mb-6">
          <PeerRankingTable
            ticker={ticker}
            peers={data.peers.peers}
            rankings={data.peers.rankings}
          />
        </div>
      )}

      {data.technical && (
        <div className="mb-6">
          <TechnicalPanel technical={data.technical} />
        </div>
      )}

      {/* News section — independent fetch; errors are isolated here */}
      <div className="mb-6">
        {newsLoading && (
          <div className="animate-pulse rounded-lg border border-neutral-200 bg-neutral-100 p-4 text-sm text-neutral-400">
            Loading news for {ticker}…
          </div>
        )}
        {!newsLoading && newsError && (
          <div className="rounded-lg border border-error/20 bg-error/10 p-4">
            <p className="text-sm text-error">Could not load news: {newsError}</p>
          </div>
        )}
        {!newsLoading && !newsError && newsData && (
          <NewsFeed
            items={newsData.items}
            available={newsData.available}
            cachedAt={newsData.cached_at}
            freshness={newsData.freshness}
          />
        )}
      </div>

      {/* Price history section — independent fetch; errors are isolated here */}
      <div className="mb-6">
        <div className="mb-2 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-neutral-900">Price History</h2>
          <div className="flex gap-1">
            {(['1M', '3M', '6M', '1Y'] as const).map((range) => (
              <button
                key={range}
                onClick={() => {
                  setPriceRange(range);
                  fetchPriceHistory(range);
                }}
                className={`rounded px-3 py-1 text-sm font-medium transition-colors ${
                  priceRange === range
                    ? 'bg-primary-600 text-neutral-0'
                    : 'bg-neutral-100 text-neutral-600 hover:bg-neutral-200'
                }`}
              >
                {range}
              </button>
            ))}
          </div>
        </div>

        {priceLoading && (
          <div className="animate-pulse rounded-lg border border-neutral-200 bg-neutral-100 p-6 text-sm text-neutral-400">
            Loading price history for {ticker}…
          </div>
        )}
        {!priceLoading && priceError && (
          <div className="rounded-lg border border-error/20 bg-error/10 p-4">
            <p className="text-sm text-error">Could not load price history: {priceError}</p>
          </div>
        )}
        {!priceLoading && !priceError && priceData && (
          <PriceHistoryChart
            ticker={ticker}
            points={priceData.points}
            freshness={priceData.freshness}
            fetchedAt={priceData.fetched_at}
          />
        )}
      </div>
    </div>
  );
}
