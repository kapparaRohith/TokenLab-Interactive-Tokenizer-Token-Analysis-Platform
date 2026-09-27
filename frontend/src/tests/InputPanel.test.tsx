import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import InputPanel from '../components/InputPanel';

describe('InputPanel', () => {
  it('renders mode tabs and textarea in text mode', () => {
    render(
      <InputPanel
        inputMode="text"
        onInputModeChange={vi.fn()}
        textInput="Hello world"
        onTextChange={vi.fn()}
        uploadedFile={null}
        onFileChange={vi.fn()}
        onValidationError={vi.fn()}
      />
    );

    expect(screen.getByText('Text')).toBeInTheDocument();
    expect(screen.getByText('TXT File')).toBeInTheDocument();
    expect(screen.getByText('PDF File')).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Type or paste text here to tokenize/i)).toBeInTheDocument();
  });

  it('calls onValidationError when wrong file extension is selected in TXT mode', () => {
    const handleValidationError = vi.fn();
    render(
      <InputPanel
        inputMode="txt"
        onInputModeChange={vi.fn()}
        textInput=""
        onTextChange={vi.fn()}
        uploadedFile={null}
        onFileChange={vi.fn()}
        onValidationError={handleValidationError}
      />
    );

    const fileInput = screen.getByLabelText(/TXT file upload/i);
    const invalidFile = new File(['content'], 'document.pdf', { type: 'application/pdf' });

    fireEvent.change(fileInput, { target: { files: [invalidFile] } });
    expect(handleValidationError).toHaveBeenCalledWith('Please select a .txt file.');
  });
});
