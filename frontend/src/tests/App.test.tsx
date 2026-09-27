import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import App from '../App';
import * as apiService from '../services/api';
import type { TokenizationResult } from '../types/api';

vi.mock('../services/api');

const mockEncodings = ['cl100k_base', 'p50k_base'];
const mockResult: TokenizationResult = {
  original_text: 'Hello world',
  source_type: 'text',
  tokenizer: 'tiktoken',
  encoding: 'cl100k_base',
  token_count: 2,
  tokens: [
    { index: 0, token_id: 15339, token_text: 'Hello' },
    { index: 1, token_id: 1917, token_text: ' world' },
  ],
  token_ids: [15339, 1917],
  token_texts: ['Hello', ' world'],
  char_count: 11,
  word_count: 2,
  tokens_per_word: 1.0,
  tokens_per_char: 0.1818,
  vocabulary: null,
  new_token_ids: null,
};

describe('App Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(apiService.fetchEncodings).mockResolvedValue(mockEncodings);
    vi.mocked(apiService.tokenizeText).mockResolvedValue(mockResult);
  });

  it('fetches encodings on mount and populates select options', async () => {
    render(<App />);
    await waitFor(() => {
      expect(apiService.fetchEncodings).toHaveBeenCalled();
    });
    expect(screen.getByRole('combobox', { name: /tiktoken encoding selection/i })).toBeInTheDocument();
  });

  it('dispatches tokenizeText when Tokenize button is clicked with non-empty text', async () => {
    render(<App />);

    const textarea = screen.getByPlaceholderText(/Type or paste text here to tokenize/i);
    fireEvent.change(textarea, { target: { value: 'Hello world' } });

    const button = screen.getByRole('button', { name: /tokenize input/i });
    fireEvent.click(button);

    await waitFor(() => {
      expect(apiService.tokenizeText).toHaveBeenCalledWith('Hello world', 'tiktoken', 'cl100k_base');
    });

    expect(screen.getByText('15339')).toBeInTheDocument();
  });

  it('shows error message if empty input is submitted without making API call', async () => {
    render(<App />);

    const button = screen.getByRole('button', { name: /tokenize input/i });
    fireEvent.click(button);

    expect(apiService.tokenizeText).not.toHaveBeenCalled();
    expect(screen.getByText('Input text cannot be empty.')).toBeInTheDocument();
  });
});
