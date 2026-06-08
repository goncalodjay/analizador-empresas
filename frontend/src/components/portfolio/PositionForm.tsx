'use client';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { apiFetch, ApiError } from '@/lib/api';
import type { PortfolioPosition, PortfolioPositionCreate, PortfolioPositionUpdate } from '@/lib/types';

interface PositionFormProps {
  position?: PortfolioPosition;
}

export function PositionForm({ position }: PositionFormProps) {
  const router = useRouter();
  const isEdit = !!position;
  const [form, setForm] = useState({
    ticker: position?.ticker || '',
    shares: position?.shares || '',
    avg_buy_price: position?.avg_buy_price || '',
    sector: position?.sector || '',
    notes: position?.notes || '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isEdit) {
        const payload: PortfolioPositionUpdate = {
          ticker: form.ticker,
          shares: form.shares,
          avg_buy_price: form.avg_buy_price,
          sector: form.sector || undefined,
          notes: form.notes || undefined,
        };
        await apiFetch(`/portfolio/positions/${position.id}`, {
          method: 'PUT',
          body: JSON.stringify(payload),
        });
      } else {
        const payload: PortfolioPositionCreate = {
          ticker: form.ticker,
          shares: form.shares,
          avg_buy_price: form.avg_buy_price,
          sector: form.sector || undefined,
          notes: form.notes || undefined,
        };
        await apiFetch('/portfolio/positions', {
          method: 'POST',
          body: JSON.stringify(payload),
        });
      }
      router.push('/portfolio');
      router.refresh();
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('Failed to save position');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="rounded-md bg-red-50 p-3 text-sm text-red-600">{error}</div>
      )}
      <div>
        <label className="block text-sm font-medium text-gray-700">Ticker</label>
        <input
          type="text"
          name="ticker"
          value={form.ticker}
          onChange={handleChange}
          required
          maxLength={10}
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
          placeholder="AAPL"
        />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Shares</label>
          <input
            type="text"
            name="shares"
            value={form.shares}
            onChange={handleChange}
            required
            pattern="[0-9]+\.?[0-9]*"
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
            placeholder="50"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Avg Buy Price</label>
          <input
            type="text"
            name="avg_buy_price"
            value={form.avg_buy_price}
            onChange={handleChange}
            required
            pattern="[0-9]+\.?[0-9]*"
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
            placeholder="175.50"
          />
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700">Sector (optional)</label>
        <input
          type="text"
          name="sector"
          value={form.sector}
          onChange={handleChange}
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
          placeholder="Technology"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700">Notes (optional)</label>
        <input
          type="text"
          name="notes"
          value={form.notes}
          onChange={handleChange}
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
        />
      </div>
      <div className="flex gap-3">
        <button
          type="submit"
          disabled={loading}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Saving...' : isEdit ? 'Update Position' : 'Create Position'}
        </button>
        <button
          type="button"
          onClick={() => router.back()}
          className="rounded-md border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}
