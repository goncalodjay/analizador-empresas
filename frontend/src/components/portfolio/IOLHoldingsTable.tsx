'use client';
import Link from 'next/link';
import type { IOLHolding } from '@/lib/types';

interface IOLHoldingsTableProps {
  holdings: IOLHolding[];
}

const currencyBadgeStyles = {
  ARS: 'bg-primary-100 text-primary-700',
  USD: 'bg-success-100 text-success-700',
};

const currencyLabel = {
  ARS: 'ARS',
  USD: 'USD',
};

export function IOLHoldingsTable({ holdings }: IOLHoldingsTableProps) {
  if (holdings.length === 0) {
    return (
      <div className="rounded-md border border-dashed border-neutral-300 p-8 text-center">
        <p className="text-neutral-500">No holdings synced from IOL yet.</p>
        <p className="mt-2 text-sm text-neutral-400">
          Connect your IOL account to see your portfolio here.
        </p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead className="border-b bg-neutral-50">
          <tr>
            <th className="px-4 py-3 font-semibold text-neutral-700">Ticker</th>
            <th className="px-4 py-3 font-semibold text-neutral-700">Quantity</th>
            <th className="px-4 py-3 font-semibold text-neutral-700">Avg Buy Price</th>
            <th className="px-4 py-3 font-semibold text-neutral-700">Currency</th>
          </tr>
        </thead>
        <tbody>
          {holdings.map((holding) => (
            <tr key={holding.ticker} className="border-b hover:bg-neutral-50 transition-colors">
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
                    currencyBadgeStyles[holding.currency as keyof typeof currencyBadgeStyles] || 'bg-neutral-100 text-neutral-700'
                  }`}
                >
                  {currencyLabel[holding.currency as keyof typeof currencyLabel] || holding.currency}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
