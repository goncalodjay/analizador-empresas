'use client';
import { useState } from 'react';
import { setPrimaryStrategy, ApiError } from '@/lib/api';
import type { Strategy } from '@/lib/types';

interface PrimaryToggleProps {
  strategyId: string;
  isPrimary: boolean;
  onSet: (updated: Strategy) => void;
}

export function PrimaryToggle({ strategyId, isPrimary, onSet }: PrimaryToggleProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleClick = async () => {
    setError('');
    setLoading(true);
    try {
      const updated = await setPrimaryStrategy(strategyId);
      onSet(updated);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('Failed to set primary');
      }
    } finally {
      setLoading(false);
    }
  };

  if (isPrimary) {
    return (
      <span className="inline-flex items-center rounded-full bg-yellow-100 px-2.5 py-0.5 text-xs font-medium text-yellow-800">
        Primary
      </span>
    );
  }

  return (
    <div className="flex flex-col gap-1">
      <button
        onClick={handleClick}
        disabled={loading}
        className="rounded-md border border-gray-300 px-3 py-1 text-xs font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
      >
        {loading ? 'Setting...' : 'Set as Primary'}
      </button>
      {error && <p className="text-xs text-red-600">{error}</p>}
    </div>
  );
}
