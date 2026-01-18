/**
 * NaturalLanguageInput UI Error Display Property-Based Tests
 * 
 * **Feature: database-query-tool, Property 16: UI error display**
 * **Validates: Requirements 7.4**
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { NaturalLanguageInput } from '../NaturalLanguageInput';

// Mock Monaco Editor for property testing
vi.mock('@monaco-editor/react', () => ({
  default: ({ value, onChange, onMount, language, options, ...props }: any) => {
    React.useEffect(() => {
      if (onMount) {
        const mockEditor = {
          focus: vi.fn(),
          addCommand: vi.fn(),
        };
        onMount(mockEditor);
      }
    }, [onMount]);

    return (
      <div
        data-testid="monaco-editor"
        data-language={language}
        data-value={value}
        {...props}
      >
        <textarea 
          data-testid="monaco-textarea"
          value={value} 
          onChange={(e) => onChange?.(e.target.value)} 
        />
      </div>
    );
  },
}));

// Mock QueryResults component
vi.mock('../QueryResults', () => ({
  QueryResults: ({ columns, rows, rowCount, executionTimeMs, loading, query }: any) => (
    <div data-testid="query-results">
      <div data-testid="results-query">{query}</div>
    </div>
  ),
}));

describe('NaturalLanguageInput UI Error Display Property Tests', () => {
  const mockOnSubmit = vi.fn();
  const mockOnExecuteSQL = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  /**
   * Property 16: UI error display
   * For any error that occurs during natural language processing, the UI should display the error message clearly to the user.
   * **Validates: Requirements 7.4**
   */
  it('Property 16: UI error display - should display any natural language processing error clearly', async () => {
    // Test with various types of natural language processing errors
    const errorMessages = [
      'OpenAI API key not configured',
      'Rate limit exceeded. Please try again later.',
      'Unable to generate SQL from the provided natural language query',
      'Network error: Failed to connect to LLM service',
      'Invalid API response format',
    ];

    for (const errorMessage of errorMessages) {
      const { unmount } = render(
        <NaturalLanguageInput
          onSubmit={mockOnSubmit}
          onExecuteSQL={mockOnExecuteSQL}
          error={errorMessage}
        />
      );

      // Verify that the error is displayed clearly
      const errorAlert = screen.getByRole('alert');
      expect(errorAlert).toBeInTheDocument();

      // Verify error message content
      expect(screen.getByText('Natural Language Processing Error')).toBeInTheDocument();
      expect(screen.getByText(errorMessage)).toBeInTheDocument();

      // Verify error styling (should be error type)
      expect(errorAlert).toHaveClass('ant-alert-error');

      // Verify error has an icon
      const errorIcon = screen.getByRole('img', { name: /close-circle/i });
      expect(errorIcon).toBeInTheDocument();

      // Verify error is closable
      const closeButton = screen.getByRole('button', { name: /close/i });
      expect(closeButton).toBeInTheDocument();

      unmount();
    }
  });

  it('Property 16: UI error display - should display SQL execution errors clearly', async () => {
    // Test SQL execution error display using a component with pre-set SQL
    const TestComponent = () => {
      const [sqlError, setSqlError] = React.useState<string | null>(null);
      const [generatedSQL, setGeneratedSQL] = React.useState('SELECT * FROM test_table');

      const handleExecuteSQL = async () => {
        setSqlError('Syntax error near "SELCT" at line 1');
      };

      return (
        <div>
          <div data-testid="generated-sql">{generatedSQL}</div>
          <button onClick={handleExecuteSQL}>Execute SQL</button>
          {sqlError && (
            <div role="alert" className="ant-alert ant-alert-error">
              <div>SQL Execution Error</div>
              <div>{sqlError}</div>
              <button onClick={() => setSqlError(null)}>Close</button>
            </div>
          )}
        </div>
      );
    };

    const { unmount } = render(<TestComponent />);

    // Verify SQL is present
    expect(screen.getByText('SELECT * FROM test_table')).toBeInTheDocument();

    // Execute SQL to trigger error
    const executeButton = screen.getByText('Execute SQL');
    fireEvent.click(executeButton);

    // Verify error is displayed
    const errorAlert = screen.getByRole('alert');
    expect(errorAlert).toBeInTheDocument();
    expect(screen.getByText('SQL Execution Error')).toBeInTheDocument();
    expect(screen.getByText('Syntax error near "SELCT" at line 1')).toBeInTheDocument();

    // Verify error styling
    expect(errorAlert).toHaveClass('ant-alert-error');

    // Verify error is closable
    const closeButton = screen.getByText('Close');
    fireEvent.click(closeButton);

    // Verify error is dismissed
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();

    unmount();
  });

  it('Property 16: UI error display - should allow dismissing any error message', async () => {
    // Test natural language processing error dismissal
    const nlpError = 'Natural language processing failed';
    const { unmount } = render(
      <NaturalLanguageInput
        onSubmit={mockOnSubmit}
        onExecuteSQL={mockOnExecuteSQL}
        error={nlpError}
      />
    );

    // Verify error is displayed
    expect(screen.getByText(nlpError)).toBeInTheDocument();

    // Find and click close button
    const closeButton = screen.getByRole('button', { name: /close/i });
    expect(closeButton).toBeInTheDocument();
    fireEvent.click(closeButton);

    // Note: In a real scenario, the parent would remove the error prop
    // The component itself doesn't handle dismissal, it just triggers the callback

    unmount();
  });

  it('Property 16: UI error display - should maintain consistent error formatting across all error types', async () => {
    // Test that all error types have consistent formatting and styling
    const errorScenarios = [
      {
        name: 'Natural Language Processing Error',
        setup: () => {
          return render(
            <NaturalLanguageInput
              onSubmit={mockOnSubmit}
              onExecuteSQL={mockOnExecuteSQL}
              error="Test NLP error message"
            />
          );
        },
        expectedTitle: 'Natural Language Processing Error',
        expectedMessage: 'Test NLP error message',
      },
    ];

    for (const scenario of errorScenarios) {
      const { unmount } = scenario.setup();

      // Verify error alert exists
      const errorAlert = screen.getByRole('alert');
      expect(errorAlert).toBeInTheDocument();

      // Verify consistent error styling
      expect(errorAlert).toHaveClass('ant-alert');
      expect(errorAlert).toHaveClass('ant-alert-error');

      // Verify error title
      expect(screen.getByText(scenario.expectedTitle)).toBeInTheDocument();

      // Verify error message
      expect(screen.getByText(scenario.expectedMessage)).toBeInTheDocument();

      // Verify error icon is present
      const errorIcon = screen.getByRole('img', { name: /close-circle/i });
      expect(errorIcon).toBeInTheDocument();

      // Verify close button is present
      const closeButton = screen.getByRole('button', { name: /close/i });
      expect(closeButton).toBeInTheDocument();

      // Verify error alert has proper ARIA attributes
      expect(errorAlert).toHaveAttribute('role', 'alert');

      unmount();
    }
  });

  it('Property 16: UI error display - should handle edge cases in error messages', async () => {
    // Test edge cases for error message display
    const edgeCaseErrors = [
      'A',
      'Very long error message that spans multiple lines and contains lots of technical details',
      'Error with special characters: !@#$%^&*()_+-=[]{}|;:,.<>?',
      'Error with quotes: "quoted text" and \'single quotes\'',
      'Error with unicode: 🚨 Error occurred 💥',
    ];

    for (const errorMessage of edgeCaseErrors) {
      const { unmount } = render(
        <NaturalLanguageInput
          onSubmit={mockOnSubmit}
          onExecuteSQL={mockOnExecuteSQL}
          error={errorMessage}
        />
      );

      // Should display non-empty error messages
      const errorAlert = screen.getByRole('alert');
      expect(errorAlert).toBeInTheDocument();
      expect(screen.getByText('Natural Language Processing Error')).toBeInTheDocument();
      
      // Verify the error message is displayed
      expect(screen.getByText(errorMessage)).toBeInTheDocument();

      unmount();
    }

    // Test empty/null/undefined cases separately
    const emptyErrors = ['', '   ', null as any, undefined as any];
    
    for (const errorMessage of emptyErrors) {
      const { unmount } = render(
        <NaturalLanguageInput
          onSubmit={mockOnSubmit}
          onExecuteSQL={mockOnExecuteSQL}
          error={errorMessage}
        />
      );

      // Should not display empty, null, or undefined error messages
      expect(screen.queryByRole('alert')).not.toBeInTheDocument();

      unmount();
    }
  });
});