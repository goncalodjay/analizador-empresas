'use client';
import type { StrategyRules } from '@/lib/types';

interface StrategyRulesEditorProps {
  value: StrategyRules;
  onChange: (rules: StrategyRules) => void;
}

function setNumeric(
  rules: StrategyRules,
  key: keyof StrategyRules,
  raw: string,
): StrategyRules {
  const next = { ...rules };
  if (raw === '') {
    delete next[key];
  } else {
    // Store as string to match backend Decimal serialization
    (next as Record<string, unknown>)[key] = raw;
  }
  return next;
}

function setBoolean(
  rules: StrategyRules,
  key: keyof StrategyRules,
  checked: boolean | undefined,
): StrategyRules {
  const next = { ...rules };
  if (checked === undefined) {
    delete next[key];
  } else {
    (next as Record<string, unknown>)[key] = checked;
  }
  return next;
}

export function StrategyRulesEditor({ value, onChange }: StrategyRulesEditorProps) {
  const numericInput = (
    label: string,
    key: keyof StrategyRules,
    placeholder?: string,
  ) => (
    <div key={key} className="flex flex-col gap-1">
      <label className="text-xs font-medium text-gray-700">{label}</label>
      <input
        type="number"
        step="any"
        placeholder={placeholder ?? 'Leave blank to skip'}
        value={(value[key] as string | undefined) ?? ''}
        onChange={(e) => onChange(setNumeric(value, key, e.target.value))}
        className="rounded-md border border-gray-300 px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
    </div>
  );

  const checkboxInput = (label: string, key: 'ema_crossover' | 'macd_bullish') => (
    <div key={key} className="flex items-center gap-2">
      <input
        id={key}
        type="checkbox"
        checked={(value[key] as boolean | undefined) ?? false}
        onChange={(e) => {
          // If unchecked and was previously unset, keep unset; otherwise set to bool
          const prev = value[key] as boolean | undefined;
          if (!e.target.checked && prev === undefined) {
            // was never set — leave as undefined
            onChange(setBoolean(value, key, undefined));
          } else {
            onChange(setBoolean(value, key, e.target.checked));
          }
        }}
        className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
      />
      <label htmlFor={key} className="text-sm text-gray-700">
        {label}
      </label>
    </div>
  );

  return (
    <div className="space-y-4">
      <div>
        <h4 className="mb-2 text-sm font-semibold text-gray-900">Fundamental</h4>
        <div className="grid grid-cols-2 gap-3">
          {numericInput('Max P/E', 'max_pe', 'e.g. 30')}
          {numericInput('Min ROE (%)', 'min_roe', 'e.g. 15')}
          {numericInput('Min Dividend Yield (%)', 'min_dividend_yield', 'e.g. 2')}
          {numericInput('Max Debt/Equity', 'max_debt_to_equity', 'e.g. 1.5')}
          {numericInput('Min Revenue Growth (%)', 'min_revenue_growth', 'e.g. 10')}
        </div>
      </div>

      <div>
        <h4 className="mb-2 text-sm font-semibold text-gray-900">Technical</h4>
        <div className="grid grid-cols-2 gap-3">
          {numericInput('RSI Entry Max', 'rsi_entry_max', 'e.g. 70')}
          {numericInput('RSI Exit Min', 'rsi_exit_min', 'e.g. 30')}
        </div>
        <div className="mt-3 space-y-2">
          {checkboxInput('Require EMA crossover (golden cross)', 'ema_crossover')}
          {checkboxInput('Require bullish MACD', 'macd_bullish')}
        </div>
      </div>

      <div>
        <h4 className="mb-2 text-sm font-semibold text-gray-900">Risk</h4>
        <div className="grid grid-cols-3 gap-3">
          {numericInput('Max Position (%)', 'max_position_pct', 'e.g. 10')}
          {numericInput('Stop Loss (%)', 'stop_loss_pct', 'e.g. 5')}
          {numericInput('Take Profit (%)', 'take_profit_pct', 'e.g. 20')}
        </div>
      </div>
    </div>
  );
}
