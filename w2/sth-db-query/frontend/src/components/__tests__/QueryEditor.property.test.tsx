/**
 * QueryEditor Property-Based Tests
 * 
 * **Feature: database-query-tool, Property 14: SQL editor syntax highlighting**
 * **Validates: Requirements 6.2**
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { QueryEditor } from '../QueryEditor';

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
        data-syntax-highlighting={language === 'sql' ? 'enabled' : 'disabled'}
        data-options={JSON.stringify(options)}
        {...props}
      >
        <textarea value={value} onChange={(e) => onChange?.(e.target.value)} />
      </div>
    );
  },
}));

// Mock monaco-editor
vi.mock('monaco-editor', () => ({
  languages: {
    setLanguageConfiguration: vi.fn(),
  },
  KeyMod: {
    CtrlCmd: 2048,
  },
  KeyCode: {
    Enter: 3,
  },
}));

describe('QueryEditor Property Tests', () => {
  const mockOnChange = vi.fn();
  const mockOnExecute = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  /**
   * Property 14: SQL editor syntax highlighting
   * For any SQL text entered in the Monaco Editor, appropriate syntax highlighting should be applied.
   * **Validates: Requirements 6.2**
   */
  it('Property 14: SQL editor syntax highlighting - should apply SQL syntax highlighting for any SQL content', () => {
    // Test with various SQL queries to ensure syntax highlighting is consistently applied
    const sqlQueries = [
      'SELECT * FROM users',
      'SELECT name, email FROM customers WHERE active = true',
      'INSERT INTO products (name, price) VALUES (\'Test\', 99.99)',
      'UPDATE orders SET status = \'completed\' WHERE id = 1',
      'DELETE FROM logs WHERE created_at < \'2023-01-01\'',
      'CREATE TABLE test (id SERIAL PRIMARY KEY, name VARCHAR(255))',
      'DROP TABLE IF EXISTS temp_table',
      'ALTER TABLE users ADD COLUMN last_login TIMESTAMP',
      'SELECT COUNT(*) FROM orders GROUP BY status HAVING COUNT(*) > 10',
      'WITH recent_orders AS (SELECT * FROM orders WHERE created_at > NOW() - INTERVAL \'7 days\') SELECT * FROM recent_orders',
      '', // Empty query
      '   ', // Whitespace only
      'EXPLAIN ANALYZE SELECT * FROM large_table',
      'SELECT DISTINCT category FROM products ORDER BY category ASC LIMIT 100',
    ];

    sqlQueries.forEach((query, index) => {
      const { unmount } = render(
        <QueryEditor
          key={index}
          value={query}
          onChange={mockOnChange}
          onExecute={mockOnExecute}
        />
      );

      const editor = screen.getByTestId('monaco-editor');
      
      // Verify that the editor is configured with SQL language
      expect(editor).toHaveAttribute('data-language', 'sql');
      
      // Verify that syntax highlighting is enabled
      expect(editor).toHaveAttribute('data-syntax-highlighting', 'enabled');
      
      // Verify that SQL-specific options are configured
      const optionsAttr = editor.getAttribute('data-options');
      expect(optionsAttr).toBeTruthy();
      
      if (optionsAttr) {
        const options = JSON.parse(optionsAttr);
        
        // Verify SQL-specific editor options are set
        expect(options.suggest?.showKeywords).toBe(true);
        expect(options.suggest?.showFunctions).toBe(true);
        expect(options.matchBrackets).toBe('always');
        expect(options.autoIndent).toBe('full');
        expect(options.formatOnType).toBe(true);
        expect(options.formatOnPaste).toBe(true);
      }

      unmount();
    });
  });

  it('Property 14: SQL editor syntax highlighting - should maintain consistent highlighting configuration across different editor instances', () => {
    // Test that multiple editor instances all have consistent SQL highlighting configuration
    const editorInstances = [
      { value: 'SELECT 1', height: 200 },
      { value: 'SELECT * FROM table1', height: 300 },
      { value: 'SELECT COUNT(*) FROM table2', height: 400 },
      { value: '', height: 250 },
    ];

    editorInstances.forEach((instance, index) => {
      const { unmount } = render(
        <QueryEditor
          key={index}
          value={instance.value}
          onChange={mockOnChange}
          onExecute={mockOnExecute}
          height={instance.height}
        />
      );

      const editor = screen.getByTestId('monaco-editor');
      
      // All instances should have SQL language configured
      expect(editor).toHaveAttribute('data-language', 'sql');
      expect(editor).toHaveAttribute('data-syntax-highlighting', 'enabled');
      
      // All instances should have consistent SQL editor options
      const optionsAttr = editor.getAttribute('data-options');
      expect(optionsAttr).toBeTruthy();
      
      if (optionsAttr) {
        const options = JSON.parse(optionsAttr);
        
        // Verify consistent SQL highlighting options across all instances
        expect(options.suggest?.showKeywords).toBe(true);
        expect(options.suggest?.showSnippets).toBe(true);
        expect(options.suggest?.showFunctions).toBe(true);
        expect(options.matchBrackets).toBe('always');
        expect(options.autoIndent).toBe('full');
        expect(options.formatOnType).toBe(true);
        expect(options.formatOnPaste).toBe(true);
        expect(options.folding).toBe(true);
        expect(options.foldingStrategy).toBe('indentation');
        expect(options.showFoldingControls).toBe('always');
      }

      unmount();
    });
  });

  it('Property 14: SQL editor syntax highlighting - should configure SQL language features for any editor instance', () => {
    // Test that SQL language configuration is applied regardless of initial content
    const testCases = [
      { value: 'SELECT', description: 'partial SQL keyword' },
      { value: 'SELECT * FROM users WHERE id = 1;', description: 'complete SQL statement' },
      { value: '-- This is a comment\nSELECT * FROM table', description: 'SQL with comments' },
      { value: 'SELECT\n  column1,\n  column2\nFROM\n  table_name', description: 'multi-line formatted SQL' },
      { value: 'INVALID SQL SYNTAX HERE', description: 'invalid SQL syntax' },
    ];

    testCases.forEach((testCase, index) => {
      const { unmount } = render(
        <QueryEditor
          key={index}
          value={testCase.value}
          onChange={mockOnChange}
          onExecute={mockOnExecute}
        />
      );

      const editor = screen.getByTestId('monaco-editor');
      
      // Verify SQL language is set regardless of content validity
      expect(editor).toHaveAttribute('data-language', 'sql');
      expect(editor).toHaveAttribute('data-syntax-highlighting', 'enabled');
      
      // Verify that SQL language features are configured
      const optionsAttr = editor.getAttribute('data-options');
      expect(optionsAttr).toBeTruthy();
      
      if (optionsAttr) {
        const options = JSON.parse(optionsAttr);
        
        // SQL language features should be enabled for all content types
        expect(options.suggest?.showKeywords).toBe(true);
        expect(options.suggest?.showFunctions).toBe(true);
        expect(options.matchBrackets).toBe('always');
        expect(options.wordWrap).toBe('on');
        expect(options.tabSize).toBe(2);
        expect(options.insertSpaces).toBe(true);
      }

      unmount();
    });
  });
});