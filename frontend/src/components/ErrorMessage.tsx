import React from 'react';

interface ErrorMessageProps {
  error: string | null;
  onDismiss: () => void;
}

const ErrorMessage: React.FC<ErrorMessageProps> = ({ error, onDismiss }) => {
  if (!error) return null;
  return (
    <div
      className="error-message"
      role="status"
      aria-live="polite"
      aria-atomic="true"
    >
      <p>{error}</p>
      <button
        className="btn btn-icon"
        onClick={onDismiss}
        aria-label="Dismiss error message"
        type="button"
      >
        ✕
      </button>
    </div>
  );
};

export default ErrorMessage;
