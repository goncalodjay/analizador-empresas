import type { NewsItemOut } from '@/lib/types';
import { DataFreshnessTag } from '@/components/layout/DataFreshnessTag';
import { NewsItemCard } from '@/components/analysis/NewsItemCard';

interface NewsFeedProps {
  items: NewsItemOut[];
  available: boolean;
  cachedAt: string | null;
  freshness: 'live' | 'stale' | null;
}

function freshnessStatus(freshness: 'live' | 'stale' | null): 'live' | 'stale' {
  if (freshness === 'live') return 'live';
  return 'stale';
}

export function NewsFeed({ items, available, cachedAt, freshness }: NewsFeedProps) {
  const tagTimestamp = cachedAt ? cachedAt.slice(0, 16) : undefined;

  return (
    <section aria-label="Recent News">
      <div className="mb-3 flex items-center gap-3">
        <h2 className="text-lg font-semibold text-gray-900">Recent News</h2>
        <DataFreshnessTag
          status={freshnessStatus(freshness)}
          timestamp={tagTimestamp}
        />
      </div>

      {!available && (
        <p className="text-sm text-gray-500">
          News unavailable (no provider configured).
        </p>
      )}

      {available && items.length === 0 && (
        <p className="text-sm text-gray-500">
          No recent news available for this ticker.
        </p>
      )}

      {available && items.length > 0 && (
        <div className="flex flex-col gap-3">
          {items.map((item, idx) => (
            <NewsItemCard key={item.url ?? idx} item={item} />
          ))}
        </div>
      )}
    </section>
  );
}
