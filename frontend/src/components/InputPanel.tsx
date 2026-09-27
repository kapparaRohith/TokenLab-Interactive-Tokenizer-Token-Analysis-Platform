import React, { useRef } from 'react';

type InputMode = 'text' | 'txt' | 'pdf';

interface InputPanelProps {
  inputMode: InputMode;
  onInputModeChange: (mode: InputMode) => void;
  textInput: string;
  onTextChange: (text: string) => void;
  onFileChange: (file: File) => void;
  uploadedFile: File | null;
  onValidationError: (msg: string) => void;
}

const InputPanel: React.FC<InputPanelProps> = ({
  inputMode,
  onInputModeChange,
  textInput,
  onTextChange,
  onFileChange,
  uploadedFile,
  onValidationError,
}) => {
  const txtRef = useRef<HTMLInputElement>(null);
  const pdfRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>, expectedExt: string) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!file.name.toLowerCase().endsWith(expectedExt)) {
      onValidationError(`Please select a ${expectedExt} file.`);
      e.target.value = '';
      return;
    }
    onFileChange(file);
  };

  return (
    <div className="glass-panel">
      <div className="panel-header">
        <span className="panel-title">Input</span>
      </div>

      {/* Mode tabs */}
      <div className="tabs" role="tablist" aria-label="Input mode">
        {(['text', 'txt', 'pdf'] as InputMode[]).map((mode) => (
          <button
            key={mode}
            className={`tab-btn${inputMode === mode ? ' tab-btn--active' : ''}`}
            onClick={() => onInputModeChange(mode)}
            role="tab"
            aria-selected={inputMode === mode}
            aria-label={`${mode.toUpperCase()} input mode`}
            type="button"
            id={`tab-${mode}`}
          >
            {mode === 'text' ? 'Text' : mode === 'txt' ? 'TXT File' : 'PDF File'}
          </button>
        ))}
      </div>

      {/* Text mode */}
      {inputMode === 'text' && (
        <div className="form-group">
          <label htmlFor="text-input">Enter or paste text</label>
          <textarea
            id="text-input"
            value={textInput}
            onChange={(e) => onTextChange(e.target.value)}
            placeholder="Type or paste text here to tokenize..."
            aria-label="Text input for tokenization"
            rows={6}
          />
        </div>
      )}

      {/* TXT upload mode */}
      {inputMode === 'txt' && (
        <div className="form-group">
          <label htmlFor="txt-file-input">Upload a .txt file</label>
          <div
            className={`file-drop-area${uploadedFile ? ' has-file' : ''}`}
            onClick={() => txtRef.current?.click()}
            role="button"
            tabIndex={0}
            aria-label="Click to select a TXT file"
            onKeyDown={(e) => e.key === 'Enter' && txtRef.current?.click()}
          >
            <input
              ref={txtRef}
              id="txt-file-input"
              type="file"
              accept=".txt"
              onChange={(e) => handleFileSelect(e, '.txt')}
              aria-label="TXT file upload"
            />
            {uploadedFile ? (
              <>
                <p className="file-drop-text">✓ File selected</p>
                <p className="file-name">{uploadedFile.name}</p>
              </>
            ) : (
              <p className="file-drop-text">
                Drop a file here or <span>click to browse</span>
              </p>
            )}
          </div>
        </div>
      )}

      {/* PDF upload mode */}
      {inputMode === 'pdf' && (
        <div className="form-group">
          <label htmlFor="pdf-file-input">Upload a .pdf file</label>
          <div
            className={`file-drop-area${uploadedFile ? ' has-file' : ''}`}
            onClick={() => pdfRef.current?.click()}
            role="button"
            tabIndex={0}
            aria-label="Click to select a PDF file"
            onKeyDown={(e) => e.key === 'Enter' && pdfRef.current?.click()}
          >
            <input
              ref={pdfRef}
              id="pdf-file-input"
              type="file"
              accept=".pdf"
              onChange={(e) => handleFileSelect(e, '.pdf')}
              aria-label="PDF file upload"
            />
            {uploadedFile ? (
              <>
                <p className="file-drop-text">✓ File selected</p>
                <p className="file-name">{uploadedFile.name}</p>
              </>
            ) : (
              <p className="file-drop-text">
                Drop a file here or <span>click to browse</span>
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default InputPanel;
