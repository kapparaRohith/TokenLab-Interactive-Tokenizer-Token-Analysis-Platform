import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import VocabularyPanel from '../components/VocabularyPanel';
import type { VocabularyEntry } from '../types/api';

const mockVocab: VocabularyEntry[] = [
  { token_id: 0, token_text: 'Hello', frequency: 1, is_new: true },
  { token_id: 1, token_text: ' world', frequency: 2, is_new: false },
];

describe('VocabularyPanel', () => {
  it('renders null when vocabulary is null', () => {
    const { container } = render(
      <VocabularyPanel vocabulary={null} newTokenIds={null} onReset={vi.fn()} />
    );
    expect(container.firstChild).toBeNull();
  });

  it('renders vocabulary table with NEW and EXISTING badges', () => {
    render(
      <VocabularyPanel vocabulary={mockVocab} newTokenIds={[0]} onReset={vi.fn()} />
    );

    expect(screen.getByText('Custom Vocabulary')).toBeInTheDocument();
    expect(screen.getByText('2 entries')).toBeInTheDocument();

    expect(screen.getByText('NEW')).toBeInTheDocument();
    expect(screen.getByText('EXISTING')).toBeInTheDocument();
  });

  it('calls onReset when Reset Vocabulary button is clicked', () => {
    const handleReset = vi.fn();
    render(
      <VocabularyPanel vocabulary={mockVocab} newTokenIds={[0]} onReset={handleReset} />
    );

    const resetButton = screen.getByRole('button', { name: /reset custom tokenizer vocabulary/i });
    fireEvent.click(resetButton);
    expect(handleReset).toHaveBeenCalledOnce();
  });
});
