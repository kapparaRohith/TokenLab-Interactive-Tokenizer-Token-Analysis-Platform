import React from 'react';
import type { TokenizerMode } from '../types/api';

interface TokenizerControlsProps {
  tokenizerMode: TokenizerMode;
  onModeChange: (mode: TokenizerMode) => void;
  availableEncodings: string[];
  selectedEncoding: string;
  onEncodingChange: (enc: string) => void;
}

const TokenizerControls: React.FC<TokenizerControlsProps> = ({
  tokenizerMode,
  onModeChange,
  availableEncodings,
  selectedEncoding,
  onEncodingChange,
}) => {
  return (
    <div className="glass-panel">
      <div className="panel-header">
        <span className="panel-title">Tokenizer</span>
      </div>

      <div className="form-group">
        <label>Mode</label>
        <div className="mode-toggle" role="group" aria-label="Tokenizer mode selection">
          <button
            className={`mode-btn${tokenizerMode === 'tiktoken' ? ' mode-btn--active' : ''}`}
            onClick={() => onModeChange('tiktoken')}
            type="button"
            aria-pressed={tokenizerMode === 'tiktoken'}
            aria-label="Tiktoken tokenizer mode"
            id="mode-tiktoken"
          >
            Tiktoken
          </button>
          <button
            className={`mode-btn${tokenizerMode === 'custom' ? ' mode-btn--active' : ''}`}
            onClick={() => onModeChange('custom')}
            type="button"
            aria-pressed={tokenizerMode === 'custom'}
            aria-label="Custom tokenizer mode"
            id="mode-custom"
          >
            Custom
          </button>
        </div>
      </div>

      {tokenizerMode === 'tiktoken' && (
        <div className="form-group encoding-group">
          <label htmlFor="encoding-select">Encoding</label>
          <select
            id="encoding-select"
            value={selectedEncoding}
            onChange={(e) => onEncodingChange(e.target.value)}
            aria-label="Tiktoken encoding selection"
          >
            {availableEncodings.map((enc) => (
              <option key={enc} value={enc}>
                {enc}
              </option>
            ))}
          </select>
        </div>
      )}

      {tokenizerMode === 'custom' && (
        <p style={{ color: 'rgba(255,255,255,0.35)', fontSize: '0.8rem', marginTop: '0.5rem' }}>
          Uses regex-based deterministic splitting with in-memory vocabulary management.
        </p>
      )}
    </div>
  );
};

export default TokenizerControls;
