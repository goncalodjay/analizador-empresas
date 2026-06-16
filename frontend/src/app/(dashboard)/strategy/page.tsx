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
        return { ...s, is_primary: false };
      }),
    );
  };

  const handleDelete = (id: string) => {
    setStrategies((prev) => prev.filter((s) => s.id !== id));
  };

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-neutral-900">Strategies</h1>
        <Link
          href="/strategy/new"
          className="rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-neutral-0 hover:bg-primary-700 transition-colors"
        >
          New Strategy
        </Link>
      </div>

      {loading && <p className="text-neutral-500">Loading...</p>}
      {error && <p className="text-error">{error}</p>}

      {!loading && !error && strategies.length === 0 && (
        <div className="rounded-lg border border-dashed border-neutral-300 p-12 text-center">
          <p className="text-neutral-600">No strategies yet.</p>
          <Link
            href="/strategy/new"
            className="mt-2 inline-block text-sm text-primary-600 hover:text-primary-700 transition-colors"
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
