import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import TokenTable from '../components/TokenTable';
import type { Token } from '../types/api';

const mockTokens: Token[] = [
  { index: 0, token_id: 15339, token_text: 'Hello' },
  { index: 1, token_id: 1917, token_text: ' world' },
];

describe('TokenTable', () => {
  it('renders empty state when tokens array is empty', () => {
    render(<TokenTable tokens={[]} />);
    expect(screen.getByText(/No tokens to display yet/i)).toBeInTheDocument();
  });

  it('renders table headers and rows matching tokens length', () => {
    render(<TokenTable tokens={mockTokens} />);
    expect(screen.getByText('Index')).toBeInTheDocument();
    expect(screen.getByText('Token ID')).toBeInTheDocument();
    expect(screen.getByText('Token Text')).toBeInTheDocument();

    expect(screen.getByText('15339')).toBeInTheDocument();
    expect(screen.getByText('1917')).toBeInTheDocument();
    expect(screen.getByText('2 tokens')).toBeInTheDocument();
  });
});
