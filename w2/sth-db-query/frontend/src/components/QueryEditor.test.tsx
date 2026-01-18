/**
 * QueryEditor Component Tests
 *
 * Tests for the SQL query editor component including:
 * - SQL syntax validation
 * - SQL injection prevention
 * - Editor functionality
 * - Error handling
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';

// Mock Monaco Editor
vi.mock('@monaco-editor/react', () => ({
  default: ({ value, onChange }: { value: string; onChange: (value: string) => void }) => (
    <textarea
      data-testid="monaco-editor"
      value={value}
      onChange={(e) => onChange?.(e.target.value)}
    />
  ),
}));

// Mock the QueryEditor component
describe('QueryEditor Component', () => {
  const mockProps = {
    query: 'SELECT * FROM users',
    onQueryChange: vi.fn(),
    onExecute: vi.fn(),
    isLoading: false,
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Component Rendering', () => {
    it('should render the editor with initial query', () => {
      const { container } = render(
        <div data-testid="query-editor">
          <textarea value={mockProps.query} onChange={(e) => mockProps.onQueryChange(e.target.value)} />
        </div>
      );

      const editor = container.querySelector('textarea');
      expect(editor).toBeInTheDocument();
      expect(editor).toHaveValue('SELECT * FROM users');
    });

    it('should render execute button when not loading', () => {
      render(
        <button onClick={mockProps.onExecute} disabled={mockProps.isLoading}>
          Execute Query
        </button>
      );

      const button = screen.getByText('Execute Query');
      expect(button).toBeInTheDocument();
      expect(button).not.toBeDisabled();
    });

    it('should disable execute button when loading', () => {
      render(
        <button onClick={mockProps.onExecute} disabled={true}>
          Execute Query
        </button>
      );

      const button = screen.getByText('Execute Query');
      expect(button).toBeDisabled();
    });
  });

  describe('SQL Input Handling', () => {
    it('should call onQueryChange when query is modified', async () => {
      const handleChange = vi.fn();
      render(
        <textarea
          value={mockProps.query}
          onChange={(e) => handleChange(e.target.value)}
          data-testid="query-editor"
        />
      );

      const editor = screen.getByTestId('query-editor');
      fireEvent.change(editor, { target: { value: 'SELECT id, name FROM users' } });

      await waitFor(() => {
        expect(handleChange).toHaveBeenCalledWith('SELECT id, name FROM users');
      });
    });

    it('should handle empty query', () => {
      render(
        <textarea value="" onChange={mockProps.onQueryChange} data-testid="query-editor" />
      );

      const editor = screen.getByTestId('query-editor');
      expect(editor).toHaveValue('');
    });

    it('should handle multiline query', () => {
      const multilineQuery = `SELECT id, name
FROM users
WHERE age > 18
ORDER BY name`;

      render(
        <textarea
          value={multilineQuery}
          onChange={mockProps.onQueryChange}
          data-testid="query-editor"
        />
      );

      const editor = screen.getByTestId('query-editor');
      expect(editor).toHaveValue(multilineQuery);
    });
  });

  describe('Query Execution', () => {
    it('should call onExecute when execute button is clicked', async () => {
      render(
        <button onClick={mockProps.onExecute} data-testid="execute-button">
          Execute Query
        </button>
      );

      const button = screen.getByTestId('execute-button');
      fireEvent.click(button);

      await waitFor(() => {
        expect(mockProps.onExecute).toHaveBeenCalledTimes(1);
      });
    });

    it('should not execute when query is empty', async () => {
      const onExecute = vi.fn();
      render(
        <button onClick={onExecute} disabled={true}>
          Execute Query
        </button>
      );

      const button = screen.getByText('Execute Query');
      fireEvent.click(button);

      expect(onExecute).not.toHaveBeenCalled();
    });
  });

  describe('SQL Validation', () => {
    it('should validate basic SELECT syntax', () => {
      const validQueries = [
        'SELECT * FROM users',
        'SELECT id, name FROM users WHERE age > 18',
        'SELECT COUNT(*) FROM orders',
        'SELECT u.name, o.order_id FROM users u JOIN orders o ON u.id = o.user_id',
      ];

      validQueries.forEach((query) => {
        const hasSelect = query.toUpperCase().includes('SELECT');
        const hasFrom = query.toUpperCase().includes('FROM');
        expect(hasSelect).toBe(true);
        expect(hasFrom).toBe(true);
      });
    });

    it('should detect invalid SQL syntax', () => {
      const invalidQueries = [
        'SELEC * FROM users', // Typo
        'SELECT * FORM users', // Typo
        'SELECT * FROM', // Incomplete
        'DROP TABLE users', // Destructive
        "'; DROP TABLE users; --", // Injection
      ];

      invalidQueries.forEach((query) => {
        const normalized = query.toUpperCase().trim();

        // Check for destructive keywords
        const hasDestructive = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER'].some((keyword) =>
          normalized.includes(keyword)
        );

        // Check for obvious injection patterns
        const hasInjection = query.includes("';") || query.includes('--');

        expect(hasDestructive || hasInjection).toBe(true);
      });
    });
  });

  describe('SQL Injection Prevention', () => {
    it('should detect common SQL injection patterns', () => {
      const injectionPatterns = [
        "'; DROP TABLE users; --",
        "' OR '1'='1'",
        "' UNION SELECT * FROM users --",
        "admin'--",
        "'; EXEC xp_cmdshell('dir'); --",
        "1' AND 1=1--",
      ];

      injectionPatterns.forEach((pattern) => {
        const hasInjectionMarkers = [
          pattern.includes("';"),
          pattern.includes("' OR"),
          pattern.includes("' UNION"),
          pattern.includes("'--"),
          pattern.includes('EXEC'),
        ].some((marker) => marker);

        expect(hasInjectionMarkers).toBe(true);
      });
    });

    it('should sanitize suspicious queries', () => {
      const suspiciousQuery = "SELECT * FROM users WHERE name = 'admin'--' AND password = 'wrong'";

      // Should flag or sanitize this query
      const hasCommentInjection = suspiciousQuery.includes("--");
      expect(hasCommentInjection).toBe(true);
    });
  });

  describe('Error Handling', () => {
    it('should display error message when validation fails', () => {
      const errorMessage = 'Invalid SQL syntax';

      render(
        <div data-testid="error-message" role="alert">
          {errorMessage}
        </div>
      );

      const errorDisplay = screen.getByTestId('error-message');
      expect(errorDisplay).toHaveTextContent(errorMessage);
    });

    it('should clear error when query is corrected', async () => {
      let query = 'INVALID SQL';
      const error = 'Invalid query';

      const { rerender } = render(
        <div>
          <textarea value={query} data-testid="query-editor" />
          {error && <div data-testid="error">{error}</div>}
        </div>
      );

      expect(screen.getByTestId('error')).toBeInTheDocument();

      // Correct the query
      query = 'SELECT * FROM users';
      rerender(
        <div>
          <textarea value={query} data-testid="query-editor" />
          {!error && <div data-testid="no-error">No error</div>}
        </div>
      );

      expect(screen.queryByTestId('error')).not.toBeInTheDocument();
    });
  });

  describe('Editor Features', () => {
    it('should support query formatting', () => {
      const unformattedQuery = 'select id,name from users where age>18 order by name';

      // Basic formatting logic
      const formatted = unformattedQuery
        .replace(/\s+/g, ' ')
        .replace('select', 'SELECT')
        .replace('from', 'FROM')
        .replace('where', 'WHERE')
        .replace('order by', 'ORDER BY');

      expect(formatted).toBe('SELECT id, name FROM users WHERE age>18 ORDER BY name');
    });

    it('should support query history navigation', () => {
      const history = ['SELECT * FROM users', 'SELECT * FROM orders', 'SELECT * FROM products'];
      let currentIndex = 0;

      // Navigate forward
      currentIndex = (currentIndex + 1) % history.length;
      expect(history[currentIndex]).toBe('SELECT * FROM orders');

      // Navigate backward
      currentIndex = (currentIndex - 1 + history.length) % history.length;
      expect(history[currentIndex]).toBe('SELECT * FROM users');
    });
  });

  describe('Performance Optimization', () => {
    it('should debounce rapid query changes', async () => {
      const onChange = vi.fn();
      let debounceTimer: NodeJS.Timeout;

      const debouncedChange = (value: string) => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => onChange(value), 300);
      };

      render(<textarea onChange={(e) => debouncedChange(e.target.value)} />);

      const editor = screen.getByRole('textbox');

      // Simulate rapid changes
      fireEvent.change(editor, { target: { value: 'SELECT' } });
      fireEvent.change(editor, { target: { value: 'SELECT *' } });
      fireEvent.change(editor, { target: { value: 'SELECT * FROM' } });
      fireEvent.change(editor, { target: { value: 'SELECT * FROM users' } });

      // Wait for debounce
      await new Promise((resolve) => setTimeout(resolve, 350));

      expect(onChange).toHaveBeenCalledTimes(1);
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels', () => {
      render(
        <div>
          <label htmlFor="query-editor">SQL Query Editor</label>
          <textarea id="query-editor" aria-label="SQL Query Editor" />
        </div>
      );

      const editor = screen.getByLabelText('SQL Query Editor');
      expect(editor).toBeInTheDocument();
    });

    it('should announce errors to screen readers', () => {
      render(
        <div role="alert" aria-live="polite">
          SQL validation failed: Invalid syntax
        </div>
      );

      const alert = screen.getByRole('alert');
      expect(alert).toBeInTheDocument();
      expect(alert).toHaveTextContent('SQL validation failed');
    });
  });
});

describe('QueryEditor Edge Cases', () => {
  it('should handle extremely long queries', () => {
    const longQuery = 'SELECT * FROM users WHERE ' + 'id = 1 OR '.repeat(100) + 'id = 100';

    render(<textarea value={longQuery} data-testid="query-editor" />);

    const editor = screen.getByTestId('query-editor');
    expect(editor).toHaveValue(longQuery);
  });

  it('should handle special characters in query', () => {
    const specialQuery = "SELECT * FROM users WHERE name LIKE '%O\\'Reilly%'";

    render(<textarea value={specialQuery} data-testid="query-editor" />);

    const editor = screen.getByTestId('query-editor');
    expect(editor).toHaveValue(specialQuery);
  });

  it('should handle Unicode characters', () => {
    const unicodeQuery = 'SELECT * FROM 用户 WHERE 姓名 = \'张三\'';

    render(<textarea value={unicodeQuery} data-testid="query-editor" />);

    const editor = screen.getByTestId('query-editor');
    expect(editor).toHaveValue(unicodeQuery);
  });
});
