type FreshnessStatus = 'live' | 'delayed' | 'eod' | 'stale';

interface DataFreshnessTagProps {
  status: FreshnessStatus;
  timestamp?: string;
}

const statusStyles: Record<FreshnessStatus, string> = {
  live: 'bg-green-100 text-green-800',
  delayed: 'bg-yellow-100 text-yellow-800',
  eod: 'bg-gray-100 text-gray-600',
  stale: 'bg-red-100 text-red-800',
};

const statusLabels: Record<FreshnessStatus, string> = {
  live: 'Live',
  delayed: '15m Delay',
  eod: 'EOD',
  stale: 'Stale',
};

export function DataFreshnessTag({ status, timestamp }: DataFreshnessTagProps) {
  return (
    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${statusStyles[status]}`}>
      {statusLabels[status]}
      {timestamp && <span className="ml-1 opacity-75">{timestamp}</span>}
    </span>
  );
}
