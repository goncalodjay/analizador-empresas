'use client';
import Link from 'next/link';
import { useEffect, useState } from 'react';
import { getStrategies } from '@/lib/api';
import { StrategyCard } from '@/components/strategy/StrategyCard';
import type { Strategy } from '@/lib/types';

export default function StrategyListPage() {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    getStrategies()
      .then(setStrategies)
      .catch(() => setError('Failed to load strategies'))
      .finally(() => setLoading(false));
  }, []);

  const handleActivateToggle = (updated: Strategy) => {
    setStrategies((prev) =>
      prev.map((s) => (s.id === updated.id ? updated : s)),
    );
  };

  const handlePrimarySet = (updated: Strategy) => {
    setStrategies((prev) =>
      prev.map((s) => {
        if (s.id === updated.id) return updated;
        // Clear primary on all other cards — server enforces this but update locally too
        return { ...s, is_primary: false };
      }),
    );
  };

  const handleDelete = (id: string) => {
    setStrategies((prev) => prev.filter((s) => s.id !== id));
  };

  return (
    <div className="p-6">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Strategies</h1>
        <Link
          href="/strategy/new"
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
        >
          New Strategy
        </Link>
      </div>

      {loading && <p className="text-gray-500">Loading...</p>}
      {error && <p className="text-red-600">{error}</p>}

      {!loading && !error && strategies.length === 0 && (
        <div className="rounded-lg border border-dashed border-gray-300 p-12 text-center">
          <p className="text-gray-500">No strategies yet.</p>
          <Link
            href="/strategy/new"
            className="mt-2 inline-block text-sm text-blue-600 hover:underline"
          >
            Create your first strategy
          </Link>
        </div>
      )}

      {!loading && !error && strategies.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {strategies.map((strategy) => (
            <StrategyCard
              key={strategy.id}
              strategy={strategy}
              onActivateToggle={handleActivateToggle}
              onPrimarySet={handlePrimarySet}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}
    </div>
  );
}
