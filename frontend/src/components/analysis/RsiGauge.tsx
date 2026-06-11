'use client';

interface RsiGaugeProps {
  value: number;
  zone: 'oversold' | 'neutral' | 'overbought';
  trend: 'rising' | 'falling' | 'steady';
}

const zoneColors: Record<RsiGaugeProps['zone'], string> = {
  oversold: 'text-blue-600',
  neutral: 'text-yellow-600',
  overbought: 'text-red-600',
};

const trendSymbol: Record<RsiGaugeProps['trend'], string> = {
  rising: '↑',
  falling: '↓',
  steady: '→',
};

export function RsiGauge({ value, zone, trend }: RsiGaugeProps) {
  const clampedValue = Math.max(0, Math.min(100, value));
  const positionPct = clampedValue;

  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <span className="text-sm font-medium text-gray-700">RSI (14)</span>
        <span className={`text-sm font-semibold ${zoneColors[zone]}`}>
          {clampedValue.toFixed(1)} {trendSymbol[trend]}
        </span>
      </div>

      {/* Bar background with zones */}
      <div className="relative h-4 w-full rounded-full overflow-hidden flex">
        {/* Oversold zone: 0-30 (30% width) */}
        <div className="h-full bg-blue-200" style={{ width: '30%' }} />
        {/* Neutral zone: 30-70 (40% width) */}
        <div className="h-full bg-yellow-100" style={{ width: '40%' }} />
        {/* Overbought zone: 70-100 (30% width) */}
        <div className="h-full bg-red-200" style={{ width: '30%' }} />

        {/* Needle */}
        <div
          className="absolute top-0 h-full w-0.5 bg-gray-800"
          style={{ left: `calc(${positionPct}% - 1px)` }}
        />
      </div>

      {/* Zone labels */}
      <div className="flex justify-between mt-0.5 text-xs text-gray-400">
        <span>Oversold</span>
        <span>Neutral</span>
        <span>Overbought</span>
      </div>

      <div className="mt-1 text-xs text-gray-500 capitalize">
        Zone: <span className={`font-medium ${zoneColors[zone]}`}>{zone}</span>
        {' · '}Trend: <span className="font-medium">{trend}</span>
      </div>
    </div>
  );
}
