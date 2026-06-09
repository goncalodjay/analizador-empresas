'use client';
import { DataFreshnessTag } from '@/components/layout/DataFreshnessTag';

interface MetricCardProps {
  label: string;
  value: string | null;
  category: string;
  nature?: string;
  source?: string | null;
}

export function MetricCard({ label, value, category, nature, source }: MetricCardProps) {
  const categoryColors: Record<string, string> = {
    valuation: 'border-blue-200 bg-blue-50',
    growth: 'border-green-200 bg-green-50',
    financial_health: 'border-yellow-200 bg-yellow-50',
    dividend: 'border-purple-200 bg-purple-50',
  };

  return (
    <div className={`rounded-lg border p-3 ${categoryColors[category] || 'border-gray-200 bg-white'}`}>
      <div className="text-xs text-gray-500">{label}</div>
      <div className="mt-1 text-xl font-semibold text-gray-900">
        {value ?? '—'}
      </div>
      {nature === 'computed' && (
        <span className="mt-1 inline-block text-xs text-gray-400">computed</span>
      )}
      {source && <DataFreshnessTag status="live" timestamp={source} />}
    </div>
  );
}
