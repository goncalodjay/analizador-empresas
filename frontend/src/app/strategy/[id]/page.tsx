'use client';
import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { getStrategy, ApiError } from '@/lib/api';
import { StrategyForm } from '@/components/strategy/StrategyForm';
import { ActiveToggle } from '@/components/strategy/ActiveToggle';
import { PrimaryToggle } from '@/components/strategy/PrimaryToggle';
import type { Strategy } from '@/lib/types';

export default function StrategyDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [strategy, setStrategy] = useState<Strategy | null>(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);
  const [error, setError] = useState('');

  const id = params.id as string;

  useEffect(() => {
    getStrategy(id)
      .then(setStrategy)
      .catch((err) => {
        if (err instanceof ApiError && err.status === 404) {
          setNotFound(true);
        } else {
          setError('Failed to load strategy');
        }
      })
      .finally(() => setLoading(false));
  }, [id]);

  const handleActivateToggle = (updated: Strategy) => setStrategy(updated);
  const handlePrimarySet = (updated: Strategy) => setStrategy(updated);

  if (loading) return <div className="p-6 text-gray-500">Loading...</div>;
  if (notFound) return (
    <div className="p-6">
      <h1 className="mb-2 text-2xl font-bold text-gray-900">Strategy not found</h1>
      <p className="text-gray-500">This strategy does not exist or you do not have access to it.</p>
      <button
        onClick={() => router.push('/strategy')}
        className="mt-4 text-sm text-blue-600 hover:underline"
      >
        Back to Strategies
      </button>
    </div>
  );
  if (error) return <div className="p-6 text-red-600">{error}</div>;
  if (!strategy) return null;

  return (
    <div className="p-6">
      <h1 className="mb-6 text-2xl font-bold text-gray-900">Edit Strategy</h1>
      <div className="max-w-2xl space-y-6">
        <StrategyForm
          mode="edit"
          initial={strategy}
          onSuccess={() => router.push('/strategy')}
        />

        <div className="rounded-lg border border-gray-200 bg-gray-50 p-4">
          <h2 className="mb-3 text-sm font-semibold text-gray-700">Status Controls</h2>
          <div className="flex items-center gap-6">
            <div className="flex flex-col gap-1">
              <span className="text-xs font-medium text-gray-600">Active</span>
              <ActiveToggle
                strategyId={strategy.id}
                isActive={strategy.is_active}
                onToggle={handleActivateToggle}
              />
            </div>
            <div className="flex flex-col gap-1">
              <span className="text-xs font-medium text-gray-600">Primary</span>
              <PrimaryToggle
                strategyId={strategy.id}
                isPrimary={strategy.is_primary}
                onSet={handlePrimarySet}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
