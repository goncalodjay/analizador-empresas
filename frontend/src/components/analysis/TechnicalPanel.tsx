'use client';

import { useState } from 'react';
import { DataFreshnessTag } from '@/components/layout/DataFreshnessTag';
import { RsiGauge } from './RsiGauge';
import { MacdSummary } from './MacdSummary';

interface RsiData {
  value: string;
  zone: 'oversold' | 'neutral' | 'overbought';
  trend: 'rising' | 'falling' | 'steady';
}

interface MacdData {
  macd_line: string;
  signal_line: string;
  histogram: string;
  crossover: 'bullish' | 'bearish' | 'neutral';
}

interface EmaData {
  ema_9: string;
  ema_21: string;
  ema_50: string;
  ema_200: string;
  price_vs_ema_9: 'above' | 'below';
  price_vs_ema_200: 'above' | 'below';
  golden_cross: boolean;
  death_cross: boolean;
}

interface BollingerData {
  upper_band: string;
  middle_band: string;
  lower_band: string;
  bandwidth: string;
  squeeze: boolean;
}

interface FiftyTwoWeekData {
  high: string;
  low: string;
  current: string;
  position_pct: string;
}

interface RelativeVolumeData {
  ratio: string;
  label: 'low' | 'average' | 'high';
}

export interface TechnicalIndicators {
  rsi: RsiData | null;
  macd: MacdData | null;
  ema: EmaData | null;
  bollinger: BollingerData | null;
  fifty_two_week: FiftyTwoWeekData | null;
  relative_volume: RelativeVolumeData | null;
  source: string;
  computed_at: string;
}

interface TechnicalPanelProps {
  technical: TechnicalIndicators;
}

function LabelValue({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between py-1 border-b border-gray-100 last:border-0">
      <span className="text-xs text-gray-500">{label}</span>
      <span className="text-xs font-medium text-gray-800">{value}</span>
    </div>
  );
}

const rvColors: Record<RelativeVolumeData['label'], string> = {
  low: 'text-blue-600',
  average: 'text-yellow-600',
  high: 'text-green-600',
};

export function TechnicalPanel({ technical }: TechnicalPanelProps) {
  const [open, setOpen] = useState(true);
  const { rsi, macd, ema, bollinger, fifty_two_week, relative_volume, computed_at } = technical;

  const timestamp = computed_at ? computed_at.slice(0, 16) : undefined;

  return (
    <div className="rounded-lg border bg-white">
      {/* Header */}
      <button
        type="button"
        onClick={() => setOpen((prev) => !prev)}
        className="flex w-full items-center justify-between px-6 py-4 text-left hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <h3 className="text-lg font-semibold text-gray-900">Technical Indicators</h3>
          <DataFreshnessTag status="live" timestamp={timestamp} />
          <span className="text-xs text-gray-400">Computed · yfinance</span>
        </div>
        <svg
          className={`h-5 w-5 text-gray-400 transition-transform ${open ? 'rotate-180' : ''}`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {open && (
        <div className="px-6 pb-6 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {/* RSI */}
          {rsi && (
            <div className="rounded-md border border-gray-100 p-4">
              <RsiGauge
                value={parseFloat(rsi.value)}
                zone={rsi.zone}
                trend={rsi.trend}
              />
            </div>
          )}

          {/* MACD */}
          {macd && (
            <div className="rounded-md border border-gray-100 p-4">
              <MacdSummary
                macdLine={parseFloat(macd.macd_line)}
                signalLine={parseFloat(macd.signal_line)}
                histogram={parseFloat(macd.histogram)}
                crossover={macd.crossover}
              />
            </div>
          )}

          {/* EMA */}
          {ema && (
            <div className="rounded-md border border-gray-100 p-4">
              <div className="text-sm font-medium text-gray-700 mb-2">
                Exponential Moving Averages
                {ema.golden_cross && (
                  <span className="ml-2 inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium bg-green-100 text-green-800">
                    Golden Cross
                  </span>
                )}
                {ema.death_cross && (
                  <span className="ml-2 inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium bg-red-100 text-red-800">
                    Death Cross
                  </span>
                )}
              </div>
              <LabelValue label="EMA 9" value={`$${parseFloat(ema.ema_9).toFixed(2)}`} />
              <LabelValue label="EMA 21" value={`$${parseFloat(ema.ema_21).toFixed(2)}`} />
              <LabelValue label="EMA 50" value={`$${parseFloat(ema.ema_50).toFixed(2)}`} />
              <LabelValue label="EMA 200" value={`$${parseFloat(ema.ema_200).toFixed(2)}`} />
              <LabelValue
                label="Price vs EMA 9"
                value={ema.price_vs_ema_9.charAt(0).toUpperCase() + ema.price_vs_ema_9.slice(1)}
              />
              <LabelValue
                label="Price vs EMA 200"
                value={ema.price_vs_ema_200.charAt(0).toUpperCase() + ema.price_vs_ema_200.slice(1)}
              />
            </div>
          )}

          {/* Bollinger Bands */}
          {bollinger && (
            <div className="rounded-md border border-gray-100 p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">Bollinger Bands (20)</span>
                {bollinger.squeeze && (
                  <span className="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium bg-purple-100 text-purple-800">
                    Squeeze
                  </span>
                )}
              </div>
              <LabelValue label="Upper Band" value={`$${parseFloat(bollinger.upper_band).toFixed(2)}`} />
              <LabelValue label="Middle (SMA 20)" value={`$${parseFloat(bollinger.middle_band).toFixed(2)}`} />
              <LabelValue label="Lower Band" value={`$${parseFloat(bollinger.lower_band).toFixed(2)}`} />
              <LabelValue label="Bandwidth" value={parseFloat(bollinger.bandwidth).toFixed(4)} />
            </div>
          )}

          {/* 52-Week Range */}
          {fifty_two_week && (
            <div className="rounded-md border border-gray-100 p-4">
              <div className="text-sm font-medium text-gray-700 mb-2">52-Week Range</div>
              <LabelValue label="52W High" value={`$${parseFloat(fifty_two_week.high).toFixed(2)}`} />
              <LabelValue label="52W Low" value={`$${parseFloat(fifty_two_week.low).toFixed(2)}`} />
              <LabelValue label="Current" value={`$${parseFloat(fifty_two_week.current).toFixed(2)}`} />
              {/* Position bar */}
              <div className="mt-2">
                <div className="flex justify-between text-xs text-gray-400 mb-1">
                  <span>Low</span>
                  <span>{parseFloat(fifty_two_week.position_pct).toFixed(1)}% of range</span>
                  <span>High</span>
                </div>
                <div className="relative h-2 w-full rounded-full bg-gray-200">
                  <div
                    className="absolute top-0 left-0 h-full rounded-full bg-blue-500"
                    style={{ width: `${Math.min(100, Math.max(0, parseFloat(fifty_two_week.position_pct)))}%` }}
                  />
                </div>
              </div>
            </div>
          )}

          {/* Relative Volume */}
          {relative_volume && (
            <div className="rounded-md border border-gray-100 p-4">
              <div className="text-sm font-medium text-gray-700 mb-2">Relative Volume</div>
              <div className="flex items-end gap-2">
                <span className="text-2xl font-bold text-gray-800">
                  {parseFloat(relative_volume.ratio).toFixed(2)}x
                </span>
                <span className={`mb-0.5 text-sm font-medium capitalize ${rvColors[relative_volume.label]}`}>
                  {relative_volume.label}
                </span>
              </div>
              <p className="mt-1 text-xs text-gray-400">
                vs. 20-day average volume
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
