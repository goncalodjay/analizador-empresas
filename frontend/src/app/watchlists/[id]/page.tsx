'use client';
import { useEffect, useState, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { apiFetch } from '@/lib/api';
import { WatchlistForm } from '@/components/watchlist/WatchlistForm';
import { TickerInput } from '@/components/watchlist/TickerInput';
import type { WatchlistDetail } from '@/lib/types';

export default function WatchlistDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [watchlist, setWatchlist] = useState<WatchlistDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [deletingTicker, setDeletingTicker] = useState<string | null>(null);

  const fetchWatchlist = useCallback(async () => {
    try {
      const data = await apiFetch<WatchlistDetail>(`/watchlists/${params.id}`);
      setWatchlist(data);
    } finally {
      setLoading(false);
    }
  }, [params.id]);

  useEffect(() => {
    fetchWatchlist();
  }, [fetchWatchlist]);

  const handleUpdate = async (name: string, description: string) => {
    await apiFetch(`/watchlists/${params.id}`, {
      method: 'PUT',
      body: JSON.stringify({ name, description: description || undefined }),
    });
    setEditing(false);
    await fetchWatchlist();
  };

  const handleRemoveTicker = async (ticker: string) => {
    if (!confirm(`Remove ${ticker}?`)) return;
    setDeletingTicker(ticker);
    try {
      await apiFetch(`/watchlists/${params.id}/tickers/${ticker}`, { method: 'DELETE' });
      await fetchWatchlist();
    } catch {
      alert('Failed to remove ticker');
    } finally {
      setDeletingTicker(null);
    }
  };

  const handleDeleteWatchlist = async () => {
    if (!confirm('Delete this watchlist?')) return;
    await apiFetch(`/watchlists/${params.id}`, { method: 'DELETE' });
    router.push('/watchlists');
  };

  if (loading) return <div className="p-6 text-gray-500">Loading...</div>;
  if (!watchlist) return <div className="p-6 text-gray-500">Watchlist not found</div>;

  return (
    <div className="p-6">
      <div className="mb-6 flex items-start justify-between">
        <div>
          {editing ? (
            <WatchlistForm
              initialName={watchlist.name}
              initialDescription={watchlist.description || ''}
              onSave={handleUpdate}
              submitLabel="Save"
            />
          ) : (
            <>
              <h1 className="text-2xl font-bold text-gray-900">{watchlist.name}</h1>
              {watchlist.description && (
                <p className="mt-1 text-gray-500">{watchlist.description}</p>
              )}
              <div className="mt-3 flex gap-2">
                <button
                  onClick={() => setEditing(true)}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  Edit
                </button>
                <button
                  onClick={handleDeleteWatchlist}
                  className="text-sm text-red-600 hover:text-red-800"
                >
                  Delete
                </button>
              </div>
            </>
          )}
        </div>
      </div>

      {!editing && (
        <>
          <div className="mb-4">
            <TickerInput watchlistId={watchlist.id} onTickerAdded={fetchWatchlist} />
          </div>

          <div className="rounded-lg border">
            {watchlist.tickers.length === 0 ? (
              <p className="p-4 text-sm text-gray-500">No tickers in this watchlist.</p>
            ) : (
              <ul className="divide-y">
                {watchlist.tickers.map((t) => (
                  <li key={t.ticker} className="flex items-center justify-between px-4 py-3">
                    <span className="font-medium">{t.ticker}</span>
                    <button
                      onClick={() => handleRemoveTicker(t.ticker)}
                      disabled={deletingTicker === t.ticker}
                      className="text-sm text-red-600 hover:text-red-800 disabled:opacity-50"
                    >
                      {deletingTicker === t.ticker ? 'Removing...' : 'Remove'}
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </>
      )}
    </div>
  );
}
