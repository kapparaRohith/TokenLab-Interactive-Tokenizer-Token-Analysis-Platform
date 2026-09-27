/**
 * API service — all backend communication.
 * Uses native fetch only (no axios).
 * All errors are surfaced as ApiError with a .detail string.
 */
import type { TokenizationResult, TokenizerMode } from '../types/api';

const BASE_URL = 'http://localhost:8000';

export class ApiError extends Error {
  detail: string;
  constructor(detail: string) {
    super(detail);
    this.detail = detail;
    this.name = 'ApiError';
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = `Request failed with status ${res.status}`;
    try {
      const body = await res.json();
      if (body?.detail && typeof body.detail === 'string') {
        detail = body.detail;
      }
    } catch {
      // keep default message
    }
    throw new ApiError(detail);
  }
  return res.json() as Promise<T>;
}

export async function fetchEncodings(): Promise<string[]> {
  const res = await fetch(`${BASE_URL}/tokenize/encodings`);
  const data = await handleResponse<{ encodings: string[] }>(res);
  return data.encodings;
}

export async function tokenizeText(
  text: string,
  tokenizer: TokenizerMode,
  encoding?: string,
): Promise<TokenizationResult> {
  const form = new FormData();
  form.append('text', text);
  form.append('tokenizer', tokenizer);
  if (encoding) form.append('encoding', encoding);

  const res = await fetch(`${BASE_URL}/tokenize/text`, { method: 'POST', body: form });
  return handleResponse<TokenizationResult>(res);
}

export async function tokenizeFile(
  file: File,
  tokenizer: TokenizerMode,
  encoding?: string,
): Promise<TokenizationResult> {
  const form = new FormData();
  form.append('file', file);
  form.append('tokenizer', tokenizer);
  if (encoding) form.append('encoding', encoding);

  const res = await fetch(`${BASE_URL}/tokenize/file`, { method: 'POST', body: form });
  return handleResponse<TokenizationResult>(res);
}

export async function resetVocabulary(): Promise<void> {
  const res = await fetch(`${BASE_URL}/tokenize/custom/reset`, { method: 'POST' });
  await handleResponse<{ message: string }>(res);
}
