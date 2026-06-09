'use client';

interface HealthScoreGaugeProps {
  composite: number;
  verdict: string;
  subScores: {
    fundamental_quality: number;
    earnings_momentum: number;
    analyst_sentiment: number;
    technical_momentum: number;
  };
  topDrivers: string[];
}

const verdictColors: Record<string, string> = {
  'Strong Buy': 'text-green-600',
  Accumulate: 'text-emerald-500',
  Hold: 'text-yellow-500',
  Reduce: 'text-orange-500',
  Avoid: 'text-red-600',
};

export function HealthScoreGauge({
  composite,
  verdict,
  subScores,
  topDrivers,
}: HealthScoreGaugeProps) {
  const radius = 50;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (composite / 100) * circumference;

  return (
    <div className="rounded-lg border bg-white p-6">
      <h3 className="mb-4 text-lg font-semibold">Health Score</h3>
      <div className="flex flex-col items-center sm:flex-row sm:gap-8">
        <div className="relative h-32 w-32">
          <svg className="h-full w-full -rotate-90" viewBox="0 0 120 120">
            <circle cx="60" cy="60" r={radius} fill="none" stroke="#e5e7eb" strokeWidth="10" />
            <circle
              cx="60"
              cy="60"
              r={radius}
              fill="none"
              stroke={composite >= 65 ? '#16a34a' : composite >= 45 ? '#ca8a04' : '#dc2626'}
              strokeWidth="10"
              strokeDasharray={circumference}
              strokeDashoffset={offset}
              strokeLinecap="round"
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-2xl font-bold">{composite}</span>
            <span className="text-xs text-gray-500">/100</span>
          </div>
        </div>
        <div className="mt-4 sm:mt-0">
          <span className={`text-lg font-bold ${verdictColors[verdict] || 'text-gray-600'}`}>
            {verdict}
          </span>
          <div className="mt-2 grid grid-cols-2 gap-2 text-sm">
            <span className="text-gray-500">Fund. Quality:</span>
            <span className="font-medium">{subScores.fundamental_quality}/25</span>
            <span className="text-gray-500">Earnings Mom.:</span>
            <span className="font-medium">{subScores.earnings_momentum}/25</span>
            <span className="text-gray-500">Analyst Sent.:</span>
            <span className="font-medium">{subScores.analyst_sentiment}/25</span>
            <span className="text-gray-500">Tech. Mom.:</span>
            <span className="font-medium">{subScores.technical_momentum}/25</span>
          </div>
          {topDrivers.length > 0 && (
            <div className="mt-2 text-xs text-gray-400">
              Top drivers: {topDrivers.join(', ')}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
