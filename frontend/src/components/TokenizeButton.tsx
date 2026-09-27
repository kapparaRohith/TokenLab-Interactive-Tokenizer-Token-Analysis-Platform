import React from 'react';

interface TokenizeButtonProps {
  isLoading: boolean;
  onClick: () => void;
  disabled: boolean;
}

const TokenizeButton: React.FC<TokenizeButtonProps> = ({ isLoading, onClick, disabled }) => {
  return (
    <button
      className="btn btn-primary"
      onClick={onClick}
      disabled={disabled || isLoading}
      aria-label={isLoading ? 'Tokenizing, please wait' : 'Tokenize input'}
      aria-busy={isLoading}
      type="button"
      id="tokenize-btn"
    >
      {isLoading ? (
        <>
          <div className="spinner" aria-hidden="true" />
          Tokenizing...
        </>
      ) : (
        '⚡ Tokenize'
      )}
    </button>
  );
};

export default TokenizeButton;
