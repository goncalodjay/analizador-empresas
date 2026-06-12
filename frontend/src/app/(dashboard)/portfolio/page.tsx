'use client';
import { useEffect, useState } from 'react';
import { apiFetch } from '@/lib/api';
import { IOLHoldingsTable } from '@/components/portfolio/IOLHoldingsTable';
import { IOLSetupForm } from '@/components/portfolio/IOLSetupForm';
import { DataFreshnessTag } from '@/components/layout/DataFreshnessTag';
import type { IOLHolding, IOLStatus, IOLSyncResponse } from '@/lib/types';

export default function PortfolioPage() {
  const [holdings, setHoldings] = useState<IOLHolding[]>([]);
  const [iolStatus, setIolStatus] = useState<IOLStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [error, setError] = useState('');
  const [syncTimestamp, setSyncTimestamp] = useState<string | null>(null);

  const fetchHoldings = async () => {
    try {
      setLoading(true);
      const data = await apiFetch<{ holdings: IOLHolding[] }>('/iol/holdings');
      setHoldings(data.holdings);
    } catch {
      setError('Failed to load holdings');
      setHoldings([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchStatus = async () => {
    try {
      const status = await apiFetch<IOLStatus>('/iol/status');
      setIolStatus(status);
      if (status.connected) {
        setSyncTimestamp(status.last_sync || null);
      }
    } catch {
      setIolStatus(null);
    }
  };

  const handleSync = async () => {
    try {
      setSyncing(true);
      setError('');
      const response = await apiFetch<IOLSyncResponse>('/iol/sync-now', {
        method: 'POST',
      });
      setSyncTimestamp(response.synced_at);
      await fetchHoldings();
    } catch (err) {
      setError(
        err instanceof Error && err.message.includes('401')
          ? 'IOL connection expired. Please reconnect your account.'
          : 'Portfolio sync failed. Please try again.'
      );
    } finally {
      setSyncing(false);
    }
  };

  const handleSetupSuccess = async () => {
    await fetchStatus();
    await fetchHoldings();
  };

  useEffect(() => {
    const initialize = async () => {
      await fetchStatus();
      await fetchHoldings();
    };
    initialize();
  }, []);

  const isConnected = iolStatus?.connected ?? false;

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">Portfolio</h1>
          {isConnected && <DataFreshnessTag status="live" />}
        </div>
        {isConnected && (
          <button
            onClick={handleSync}
            disabled={syncing || !isConnected}
            className="rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-neutral-0 hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {syncing ? 'Syncing...' : 'Sync Now'}
          </button>
        )}
      </div>

      {!isConnected && (
        <div className="mb-6">
          <IOLSetupForm onSuccess={handleSetupSuccess} />
        </div>
      )}

      {error && <p className="mb-4 text-sm text-error">{error}</p>}

      {isConnected && syncTimestamp && (
        <p className="mb-4 text-xs text-neutral-500">
          Last synced: {new Date(syncTimestamp).toLocaleString()}
        </p>
      )}

      {loading ? (
        <p className="text-neutral-500">Loading holdings...</p>
      ) : (
        <IOLHoldingsTable holdings={holdings} />
      )}
    </div>
  );
}
