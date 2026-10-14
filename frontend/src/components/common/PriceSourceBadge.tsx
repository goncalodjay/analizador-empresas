'use client';

interface PriceSourceBadgeProps {
  source?: string;
  fetched_at?: string | null;
}

/**
 * PriceSourceBadge displays a badge indicating which price source was used.
 * Color-coded by source:
 * - IOL BCBA: green
 * - Yahoo Finance: blue
 * - Stale: orange
 */
export function PriceSourceBadge({ source = 'yfinance', fetched_at }: PriceSourceBadgeProps) {
  // Determine badge color based on source
  let badgeColor = 'bg-primary-100 text-primary-700';  // Default: yfinance (blue)
  let displayText = 'Yahoo';

  if (source === 'iol-bcba' || source === 'iol') {
    badgeColor = 'bg-success/20 text-success';
    displayText = 'IOL';
  } else if (source === 'stale') {
    badgeColor = 'bg-warning/20 text-warning';
    displayText = 'Stale';
  } else if (source?.includes('yfinance') || source === 'yfinance') {
    badgeColor = 'bg-primary-100 text-primary-700';
    displayText = 'Yahoo';
  }

  // Format timestamp for tooltip
  let timeAgo = '';
  if (fetched_at) {
    try {
      const now = new Date();
      const fetched = new Date(fetched_at);
      const diffMs = now.getTime() - fetched.getTime();
      const diffMins = Math.floor(diffMs / 60000);
      const diffHours = Math.floor(diffMs / 3600000);

      if (diffMins < 1) {
        timeAgo = 'just now';
      } else if (diffMins < 60) {
        timeAgo = `${diffMins}m ago`;
      } else if (diffHours < 24) {
        timeAgo = `${diffHours}h ago`;
      } else {
        timeAgo = `${Math.floor(diffHours / 24)}d ago`;
      }
    } catch {
      timeAgo = '';
    }
  }

  return (
    <span
      className={`inline-flex items-center rounded-sm px-2 py-0.5 text-xs font-medium ${badgeColor}`}
      title={timeAgo ? `Updated ${timeAgo}` : 'Updated at unknown time'}
    >
      {displayText}
      {timeAgo && <span className="ml-1 opacity-75">({timeAgo})</span>}
    </span>
  );
}
