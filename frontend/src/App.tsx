import React, { useEffect, useState } from 'react';
import ErrorMessage from './components/ErrorMessage';
import ExtractedTextPanel from './components/ExtractedTextPanel';
import InputPanel from './components/InputPanel';
import StatisticsPanel from './components/StatisticsPanel';
import TokenTable from './components/TokenTable';
import TokenizeButton from './components/TokenizeButton';
import TokenizerControls from './components/TokenizerControls';
import VocabularyPanel from './components/VocabularyPanel';
import { fetchEncodings, resetVocabulary, tokenizeFile, tokenizeText } from './services/api';
import type { TokenizationResult, TokenizerMode } from './types/api';

type InputMode = 'text' | 'txt' | 'pdf';

const App: React.FC = () => {
  const [inputMode, setInputMode] = useState<InputMode>('text');
  const [textInput, setTextInput] = useState<string>('');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [tokenizerMode, setTokenizerMode] = useState<TokenizerMode>('tiktoken');
  const [selectedEncoding, setSelectedEncoding] = useState<string>('cl100k_base');
  const [availableEncodings, setAvailableEncodings] = useState<string[]>([]);
  const [result, setResult] = useState<TokenizationResult | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch encodings on mount
  useEffect(() => {
    fetchEncodings()
      .then((encodings) => {
        setAvailableEncodings(encodings);
        if (encodings.length > 0) {
          setSelectedEncoding(encodings[0]);
        }
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : 'Failed to fetch available encodings');
      });
  }, []);

  const handleInputModeChange = (mode: InputMode) => {
    setInputMode(mode);
    setUploadedFile(null);
    setResult(null);
    setError(null);
  };

  const handleTokenizerModeChange = (mode: TokenizerMode) => {
    setTokenizerMode(mode);
    setResult(null);
    setError(null);
  };

  const handleTokenize = async () => {
    setError(null);

    // Client-side validation
    if (inputMode === 'text') {
      if (!textInput.trim()) {
        setError('Input text cannot be empty.');
        return;
      }
    } else if (inputMode === 'txt') {
      if (!uploadedFile) {
        setError('Please select a .txt file to upload.');
        return;
      }
      if (!uploadedFile.name.toLowerCase().endsWith('.txt')) {
        setError('Please select a .txt file.');
        return;
      }
    } else if (inputMode === 'pdf') {
      if (!uploadedFile) {
        setError('Please select a .pdf file to upload.');
        return;
      }
      if (!uploadedFile.name.toLowerCase().endsWith('.pdf')) {
        setError('Please select a .pdf file.');
        return;
      }
    }

    setIsLoading(true);
    try {
      let res: TokenizationResult;
      if (inputMode === 'text') {
        res = await tokenizeText(textInput, tokenizerMode, tokenizerMode === 'tiktoken' ? selectedEncoding : undefined);
      } else {
        res = await tokenizeFile(uploadedFile!, tokenizerMode, tokenizerMode === 'tiktoken' ? selectedEncoding : undefined);
      }
      setResult(res);
    } catch (err: any) {
      setError(err.detail || err.message || 'An error occurred during tokenization');
    } finally {
      setIsLoading(false);
    }
  };

  const handleResetVocab = async () => {
    setError(null);
    try {
      await resetVocabulary();
      setResult(null);
    } catch (err: any) {
      setError(err.detail || err.message || 'Failed to reset vocabulary');
    }
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem 1.5rem' }}>
      <header style={{ marginBottom: '2rem', textAlign: 'center' }}>
        <h1
          style={{
            fontSize: '2.5rem',
            fontWeight: 700,
            background: 'var(--gradient-primary)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            marginBottom: '0.5rem',
          }}
        >
          Tokenizer Studio
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1rem', maxWidth: '600px', margin: '0 auto' }}>
          Visualize text tokenization using authoritative OpenAI Tiktoken encodings or an interactive Custom Tokenizer with dynamic vocabulary management.
        </p>
      </header>

      <main style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        <InputPanel
          inputMode={inputMode}
          onInputModeChange={handleInputModeChange}
          textInput={textInput}
          onTextChange={setTextInput}
          uploadedFile={uploadedFile}
          onFileChange={setUploadedFile}
          onValidationError={(msg) => setError(msg)}
        />

        <TokenizerControls
          tokenizerMode={tokenizerMode}
          onModeChange={handleTokenizerModeChange}
          availableEncodings={availableEncodings}
          selectedEncoding={selectedEncoding}
          onEncodingChange={setSelectedEncoding}
        />

        <TokenizeButton
          isLoading={isLoading}
          onClick={handleTokenize}
          disabled={isLoading}
        />

        <ErrorMessage error={error} onDismiss={() => setError(null)} />

        <ExtractedTextPanel text={result?.original_text ?? null} sourceType={result?.source_type ?? null} />

        <StatisticsPanel result={result} />

        {tokenizerMode === 'custom' && (
          <VocabularyPanel
            vocabulary={result?.vocabulary ?? null}
            newTokenIds={result?.new_token_ids ?? null}
            onReset={handleResetVocab}
          />
        )}

        <TokenTable tokens={result?.tokens ?? []} />
      </main>
    </div>
  );
};

export default App;
