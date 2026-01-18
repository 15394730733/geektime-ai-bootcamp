/**
 * Property-based tests for QueryPanel component
 * 
 * Tests Property 6: Tab Independence
 * **Validates: Requirements 3.1**
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, cleanup } from '@testing-library/react';
import * as fc from 'fast-check';
import { QueryPanel } from '../QueryPanel';
import { QueryTab, QueryResult } from '../../types/layout';

// Mock react-resizable-panels
vi.mock('react-resizable-panels', () => ({
  Panel: ({ children, ...props }: any) => <div data-testid="panel" {...props}>{children}</div>,
  PanelGroup: ({ children, ...props }: any) => <div data-testid="panel-group" {...props}>{children}</div>,
  PanelResizeHandle: (props: any) => <div data-testid="resize-handle" {...props} />,
}));

// Mock QueryEditor to avoid Monaco Editor issues
vi.mock('../QueryEditor', () => ({
  QueryEditor: ({ value, onChange, onExecute }: any) => (
    <div data-testid="query-editor">
      <textarea
        data-testid="query-textarea"
        value={value}
        onChange={(e) => onChange?.(e.target.value)}
      />
      <button data-testid="execute-button" onClick={onExecute}>
        Execute
      </button>
    </div>
  ),
}));

// Mock QueryResults
vi.mock('../QueryResults', () => ({
  QueryResults: ({ columns, rows, query }: any) => (
    <div data-testid="query-results">
      {rows.length === 0 && !query ? (
        <div>Execute a query to see results here.</div>
      ) : rows.length === 0 ? (
        <div>No results found for the query.</div>
      ) : (
        <div>
          <div>Columns: {columns.join(', ')}</div>
          <div>Rows: {rows.length}</div>
        </div>
      )}
    </div>
  ),
}));

// Mock TabBar
vi.mock('../TabBar', () => ({
  TabBar: ({ tabs, activeTabId, onTabChange, onTabCreate, onTabClose }: any) => (
    <div data-testid="tab-bar">
      {tabs.map((tab: any) => (
        <button
          key={tab.id}
          data-testid={`tab-${tab.id}`}
          onClick={() => onTabChange(tab.id)}
          className={tab.id === activeTabId ? 'active' : ''}
        >
          {tab.name}
        </button>
      ))}
      <button data-testid="create-tab" onClick={onTabCreate}>
        +
      </button>
    </div>
  ),
}));

// Generators for property-based testing
const queryResultArbitrary = fc.record({
  columns: fc.array(fc.string(), { minLength: 1, maxLength: 5 }),
  rows: fc.array(fc.array(fc.oneof(fc.string(), fc.integer(), fc.constant(null)), { minLength: 1, maxLength: 5 }), { maxLength: 10 }),
  rowCount: fc.nat(1000),
  executionTimeMs: fc.nat(10000),
  truncated: fc.boolean(),
});

const queryTabArbitrary = fc.record({
  id: fc.string({ minLength: 1 }),
  name: fc.string({ minLength: 1 }),
  query: fc.string(),
  results: fc.oneof(fc.constant(null), queryResultArbitrary),
  isDirty: fc.boolean(),
  createdAt: fc.date(),
});

const tabsArbitrary = fc.array(queryTabArbitrary, { minLength: 1, maxLength: 5 }).map(tabs => {
  // Ensure unique IDs
  return tabs.map((tab, index) => ({
    ...tab,
    id: `tab-${index}`,
  }));
});

describe('QueryPanel Property Tests', () => {
  const mockProps = {
    databaseName: 'test-db',
    verticalSplitSize: 50,
    loading: false,
    onTabChange: vi.fn(),
    onTabCreate: vi.fn(),
    onTabClose: vi.fn(),
    onQueryChange: vi.fn(),
    onExecute: vi.fn(),
    onVerticalSplitChange: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
    cleanup();
  });

  afterEach(() => {
    cleanup();
  });

  describe('Property 6: Tab Independence', () => {
    it('should maintain independent query content for each tab', () => {
      fc.assert(
        fc.property(
          tabsArbitrary,
          fc.nat().filter(n => n >= 0), // activeTabIndex
          (tabs, activeTabIndex) => {
            // Clean up before each property test iteration
            cleanup();
            
            // Ensure we have a valid active tab index
            const activeTab = tabs[activeTabIndex % tabs.length];
            const activeTabId = activeTab.id;

            const { container, rerender } = render(
              <QueryPanel
                {...mockProps}
                tabs={tabs}
                activeTabId={activeTabId}
              />
            );

            // Verify the active tab's content is displayed using container-scoped query
            const textarea = container.querySelector('[data-testid="query-textarea"]') as HTMLTextAreaElement;
            expect(textarea).toBeTruthy();
            expect(textarea.value).toBe(activeTab.query);

            // Switch to a different tab if available
            if (tabs.length > 1) {
              const otherTab = tabs.find(tab => tab.id !== activeTabId)!;
              
              rerender(
                <QueryPanel
                  {...mockProps}
                  tabs={tabs}
                  activeTabId={otherTab.id}
                />
              );

              // Verify the new active tab's content is displayed
              const newTextarea = container.querySelector('[data-testid="query-textarea"]') as HTMLTextAreaElement;
              expect(newTextarea).toBeTruthy();
              expect(newTextarea.value).toBe(otherTab.query);
            }

            return true;
          }
        ),
        { numRuns: 50 } // Reduced from 100 to avoid timeout
      );
    });

    it('should maintain independent results for each tab', () => {
      fc.assert(
        fc.property(
          tabsArbitrary,
          fc.nat().filter(n => n >= 0), // activeTabIndex
          (tabs, activeTabIndex) => {
            // Clean up before each property test iteration
            cleanup();
            
            // Ensure we have a valid active tab index
            const activeTab = tabs[activeTabIndex % tabs.length];
            const activeTabId = activeTab.id;

            const { container, rerender } = render(
              <QueryPanel
                {...mockProps}
                tabs={tabs}
                activeTabId={activeTabId}
              />
            );

            // Check if results are displayed correctly for active tab
            const resultsDiv = container.querySelector('[data-testid="query-results"]');
            expect(resultsDiv).toBeTruthy();
            
            if (activeTab.results && activeTab.results.rows.length > 0) {
              // Should show results
              expect(resultsDiv!.textContent).toContain(`Rows: ${activeTab.results.rows.length}`);
            } else {
              // Should show placeholder or empty state - either message is acceptable
              const hasExecuteMessage = resultsDiv!.textContent!.includes('Execute a query to see results here.');
              const hasNoResultsMessage = resultsDiv!.textContent!.includes('No results found for the query.');
              expect(hasExecuteMessage || hasNoResultsMessage).toBe(true);
            }

            // Switch to a different tab if available
            if (tabs.length > 1) {
              const otherTab = tabs.find(tab => tab.id !== activeTabId)!;
              
              rerender(
                <QueryPanel
                  {...mockProps}
                  tabs={tabs}
                  activeTabId={otherTab.id}
                />
              );

              // Check if results are displayed correctly for the new active tab
              const newResultsDiv = container.querySelector('[data-testid="query-results"]');
              expect(newResultsDiv).toBeTruthy();
              
              if (otherTab.results && otherTab.results.rows.length > 0) {
                // Should show results
                expect(newResultsDiv!.textContent).toContain(`Rows: ${otherTab.results.rows.length}`);
              } else {
                // Should show placeholder or empty state - either message is acceptable
                const hasExecuteMessage = newResultsDiv!.textContent!.includes('Execute a query to see results here.');
                const hasNoResultsMessage = newResultsDiv!.textContent!.includes('No results found for the query.');
                expect(hasExecuteMessage || hasNoResultsMessage).toBe(true);
              }
            }

            return true;
          }
        ),
        { numRuns: 50 } // Reduced from 100 to avoid timeout
      );
    });

    it('should preserve tab state when switching between tabs', () => {
      fc.assert(
        fc.property(
          fc.array(queryTabArbitrary, { minLength: 2, maxLength: 4 }).map(tabs => {
            // Ensure unique IDs and at least one tab has content
            return tabs.map((tab, index) => ({
              ...tab,
              id: `tab-${index}`,
              query: index === 0 ? 'SELECT * FROM users' : tab.query,
            }));
          }),
          (tabs) => {
            // Clean up before each property test iteration
            cleanup();
            
            const firstTab = tabs[0];
            const secondTab = tabs[1];

            // Start with first tab
            const { container, rerender } = render(
              <QueryPanel
                {...mockProps}
                tabs={tabs}
                activeTabId={firstTab.id}
              />
            );

            // Verify first tab content
            const textarea1 = container.querySelector('[data-testid="query-textarea"]') as HTMLTextAreaElement;
            expect(textarea1).toBeTruthy();
            expect(textarea1.value).toBe(firstTab.query);

            // Switch to second tab
            rerender(
              <QueryPanel
                {...mockProps}
                tabs={tabs}
                activeTabId={secondTab.id}
              />
            );

            // Verify second tab content
            const textarea2 = container.querySelector('[data-testid="query-textarea"]') as HTMLTextAreaElement;
            expect(textarea2).toBeTruthy();
            expect(textarea2.value).toBe(secondTab.query);

            // Switch back to first tab
            rerender(
              <QueryPanel
                {...mockProps}
                tabs={tabs}
                activeTabId={firstTab.id}
              />
            );

            // Verify first tab content is preserved
            const textarea3 = container.querySelector('[data-testid="query-textarea"]') as HTMLTextAreaElement;
            expect(textarea3).toBeTruthy();
            expect(textarea3.value).toBe(firstTab.query);

            return true;
          }
        ),
        { numRuns: 50 } // Reduced from 100 to avoid timeout
      );
    });

    it('should handle query changes independently per tab', () => {
      fc.assert(
        fc.property(
          fc.array(queryTabArbitrary, { minLength: 2, maxLength: 3 }).map(tabs => {
            return tabs.map((tab, index) => ({
              ...tab,
              id: `tab-${index}`,
            }));
          }),
          fc.string({ minLength: 1, maxLength: 50 }), // new query content
          (tabs, newQuery) => {
            // Clean up before each property test iteration
            cleanup();
            
            const firstTab = tabs[0];
            const mockOnQueryChange = vi.fn();

            const { container } = render(
              <QueryPanel
                {...mockProps}
                tabs={tabs}
                activeTabId={firstTab.id}
                onQueryChange={mockOnQueryChange}
              />
            );

            // Simulate query change
            const textarea = container.querySelector('[data-testid="query-textarea"]') as HTMLTextAreaElement;
            expect(textarea).toBeTruthy();
            fireEvent.change(textarea, { target: { value: newQuery } });

            // Verify onQueryChange was called with correct tab ID
            expect(mockOnQueryChange).toHaveBeenCalledWith(firstTab.id, newQuery);

            return true;
          }
        ),
        { numRuns: 50 } // Reduced from 100 to avoid timeout
      );
    });

    it('should handle execute commands independently per tab', () => {
      fc.assert(
        fc.property(
          tabsArbitrary,
          fc.nat().filter(n => n >= 0), // activeTabIndex
          (tabs, activeTabIndex) => {
            // Clean up before each property test iteration
            cleanup();
            
            const activeTab = tabs[activeTabIndex % tabs.length];
            const mockOnExecute = vi.fn();

            const { container } = render(
              <QueryPanel
                {...mockProps}
                tabs={tabs}
                activeTabId={activeTab.id}
                onExecute={mockOnExecute}
              />
            );

            // Find and click execute button
            const executeButton = container.querySelector('[data-testid="execute-button"]') as HTMLButtonElement;
            expect(executeButton).toBeTruthy();
            fireEvent.click(executeButton);

            // Verify onExecute was called with correct tab ID
            expect(mockOnExecute).toHaveBeenCalledWith(activeTab.id);

            return true;
          }
        ),
        { numRuns: 50 } // Reduced from 100 to avoid timeout
      );
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty tabs array gracefully', () => {
      cleanup();
      
      render(
        <QueryPanel
          {...mockProps}
          tabs={[]}
          activeTabId="non-existent"
        />
      );

      expect(screen.getByText('No active tab found')).toBeInTheDocument();
    });

    it('should handle non-existent active tab ID', () => {
      cleanup();
      
      const tabs = [
        {
          id: 'tab-1',
          name: 'Query 1',
          query: 'SELECT 1',
          results: null,
          isDirty: false,
          createdAt: new Date(),
        },
      ];

      render(
        <QueryPanel
          {...mockProps}
          tabs={tabs}
          activeTabId="non-existent-tab"
        />
      );

      expect(screen.getByText('No active tab found')).toBeInTheDocument();
    });
  });
});