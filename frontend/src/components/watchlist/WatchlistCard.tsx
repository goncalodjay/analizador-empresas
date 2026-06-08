import Link from 'next/link';
import type { Watchlist } from '@/lib/types';

interface WatchlistCardProps {
  watchlist: Watchlist;
}

export function WatchlistCard({ watchlist }: WatchlistCardProps) {
  return (
    <Link
      href={`/watchlists/${watchlist.id}`}
      className="block rounded-lg border border-gray-200 bg-white p-6 transition-shadow hover:shadow-md"
    >
      <h3 className="text-lg font-semibold text-gray-900">{watchlist.name}</h3>
      {watchlist.description && (
        <p className="mt-1 text-sm text-gray-500">{watchlist.description}</p>
      )}
      <div className="mt-4 flex items-center gap-2">
        <span className="rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-medium text-blue-800">
          {watchlist.ticker_count} {watchlist.ticker_count === 1 ? 'ticker' : 'tickers'}
        </span>
      </div>
    </Link>
  );
}
