'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiFetch, ApiError } from '@/lib/api';
import { WatchlistCard } from '@/components/watchlist/WatchlistCard';
import { WatchlistForm } from '@/components/watchlist/WatchlistForm';
import type { Watchlist } from '@/lib/types';

export default function WatchlistsPage() {
  const router = useRouter();
  const [watchlists, setWatchlists] = useState<Watchlist[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);

  const fetchWatchlists = async () => {
    try {
      const data = await apiFetch<Watchlist[]>('/watchlists');
      setWatchlists(data);
    } catch {
      // silently fail
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWatchlists();
  }, []);

  const handleCreate = async (name: string, description: string) => {
    await apiFetch('/watchlists', {
      method: 'POST',
      body: JSON.stringify({ name, description: description || undefined }),
    });
    setShowForm(false);
    await fetchWatchlists();
  };

  return (
    <div className="p-6">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Watchlists</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
        >
          {showForm ? 'Cancel' : 'Create Watchlist'}
        </button>
      </div>

      {showForm && (
        <div className="mb-6 rounded-lg border bg-gray-50 p-4">
          <WatchlistForm onSave={handleCreate} submitLabel="Create Watchlist" />
        </div>
      )}

      {loading && <p className="text-gray-500">Loading...</p>}
      {!loading && watchlists.length === 0 && (
        <p className="text-gray-500">No watchlists yet.</p>
      )}
      {!loading && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {watchlists.map((wl) => (
            <WatchlistCard key={wl.id} watchlist={wl} />
          ))}
        </div>
      )}
    </div>
  );
}
