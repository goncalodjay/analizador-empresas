'use client';
import { useState } from 'react';
import { apiFetch, ApiError } from '@/lib/api';

interface TickerInputProps {
  watchlistId: string;
  onTickerAdded: () => void;
}

export function TickerInput({ watchlistId, onTickerAdded }: TickerInputProps) {
  const [ticker, setTicker] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ticker.trim()) return;
    setError('');
    setLoading(true);
    try {
      await apiFetch(`/watchlists/${watchlistId}/tickers`, {
        method: 'POST',
        body: JSON.stringify({ ticker: ticker.trim().toUpperCase() }),
      });
      setTicker('');
      onTickerAdded();
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('Failed to add ticker');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleAdd} className="flex gap-2">
      <input
        type="text"
        value={ticker}
        onChange={(e) => setTicker(e.target.value)}
        maxLength={10}
        placeholder="Add ticker..."
        className="flex-1 rounded-md border border-gray-300 px-3 py-1.5 text-sm"
      />
      <button
        type="submit"
        disabled={loading || !ticker.trim()}
        className="rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
      >
        Add
      </button>
      {error && <span className="text-xs text-red-600 self-center">{error}</span>}
    </form>
  );
}
