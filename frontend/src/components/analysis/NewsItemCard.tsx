import type { NewsItemOut } from '@/lib/types';

interface NewsItemCardProps {
  item: NewsItemOut;
}

function formatDate(isoString: string | null): string {
  if (!isoString) return '';
  try {
    return new Date(isoString).toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  } catch {
    return isoString;
  }
}

export function NewsItemCard({ item }: NewsItemCardProps) {
  return (
    <article className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <div className="mb-1">
        {item.url ? (
          <a
            href={item.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm font-medium text-blue-700 hover:underline"
          >
            {item.headline}
          </a>
        ) : (
          <span className="text-sm font-medium text-gray-900">{item.headline}</span>
        )}
      </div>
      <div className="flex items-center gap-2 text-xs text-gray-500">
        <span>{item.source_name}</span>
        {item.published_at && (
          <>
            <span aria-hidden="true">·</span>
            <time dateTime={item.published_at}>{formatDate(item.published_at)}</time>
          </>
        )}
      </div>
      {item.summary && (
        <p className="mt-2 text-sm text-gray-600 line-clamp-2">{item.summary}</p>
      )}
    </article>
  );
}
