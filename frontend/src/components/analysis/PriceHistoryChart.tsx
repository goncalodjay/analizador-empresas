'use client';

import type { PricePoint } from '@/lib/types';
import { DataFreshnessTag } from '@/components/layout/DataFreshnessTag';

interface PriceHistoryChartProps {
  ticker: string;
  points: PricePoint[];
  freshness: string;
  fetchedAt?: string | null;
}

const SVG_WIDTH = 800;
const SVG_HEIGHT = 220;
const PADDING_X = 48;
const PADDING_TOP = 16;
const PADDING_BOTTOM = 32;

function formatDate(dateStr: string): string {
  const d = new Date(dateStr + 'T00:00:00');
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function formatPrice(price: number): string {
  return price >= 1000
    ? `$${(price / 1000).toFixed(1)}k`
    : `$${price.toFixed(2)}`;
}

export function PriceHistoryChart({
  ticker,
  points,
  freshness,
  fetchedAt,
}: PriceHistoryChartProps) {
  if (points.length === 0) {
    return (
      <div className="rounded-lg border border-gray-200 bg-gray-50 p-6 text-center">
        <p className="text-sm text-gray-500">
          No price history available for {ticker}. Run ingestion to populate data.
        </p>
      </div>
    );
  }

  const closes = points.map((p) => parseFloat(p.close));
  const minClose = Math.min(...closes);
  const maxClose = Math.max(...closes);
  const priceRange = maxClose - minClose || 1;

  const chartWidth = SVG_WIDTH - PADDING_X * 2;
  const chartHeight = SVG_HEIGHT - PADDING_TOP - PADDING_BOTTOM;

  const toX = (i: number) =>
    PADDING_X + (i / (points.length - 1)) * chartWidth;

  const toY = (price: number) =>
    PADDING_TOP + chartHeight - ((price - minClose) / priceRange) * chartHeight;

  const polylinePoints = closes
    .map((price, i) => `${toX(i)},${toY(price)}`)
    .join(' ');

  // Area fill path (close the polygon below the chart)
  const areaPath =
    `M ${toX(0)},${toY(closes[0])} ` +
    closes.map((price, i) => `L ${toX(i)},${toY(price)}`).join(' ') +
    ` L ${toX(closes.length - 1)},${PADDING_TOP + chartHeight}` +
    ` L ${toX(0)},${PADDING_TOP + chartHeight} Z`;

  // Date labels: show up to 6 evenly spaced labels
  const labelIndices: number[] = [];
  const maxLabels = Math.min(6, points.length);
  for (let i = 0; i < maxLabels; i++) {
    labelIndices.push(Math.round((i / (maxLabels - 1)) * (points.length - 1)));
  }

  // Y-axis labels: min, mid, max
  const midClose = (minClose + maxClose) / 2;
  const yLabels = [
    { price: maxClose, y: toY(maxClose) },
    { price: midClose, y: toY(midClose) },
    { price: minClose, y: toY(minClose) },
  ];

  const freshnessStatus =
    freshness === 'fresh' ? 'live' : freshness === 'stale' ? 'stale' : 'eod';

  const latestClose = closes[closes.length - 1];
  const firstClose = closes[0];
  const changePct = ((latestClose - firstClose) / firstClose) * 100;
  const isPositive = changePct >= 0;

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <div className="mb-3 flex items-center justify-between">
        <div>
          <span className="text-sm font-semibold text-gray-700">
            Price history (our data)
          </span>
          <span className="ml-2 text-xs text-gray-400">— Close price</span>
        </div>
        <div className="flex items-center gap-2">
          <span
            className={`text-sm font-medium ${
              isPositive ? 'text-green-600' : 'text-red-600'
            }`}
          >
            {isPositive ? '+' : ''}
            {changePct.toFixed(2)}%
          </span>
          <DataFreshnessTag
            status={freshnessStatus as 'live' | 'delayed' | 'eod' | 'stale'}
            timestamp={fetchedAt ? fetchedAt.slice(0, 10) : undefined}
          />
          <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-500">
            Reported
          </span>
        </div>
      </div>

      <svg
        viewBox={`0 0 ${SVG_WIDTH} ${SVG_HEIGHT}`}
        className="h-auto w-full"
        aria-label={`Price history chart for ${ticker}`}
      >
        {/* Gradient fill */}
        <defs>
          <linearGradient id="priceAreaGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.15" />
            <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.01" />
          </linearGradient>
        </defs>

        {/* Y-axis gridlines and labels */}
        {yLabels.map(({ price, y }, idx) => (
          <g key={idx}>
            <line
              x1={PADDING_X}
              y1={y}
              x2={SVG_WIDTH - PADDING_X}
              y2={y}
              stroke="#e5e7eb"
              strokeWidth="1"
              strokeDasharray="4 4"
            />
            <text
              x={PADDING_X - 4}
              y={y + 4}
              textAnchor="end"
              fontSize="10"
              fill="#9ca3af"
            >
              {formatPrice(price)}
            </text>
          </g>
        ))}

        {/* Area fill */}
        <path d={areaPath} fill="url(#priceAreaGrad)" />

        {/* Price line */}
        <polyline
          points={polylinePoints}
          fill="none"
          stroke="#3b82f6"
          strokeWidth="1.5"
          strokeLinejoin="round"
          strokeLinecap="round"
        />

        {/* Date labels on X axis */}
        {labelIndices.map((idx) => (
          <text
            key={idx}
            x={toX(idx)}
            y={SVG_HEIGHT - 4}
            textAnchor="middle"
            fontSize="10"
            fill="#9ca3af"
          >
            {formatDate(points[idx].date)}
          </text>
        ))}
      </svg>
    </div>
  );
}
