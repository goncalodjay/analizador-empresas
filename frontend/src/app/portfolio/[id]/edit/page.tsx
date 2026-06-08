'use client';
import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { apiFetch } from '@/lib/api';
import { PositionForm } from '@/components/portfolio/PositionForm';
import type { PortfolioPosition } from '@/lib/types';

export default function EditPositionPage() {
  const params = useParams();
  const [position, setPosition] = useState<PortfolioPosition | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchPosition = async () => {
      try {
        const data = await apiFetch<PortfolioPosition>(`/portfolio/positions/${params.id}`);
        setPosition(data);
      } catch {
        setError('Failed to load position');
      } finally {
        setLoading(false);
      }
    };
    fetchPosition();
  }, [params.id]);

  if (loading) return <div className="p-6 text-gray-500">Loading...</div>;
  if (error) return <div className="p-6 text-red-600">{error}</div>;
  if (!position) return <div className="p-6 text-gray-500">Position not found</div>;

  return (
    <div className="p-6">
      <h1 className="mb-6 text-2xl font-bold text-gray-900">Edit {position.ticker}</h1>
      <div className="max-w-lg">
        <PositionForm position={position} />
      </div>
    </div>
  );
}
