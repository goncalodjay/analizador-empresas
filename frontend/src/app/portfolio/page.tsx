'use client';
import Link from 'next/link';
import { useEffect, useState } from 'react';
import { apiFetch } from '@/lib/api';
import { PortfolioTable } from '@/components/portfolio/PortfolioTable';
import { DataFreshnessTag } from '@/components/layout/DataFreshnessTag';
import type { PortfolioPosition } from '@/lib/types';

export default function PortfolioPage() {
  const [positions, setPositions] = useState<PortfolioPosition[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchPositions = async () => {
    try {
      const data = await apiFetch<PortfolioPosition[]>('/portfolio/positions');
      setPositions(data);
    } catch {
      setError('Failed to load positions');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPositions();
  }, []);

  const handleDelete = (id: string) => {
    setPositions((prev) => prev.filter((p) => p.id !== id));
  };

  return (
    <div className="p-6">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Portfolio</h1>
          <DataFreshnessTag status="live" />
        </div>
        <Link
          href="/portfolio/new"
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
        >
          Add Position
        </Link>
      </div>

      {loading && <p className="text-gray-500">Loading...</p>}
      {error && <p className="text-red-600">{error}</p>}
      {!loading && !error && <PortfolioTable positions={positions} onDelete={handleDelete} />}
    </div>
  );
}
