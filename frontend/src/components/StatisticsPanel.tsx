import React from 'react';
import type { TokenizationResult } from '../types/api';

interface StatisticsPanelProps {
  result: TokenizationResult | null;
}

const stats = [
  { key: 'char_count' as const, label: 'Characters', format: (v: number) => v.toLocaleString() },
  { key: 'word_count' as const, label: 'Words', format: (v: number) => v.toLocaleString() },
  { key: 'token_count' as const, label: 'Tokens', format: (v: number) => v.toLocaleString() },
  { key: 'tokens_per_word' as const, label: 'Tokens / Word', format: (v: number) => v.toFixed(4) },
  { key: 'tokens_per_char' as const, label: 'Tokens / Char', format: (v: number) => v.toFixed(4) },
];

const StatisticsPanel: React.FC<StatisticsPanelProps> = ({ result }) => {
  return (
    <div className="glass-panel">
      <div className="panel-header">
        <span className="panel-title">Statistics</span>
        {result && (
          <span className="badge badge-count">
            {result.tokenizer === 'tiktoken' ? result.encoding : 'Custom'}
          </span>
        )}
      </div>

      {result ? (
        <div className="stats-grid" aria-label="Tokenization statistics">
          {stats.map(({ key, label, format }) => (
            <div className="stat-card" key={key}>
              <span className="stat-value">{format(result[key] as number)}</span>
              <span className="stat-label">{label}</span>
            </div>
          ))}
        </div>
      ) : (
        <div className="stats-empty">
          <p>Tokenize some text to see statistics</p>
        </div>
      )}
    </div>
  );
};

export default StatisticsPanel;
