// TypeScript interfaces matching the API contract exactly.
// Source of truth: specs/001-tokenizer-app/contracts/api-contract.md

export type TokenizerMode = 'tiktoken' | 'custom';
export type SourceType = 'text' | 'txt' | 'pdf';

export interface Token {
  index: number;
  token_id: number;
  token_text: string;
}

export interface VocabularyEntry {
  token_id: number;
  token_text: string;
  frequency: number;
  is_new: boolean;
}

export interface TokenizationResult {
  original_text: string;
  source_type: SourceType;
  tokenizer: TokenizerMode;
  encoding: string;
  token_count: number;
  tokens: Token[];
  token_ids: number[];
  token_texts: string[];
  char_count: number;
  word_count: number;
  tokens_per_word: number;
  tokens_per_char: number;
  vocabulary: VocabularyEntry[] | null;
  new_token_ids: number[] | null;
}

export interface EncodingsResponse {
  encodings: string[];
}

export interface ResetResponse {
  message: string;
}

export interface ApiError extends Error {
  detail: string;
}
