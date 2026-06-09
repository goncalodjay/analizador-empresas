'use client';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { apiFetch } from '@/lib/api';
import type { PortfolioPosition } from '@/lib/types';

interface PortfolioTableProps {
  positions: PortfolioPosition[];
  onDelete: (id: string) => void;
}

export function PortfolioTable({ positions, onDelete }: PortfolioTableProps) {
  const router = useRouter();
  const [deleting, setDeleting] = useState<string | null>(null);

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this position?')) return;
    setDeleting(id);
    try {
      await apiFetch(`/portfolio/positions/${id}`, { method: 'DELETE' });
      onDelete(id);
    } catch (err) {
      alert('Failed to delete position');
    } finally {
      setDeleting(null);
    }
  };

  if (positions.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-gray-300 p-12 text-center">
        <p className="text-gray-500">No positions yet.</p>
        <Link href="/portfolio/new" className="mt-4 inline-block text-sm font-medium text-blue-600 hover:text-blue-800">
          Add your first position
        </Link>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead className="border-b bg-gray-50">
          <tr>
            <th className="px-4 py-3 font-medium">Ticker</th>
            <th className="px-4 py-3 font-medium">Shares</th>
            <th className="px-4 py-3 font-medium">Avg Price</th>
            <th className="px-4 py-3 font-medium">Sector</th>
            <th className="px-4 py-3 font-medium">Actions</th>
          </tr>
        </thead>
        <tbody>
          {positions.map((pos) => (
            <tr key={pos.id} className="border-b hover:bg-gray-50">
              <td className="px-4 py-3 font-medium">
                <Link href={`/analysis/${pos.ticker}`} className="text-blue-600 hover:text-blue-800 hover:underline">
                  {pos.ticker}
                </Link>
              </td>
              <td className="px-4 py-3">{Number(pos.shares).toLocaleString()}</td>
              <td className="px-4 py-3">${Number(pos.avg_buy_price).toFixed(2)}</td>
              <td className="px-4 py-3 text-gray-500">{pos.sector || '—'}</td>
              <td className="px-4 py-3">
                <div className="flex gap-2">
                  <button
                    onClick={() => router.push(`/portfolio/${pos.id}/edit`)}
                    className="text-blue-600 hover:text-blue-800"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(pos.id)}
                    disabled={deleting === pos.id}
                    className="text-red-600 hover:text-red-800 disabled:opacity-50"
                  >
                    {deleting === pos.id ? 'Deleting...' : 'Delete'}
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
