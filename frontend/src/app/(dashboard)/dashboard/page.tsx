'use client';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useAuth } from '@/lib/auth-context';
import { apiFetch } from '@/lib/api';
import type { IOLHoldingsResponse, IOLHolding } from '@/lib/types';
import { PriceSourceBadge } from '@/components/common/PriceSourceBadge';

interface HoldingWithPrice extends IOLHolding {
  current_price?: number;
  price_source?: string;
  current_value?: number;
  unrealized_pnl?: number;
}

export default function DashboardPage() {
  const { user } = useAuth();
  const [holdings, setHoldings] = useState<HoldingWithPrice[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchHoldings = async () => {
      if (!user) return;

      try {
        const data = await apiFetch<IOLHoldingsResponse>('/iol/holdings');
        if (data.holdings && data.holdings.length > 0) {
          // For now, just show the holdings without current prices
          // In a future update, we could fetch current prices per holding
          setHoldings(data.holdings);
        }
        setError('');
      } catch (err: any) {
        setError(err?.message || 'Failed to load holdings');
      } finally {
        setLoading(false);
      }
    };

    fetchHoldings();
  }, [user]);

  if (!user) {
    return <div className="text-neutral-500">Please log in to see your dashboard.</div>;
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-neutral-900">Dashboard</h1>
        <p className="mt-1 text-neutral-600">Welcome, {user.email}</p>
      </div>

      {/* Holdings Section */}
      <div className="mt-8">
        <h2 className="mb-4 text-lg font-semibold text-neutral-900">Portfolio Holdings</h2>

        {error && (
          <div className="mb-4 rounded-md border border-error/20 bg-error/10 p-4">
            <p className="text-sm text-error">{error}</p>
          </div>
        )}

        {loading && (
          <div className="rounded-md border border-neutral-200 p-4 text-center text-neutral-500">
            Loading your holdings...
          </div>
        )}

        {!loading && holdings.length === 0 && !error && (
          <div className="rounded-md border border-dashed border-neutral-300 p-8 text-center">
            <p className="text-neutral-500">No holdings synced from IOL yet.</p>
            <p className="mt-2 text-sm text-neutral-400">
              Connect your IOL account in Settings to sync your portfolio.
            </p>
          </div>
        )}

        {!loading && holdings.length > 0 && (
          <div className="overflow-x-auto rounded-md border border-neutral-200">
            <table className="w-full text-left text-sm">
              <thead className="border-b bg-neutral-50">
                <tr>
                  <th className="px-4 py-3 font-semibold text-neutral-700">Ticker</th>
                  <th className="px-4 py-3 font-semibold text-neutral-700">Quantity</th>
                  <th className="px-4 py-3 font-semibold text-neutral-700">Avg Buy Price</th>
                  <th className="px-4 py-3 font-semibold text-neutral-700">Currency</th>
                  <th className="px-4 py-3 font-semibold text-neutral-700">Price Source</th>
                </tr>
              </thead>
              <tbody>
                {holdings.map((holding) => {
                  // Determine price source badge based on currency
                  const priceSource = holding.currency === 'ARS' ? 'iol-bcba' : 'yfinance';

                  return (
                    <tr
                      key={holding.ticker}
                      className="border-b hover:bg-neutral-50 transition-colors"
                    >
                      <td className="px-4 py-3 font-medium">
                        <Link
                          href={`/analysis/${holding.ticker}`}
                          className="text-primary-600 hover:text-primary-700 hover:underline"
                        >
                          {holding.ticker}
                        </Link>
                      </td>
                      <td className="px-4 py-3">
                        {Number(holding.quantity).toLocaleString(undefined, {
                          minimumFractionDigits: 0,
                          maximumFractionDigits: 2,
                        })}
                      </td>
                      <td className="px-4 py-3">
                        {Number(holding.avg_buy_price).toLocaleString(undefined, {
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2,
                        })}
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className={`inline-block rounded-sm px-2 py-1 text-xs font-medium ${
                            holding.currency === 'ARS'
                              ? 'bg-primary-100 text-primary-700'
                              : 'bg-success/20 text-success'
                          }`}
                        >
                          {holding.currency}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <PriceSourceBadge source={priceSource} />
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
