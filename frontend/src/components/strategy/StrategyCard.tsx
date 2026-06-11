'use client';
import Link from 'next/link';
import { useState } from 'react';
import { deleteStrategy, ApiError } from '@/lib/api';
import { ActiveToggle } from './ActiveToggle';
import { PrimaryToggle } from './PrimaryToggle';
import type { Strategy } from '@/lib/types';

interface StrategyCardProps {
  strategy: Strategy;
  onActivateToggle: (updated: Strategy) => void;
  onPrimarySet: (updated: Strategy) => void;
  onDelete: (id: string) => void;
}

const STYLE_COLORS: Record<string, string> = {
  value: 'bg-green-100 text-green-800',
  growth: 'bg-blue-100 text-blue-800',
  momentum: 'bg-purple-100 text-purple-800',
  dividend: 'bg-yellow-100 text-yellow-800',
  hybrid: 'bg-gray-100 text-gray-800',
};

function rulesSummary(rules: Strategy['rules']): string {
  const set = Object.entries(rules).filter(([, v]) => v !== undefined && v !== null);
  if (set.length === 0) return 'No rules set';
  if (set.length <= 2) {
    return set.map(([k, v]) => `${k}: ${v}`).join(', ');
  }
  return `${set.length} rules set`;
}

export function StrategyCard({
  strategy,
  onActivateToggle,
  onPrimarySet,
  onDelete,
}: StrategyCardProps) {
  const [deleteError, setDeleteError] = useState('');

  const handleDelete = async () => {
    if (!window.confirm(`Delete strategy "${strategy.name}"? This cannot be undone.`)) return;
    setDeleteError('');
    try {
      await deleteStrategy(strategy.id);
      onDelete(strategy.id);
    } catch (err) {
      if (err instanceof ApiError) {
        setDeleteError(err.message);
      } else {
        setDeleteError('Failed to delete strategy');
      }
    }
  };

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
      <div className="mb-3 flex items-start justify-between gap-2">
        <Link
          href={`/strategy/${strategy.id}`}
          className="text-lg font-semibold text-gray-900 hover:text-blue-600 hover:underline"
        >
          {strategy.name}
        </Link>
        <div className="flex shrink-0 items-center gap-2">
          <span
            className={`rounded-full px-2.5 py-0.5 text-xs font-medium capitalize ${
              STYLE_COLORS[strategy.style] ?? 'bg-gray-100 text-gray-800'
            }`}
          >
            {strategy.style}
          </span>
          {strategy.is_primary && (
            <span className="rounded-full bg-yellow-100 px-2.5 py-0.5 text-xs font-medium text-yellow-800">
              Primary
            </span>
          )}
        </div>
      </div>

      {strategy.description && (
        <p className="mb-3 text-sm text-gray-500 line-clamp-2">{strategy.description}</p>
      )}

      <p className="mb-4 text-xs text-gray-400">{rulesSummary(strategy.rules)}</p>

      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <ActiveToggle
            strategyId={strategy.id}
            isActive={strategy.is_active}
            onToggle={onActivateToggle}
          />
          <PrimaryToggle
            strategyId={strategy.id}
            isPrimary={strategy.is_primary}
            onSet={onPrimarySet}
          />
        </div>
        <button
          onClick={handleDelete}
          className="text-xs text-red-600 hover:text-red-800 hover:underline"
        >
          Delete
        </button>
      </div>

      {deleteError && (
        <p className="mt-2 text-xs text-red-600">{deleteError}</p>
      )}
    </div>
  );
}
