'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { createStrategy, updateStrategy, ApiError } from '@/lib/api';
import { StrategyRulesEditor } from './StrategyRulesEditor';
import type { Strategy, StrategyCreate, StrategyRules, StrategyStyle } from '@/lib/types';

const STYLES: StrategyStyle[] = ['value', 'growth', 'momentum', 'dividend', 'hybrid'];

interface StrategyFormProps {
  mode: 'create' | 'edit';
  initial?: Strategy;
  onSuccess: () => void;
}

export function StrategyForm({ mode, initial, onSuccess }: StrategyFormProps) {
  const router = useRouter();
  const [name, setName] = useState(initial?.name ?? '');
  const [style, setStyle] = useState<StrategyStyle | ''>(initial?.style ?? '');
  const [description, setDescription] = useState(initial?.description ?? '');
  const [rules, setRules] = useState<StrategyRules>(initial?.rules ?? {});
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      setError('Name is required');
      return;
    }
    if (!style) {
      setError('Style is required');
      return;
    }
    setError('');
    setLoading(true);
    try {
      if (mode === 'create') {
        const data: StrategyCreate = {
          name: name.trim(),
          style,
          rules,
          ...(description.trim() ? { description: description.trim() } : {}),
        };
        await createStrategy(data);
      } else {
        await updateStrategy(initial!.id, {
          name: name.trim(),
          style,
          rules,
          ...(description.trim() ? { description: description.trim() } : { description: undefined }),
        });
      }
      onSuccess();
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('Failed to save strategy');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {error && (
        <div className="rounded-md bg-red-50 p-3 text-sm text-red-600">{error}</div>
      )}

      {/* Training ready badge (edit mode, read-only) */}
      {mode === 'edit' && initial && (
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-gray-700">Training ready:</span>
          <span
            className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${
              initial.is_training_ready
                ? 'bg-green-100 text-green-800'
                : 'bg-gray-100 text-gray-500'
            }`}
          >
            {initial.is_training_ready ? 'Ready' : 'Not ready'}
          </span>
        </div>
      )}

      <div className="flex flex-col gap-1">
        <label className="text-sm font-medium text-gray-700">
          Name <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
          maxLength={120}
          placeholder="Strategy name"
          className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div className="flex flex-col gap-1">
        <label className="text-sm font-medium text-gray-700">
          Style <span className="text-red-500">*</span>
        </label>
        <select
          value={style}
          onChange={(e) => setStyle(e.target.value as StrategyStyle)}
          required
          className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Select a style</option>
          {STYLES.map((s) => (
            <option key={s} value={s} className="capitalize">
              {s.charAt(0).toUpperCase() + s.slice(1)}
            </option>
          ))}
        </select>
      </div>

      <div className="flex flex-col gap-1">
        <label className="text-sm font-medium text-gray-700">Description</label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={3}
          maxLength={2000}
          placeholder="Describe this strategy (optional)"
          className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div>
        <label className="mb-2 block text-sm font-medium text-gray-700">Rules</label>
        <div className="rounded-lg border border-gray-200 p-4">
          <StrategyRulesEditor value={rules} onChange={setRules} />
        </div>
      </div>

      <div className="flex items-center gap-3">
        <button
          type="submit"
          disabled={loading}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Saving...' : mode === 'create' ? 'Create Strategy' : 'Save Changes'}
        </button>
        <button
          type="button"
          onClick={() => router.push('/strategy')}
          className="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}
