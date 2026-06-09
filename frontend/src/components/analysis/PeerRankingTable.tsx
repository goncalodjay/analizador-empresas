'use client';

interface Peer {
  ticker: string;
  name?: string | null;
  pe_trailing?: string | null;
  revenue_growth?: string | null;
  roe?: string | null;
  debt_to_equity?: string | null;
}

interface PeerRankingTableProps {
  ticker: string;
  peers: Peer[];
  rankings: Record<string, number>;
}

export function PeerRankingTable({ ticker, peers, rankings }: PeerRankingTableProps) {
  if (peers.length === 0) return null;

  return (
    <div className="rounded-lg border bg-white p-4">
      <h3 className="mb-3 font-semibold">Peer Comparison</h3>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="border-b">
            <tr>
              <th className="py-2 pr-4 font-medium">Ticker</th>
              <th className="py-2 pr-4 font-medium">P/E</th>
              <th className="py-2 pr-4 font-medium">Rev Growth</th>
              <th className="py-2 pr-4 font-medium">ROE</th>
              <th className="py-2 pr-4 font-medium">D/E</th>
            </tr>
          </thead>
          <tbody>
            {peers.slice(0, 6).map((peer) => (
              <tr
                key={peer.ticker}
                className={`border-b ${peer.ticker === ticker ? 'bg-blue-50 font-medium' : ''}`}
              >
                <td className="py-2 pr-4">{peer.ticker}</td>
                <td className="py-2 pr-4">{peer.pe_trailing ?? '—'}</td>
                <td className="py-2 pr-4">{peer.revenue_growth ? `${peer.revenue_growth}%` : '—'}</td>
                <td className="py-2 pr-4">{peer.roe ? `${peer.roe}%` : '—'}</td>
                <td className="py-2 pr-4">{peer.debt_to_equity ?? '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {Object.keys(rankings).length > 0 && (
        <div className="mt-2 text-xs text-gray-400">
          Ranked #{rankings.pe_trailing} in P/E • #{rankings.revenue_growth} in Rev Growth
        </div>
      )}
    </div>
  );
}
