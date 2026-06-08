'use client';
import { useState } from 'react';
import { apiFetch, ApiError } from '@/lib/api';

interface WatchlistFormProps {
  initialName?: string;
  initialDescription?: string;
  onSave: (name: string, description: string) => Promise<void>;
  submitLabel: string;
}

export function WatchlistForm({ initialName = '', initialDescription = '', onSave, submitLabel }: WatchlistFormProps) {
  const [name, setName] = useState(initialName);
  const [description, setDescription] = useState(initialDescription);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await onSave(name, description);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('Failed to save');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      {error && <div className="rounded-md bg-red-50 p-3 text-sm text-red-600">{error}</div>}
      <input
        type="text"
        value={name}
        onChange={(e) => setName(e.target.value)}
        required
        maxLength={100}
        placeholder="Watchlist name"
        className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
      />
      <input
        type="text"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        placeholder="Description (optional)"
        className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
      />
      <button
        type="submit"
        disabled={loading}
        className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
      >
        {loading ? 'Saving...' : submitLabel}
      </button>
    </form>
  );
}
