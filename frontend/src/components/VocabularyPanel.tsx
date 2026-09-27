import React from 'react';
import type { VocabularyEntry } from '../types/api';

interface VocabularyPanelProps {
  vocabulary: VocabularyEntry[] | null;
  newTokenIds: number[] | null;
  onReset: () => void;
}

const VocabularyPanel: React.FC<VocabularyPanelProps> = ({
  vocabulary,
  onReset,
}) => {
  if (!vocabulary) return null;

  return (
    <div className="glass-panel">
      <div className="panel-header">
        <span className="panel-title">Custom Vocabulary</span>
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          {vocabulary.length > 0 && (
            <span className="badge badge-count">{vocabulary.length} entries</span>
          )}
          <button
            className="btn btn-danger"
            onClick={onReset}
            type="button"
            aria-label="Reset custom tokenizer vocabulary"
            id="reset-vocab-btn"
          >
            Reset Vocabulary
          </button>
        </div>
      </div>

      {vocabulary.length === 0 ? (
        <div className="vocab-empty">
          <p>Vocabulary is empty — tokenize some text to populate it</p>
        </div>
      ) : (
        <div className="vocab-table-wrapper">
          <table className="vocab-table" aria-label="Vocabulary table">
            <thead>
              <tr>
                <th scope="col">ID</th>
                <th scope="col">Token</th>
                <th scope="col">Freq</th>
                <th scope="col">Status</th>
              </tr>
            </thead>
            <tbody>
              {vocabulary.map((entry) => (
                <tr key={entry.token_id}>
                  <td>{entry.token_id}</td>
                  <td>{JSON.stringify(entry.token_text)}</td>
                  <td>{entry.frequency}</td>
                  <td>
                    {entry.is_new ? (
                      <span className="badge badge-new" aria-label="New token">NEW</span>
                    ) : (
                      <span className="badge badge-existing" aria-label="Existing token">EXISTING</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default VocabularyPanel;
