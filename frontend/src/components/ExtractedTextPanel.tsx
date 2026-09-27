import React, { useState } from 'react';
import type { SourceType } from '../types/api';

interface ExtractedTextPanelProps {
  text: string | null;
  sourceType: SourceType | null;
}

const ExtractedTextPanel: React.FC<ExtractedTextPanelProps> = ({ text, sourceType }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);

  if (!text || (sourceType !== 'txt' && sourceType !== 'pdf')) {
    return null;
  }

  return (
    <div className="glass-panel" style={{ marginTop: '1.5rem' }}>
      <div className="panel-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <h2 style={{ fontSize: '1.1rem', margin: 0 }}>Extracted Text</h2>
          <span className="badge-existing" style={{ textTransform: 'uppercase', fontSize: '0.75rem' }}>
            {sourceType}
          </span>
        </div>
        <button
          type="button"
          className="btn-secondary"
          onClick={() => setIsCollapsed(!isCollapsed)}
          aria-expanded={!isCollapsed}
          aria-label={isCollapsed ? 'Expand extracted text' : 'Collapse extracted text'}
          style={{ padding: '0.25rem 0.75rem', fontSize: '0.85rem' }}
        >
          {isCollapsed ? 'Show ▼' : 'Hide ▲'}
        </button>
      </div>

      {!isCollapsed && (
        <pre
          style={{
            fontFamily: 'var(--font-mono)',
            fontSize: '0.9rem',
            lineHeight: '1.5',
            backgroundColor: 'rgba(0, 0, 0, 0.3)',
            padding: '1rem',
            borderRadius: 'var(--radius-md)',
            border: '1px solid rgba(255, 255, 255, 0.05)',
            maxHeight: '250px',
            overflowY: 'auto',
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word',
            color: 'var(--text-secondary)',
            marginTop: '1rem',
          }}
        >
          {text}
        </pre>
      )}
    </div>
  );
};

export default ExtractedTextPanel;
