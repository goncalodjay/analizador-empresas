'use client';
import { useState } from 'react';
import { activateStrategy, ApiError } from '@/lib/api';
import type { Strategy } from '@/lib/types';

interface ActiveToggleProps {
  strategyId: string;
  isActive: boolean;
  onToggle: (updated: Strategy) => void;
}

export function ActiveToggle({ strategyId, isActive, onToggle }: ActiveToggleProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleClick = async () => {
    setError('');
    setLoading(true);
    try {
      const updated = await activateStrategy(strategyId, !isActive);
      onToggle(updated);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('Failed to update status');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-1">
      <button
        role="switch"
        aria-checked={isActive}
        onClick={handleClick}
        disabled={loading}
        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 ${
          isActive ? 'bg-blue-600' : 'bg-gray-200'
        }`}
        title={isActive ? 'Active — click to deactivate' : 'Inactive — click to activate'}
      >
        <span
          className={`inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform ${
            isActive ? 'translate-x-6' : 'translate-x-1'
          }`}
        />
      </button>
      <span className="text-xs text-gray-500">{isActive ? 'Active' : 'Inactive'}</span>
      {error && <p className="text-xs text-red-600">{error}</p>}
    </div>
  );
}
