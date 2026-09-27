import React from 'react';
import type { Token } from '../types/api';

interface TokenTableProps {
  tokens: Token[];
}

const TokenTable: React.FC<TokenTableProps> = ({ tokens }) => {
  return (
    <div className="glass-panel">
      <div className="panel-header">
        <span className="panel-title">Tokens</span>
        {tokens.length > 0 && (
          <span className="badge badge-count">{tokens.length} tokens</span>
        )}
      </div>

      {tokens.length === 0 ? (
        <div className="token-table-empty">
          <p>No tokens to display yet</p>
        </div>
      ) : (
        <div className="token-table-wrapper">
          <table className="token-table" aria-label="Token table">
            <thead>
              <tr>
                <th scope="col">Index</th>
                <th scope="col">Token ID</th>
                <th scope="col">Token Text</th>
              </tr>
            </thead>
            <tbody>
              {tokens.map((token) => (
                <tr key={token.index}>
                  <td>{token.index}</td>
                  <td>{token.token_id}</td>
                  <td>{JSON.stringify(token.token_text)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default TokenTable;
