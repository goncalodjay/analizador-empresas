'use client';

interface MacdSummaryProps {
  macdLine: number;
  signalLine: number;
  histogram: number;
  crossover: 'bullish' | 'bearish' | 'neutral';
}

const crossoverStyles: Record<MacdSummaryProps['crossover'], { badge: string; label: string }> = {
  bullish: { badge: 'bg-green-100 text-green-800', label: 'Bullish' },
  bearish: { badge: 'bg-red-100 text-red-800', label: 'Bearish' },
  neutral: { badge: 'bg-gray-100 text-gray-600', label: 'Neutral' },
};

function fmt(n: number): string {
  return n.toFixed(4);
}

export function MacdSummary({ macdLine, signalLine, histogram, crossover }: MacdSummaryProps) {
  const styles = crossoverStyles[crossover];
  const histPositive = histogram >= 0;

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-gray-700">MACD (12/26/9)</span>
        <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${styles.badge}`}>
          {styles.label}
        </span>
      </div>

      <div className="grid grid-cols-3 gap-2 text-sm">
        <div className="rounded-md bg-gray-50 p-2 text-center">
          <div className="text-xs text-gray-500 mb-0.5">MACD Line</div>
          <div className="font-semibold text-gray-800">{fmt(macdLine)}</div>
        </div>
        <div className="rounded-md bg-gray-50 p-2 text-center">
          <div className="text-xs text-gray-500 mb-0.5">Signal</div>
          <div className="font-semibold text-gray-800">{fmt(signalLine)}</div>
        </div>
        <div className="rounded-md bg-gray-50 p-2 text-center">
          <div className="text-xs text-gray-500 mb-0.5">Histogram</div>
          <div className={`font-semibold ${histPositive ? 'text-green-600' : 'text-red-600'}`}>
            {histPositive ? '+' : ''}{fmt(histogram)}
          </div>
        </div>
      </div>
    </div>
  );
}
