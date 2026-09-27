import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import StatisticsPanel from '../components/StatisticsPanel';
import type { TokenizationResult } from '../types/api';

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

describe('StatisticsPanel', () => {
  it('renders empty state when result is null', () => {
    render(<StatisticsPanel result={null} />);
    expect(screen.getByText(/Tokenize some text to see statistics/i)).toBeInTheDocument();
  });

  it('renders all 5 stat cards with formatted values when result is provided', () => {
    render(<StatisticsPanel result={mockResult} />);
    expect(screen.getByText('Characters')).toBeInTheDocument();
    expect(screen.getByText('11')).toBeInTheDocument();

    expect(screen.getByText('Words')).toBeInTheDocument();
    expect(screen.getAllByText('2').length).toBeGreaterThanOrEqual(1);

    expect(screen.getByText('Tokens')).toBeInTheDocument();

    expect(screen.getByText('Tokens / Word')).toBeInTheDocument();
    expect(screen.getByText('1.0000')).toBeInTheDocument();

    expect(screen.getByText('Tokens / Char')).toBeInTheDocument();
    expect(screen.getByText('0.1818')).toBeInTheDocument();
  });
});
