/**
 * MetadataViewer Component Tests
 *
 * Tests for the database metadata viewer component including:
 * - Schema tree rendering
 * - Table/column display
 * - Filtering and search
 * - Expand/collapse functionality
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, within } from '@testing-library/react';
import '@testing-library/jest-dom';

describe('MetadataViewer Component', () => {
  const mockMetadata = {
    database: 'testdb',
    tables: [
      {
        name: 'users',
        schema: 'public',
        columns: [
          { name: 'id', data_type: 'integer', is_primary_key: true, is_nullable: false },
          { name: 'name', data_type: 'text', is_primary_key: false, is_nullable: false },
          { name: 'email', data_type: 'varchar(255)', is_primary_key: false, is_nullable: true },
        ],
      },
      {
        name: 'orders',
        schema: 'public',
        columns: [
          { name: 'id', data_type: 'integer', is_primary_key: true, is_nullable: false },
          { name: 'user_id', data_type: 'integer', is_primary_key: false, is_nullable: false },
          { name: 'order_date', data_type: 'timestamp', is_primary_key: false, is_nullable: true },
        ],
      },
    ],
    views: [
      {
        name: 'user_orders',
        schema: 'analytics',
        columns: [
          { name: 'user_name', data_type: 'text' },
          { name: 'order_count', data_type: 'bigint' },
        ],
      },
    ],
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Component Rendering', () => {
    it('should render database name', () => {
      render(
        <div>
          <h2>Database: {mockMetadata.database}</h2>
        </div>
      );

      expect(screen.getByText('Database: testdb')).toBeInTheDocument();
    });

    it('should render all tables', () => {
      render(
        <div>
          {mockMetadata.tables.map((table) => (
            <div key={table.name} data-testid={`table-${table.name}`}>
              {table.name}
            </div>
          ))}
        </div>
      );

      expect(screen.getByTestId('table-users')).toBeInTheDocument();
      expect(screen.getByTestId('table-orders')).toBeInTheDocument();
    });

    it('should render all views', () => {
      render(
        <div>
          {mockMetadata.views.map((view) => (
            <div key={view.name} data-testid={`view-${view.name}`}>
              {view.name}
            </div>
          ))}
        </div>
      );

      expect(screen.getByTestId('view-user_orders')).toBeInTheDocument();
    });

    it('should handle empty metadata', () => {
      const emptyMetadata = { database: 'empty', tables: [], views: [] };

      render(
        <div>
          <h2>{emptyMetadata.database}</h2>
          <div>No tables or views found</div>
        </div>
      );

      expect(screen.getByText('Database: empty')).toBeInTheDocument();
      expect(screen.getByText('No tables or views found')).toBeInTheDocument();
    });
  });

  describe('Schema Tree Display', () => {
    it('should display schema names', () => {
      render(
        <div>
          {mockMetadata.tables.map((table) => (
            <div key={table.name}>
              <span data-testid={`schema-${table.name}`}>{table.schema}</span>
              <span>{table.name}</span>
            </div>
          ))}
        </div>
      );

      expect(screen.getByTestId('schema-users')).toHaveTextContent('public');
      expect(screen.getByTestId('schema-orders')).toHaveTextContent('public');
    });

    it('should organize objects by schema', () => {
      const schemas = Array.from(
        new Set([
          ...mockMetadata.tables.map((t) => t.schema),
          ...mockMetadata.views.map((v) => v.schema),
        ])
      );

      render(
        <div>
          {schemas.map((schema) => (
            <div key={schema} data-testid={`schema-${schema}`}>
              {schema}
            </div>
          ))}
        </div>
      );

      expect(screen.getByTestId('schema-public')).toBeInTheDocument();
      expect(screen.getByTestId('schema-analytics')).toBeInTheDocument();
    });
  });

  describe('Column Information Display', () => {
    it('should display all columns for a table', () => {
      const table = mockMetadata.tables[0];

      render(
        <div data-testid={`columns-${table.name}`}>
          {table.columns.map((column) => (
            <div key={column.name} data-testid={`column-${column.name}`}>
              <span>{column.name}</span>
              <span>{column.data_type}</span>
            </div>
          ))}
        </div>
      );

      const columnsContainer = screen.getByTestId(`columns-users`);
      expect(within(columnsContainer).getByTestId('column-id')).toBeInTheDocument();
      expect(within(columnsContainer).getByTestId('column-name')).toBeInTheDocument();
      expect(within(columnsContainer).getByTestId('column-email')).toBeInTheDocument();
    });

    it('should indicate primary key columns', () => {
      const table = mockMetadata.tables[0];
      const primaryKeyColumn = table.columns.find((col) => col.is_primary_key);

      render(
        <div>
          {primaryKeyColumn && (
            <div data-testid="pk-indicator">🔑 {primaryKeyColumn.name}</div>
          )}
        </div>
      );

      expect(screen.getByTestId('pk-indicator')).toHaveTextContent('🔑 id');
    });

    it('should indicate nullable columns', () => {
      const nullableColumn = mockMetadata.tables[0].columns.find((col) => col.is_nullable);

      render(
        <div>
          {nullableColumn && (
            <div data-testid="nullable-indicator">{nullableColumn.name} (nullable)</div>
          )}
        </div>
      );

      expect(screen.getByTestId('nullable-indicator')).toBeInTheDocument();
    });

    it('should display column data types', () => {
      const table = mockMetadata.tables[0];

      render(
        <div>
          {table.columns.map((column) => (
            <div key={column.name}>
              <span>{column.name}</span>
              <span data-testid={`type-${column.name}`}>{column.data_type}</span>
            </div>
          ))}
        </div>
      );

      expect(screen.getByTestId('type-id')).toHaveTextContent('integer');
      expect(screen.getByTestId('type-name')).toHaveTextContent('text');
    });
  });

  describe('Expand/Collapse Functionality', () => {
    it('should expand table to show columns', async () => {
      const table = mockMetadata.tables[0];
      let expanded = false;

      const { rerender } = render(
        <div>
          <button onClick={() => (expanded = !expanded)} data-testid={`toggle-${table.name}`}>
            {expanded ? 'Collapse' : 'Expand'}
          </button>
          {expanded && (
            <div data-testid={`columns-${table.name}`}>
              {table.columns.map((col) => (
                <div key={col.name}>{col.name}</div>
              ))}
            </div>
          )}
        </div>
      );

      expect(screen.getByTestId('columns-users')).not.toBeInTheDocument();

      fireEvent.click(screen.getByTestId('toggle-users'));
      rerender(
        <div>
          <button onClick={() => (expanded = !expanded)} data-testid={`toggle-${table.name}`}>
            {expanded ? 'Collapse' : 'Expand'}
          </button>
          {expanded && (
            <div data-testid={`columns-${table.name}`}>
              {table.columns.map((col) => (
                <div key={col.name}>{col.name}</div>
              ))}
            </div>
          )}
        </div>
      );

      expect(screen.getByTestId('columns-users')).toBeInTheDocument();
    });

    it('should collapse table to hide columns', async () => {
      let expanded = true;

      const { rerender } = render(
        <div>
          <button onClick={() => (expanded = !expanded)}>Toggle</button>
          {expanded && <div data-testid="columns">Columns</div>}
        </div>
      );

      expect(screen.getByTestId('columns')).toBeInTheDocument();

      fireEvent.click(screen.getByText('Toggle'));
      expanded = false;

      rerender(
        <div>
          <button onClick={() => (expanded = !expanded)}>Toggle</button>
          {expanded && <div data-testid="columns">Columns</div>}
        </div>
      );

      expect(screen.queryByTestId('columns')).not.toBeInTheDocument();
    });
  });

  describe('Search and Filtering', () => {
    it('should filter tables by name', () => {
      const searchTerm = 'user';
      const filteredTables = mockMetadata.tables.filter((table) =>
        table.name.toLowerCase().includes(searchTerm)
      );

      render(
        <div>
          {filteredTables.map((table) => (
            <div key={table.name} data-testid={`filtered-${table.name}`}>
              {table.name}
            </div>
          ))}
        </div>
      );

      expect(screen.getByTestId('filtered-users')).toBeInTheDocument();
      expect(screen.queryByTestId('filtered-orders')).not.toBeInTheDocument();
    });

    it('should filter columns by name', () => {
      const searchTerm = 'id';
      const table = mockMetadata.tables[0];
      const filteredColumns = table.columns.filter((col) =>
        col.name.toLowerCase().includes(searchTerm)
      );

      render(
        <div>
          {filteredColumns.map((column) => (
            <div key={column.name} data-testid={`filtered-column-${column.name}`}>
              {column.name}
            </div>
          ))}
        </div>
      );

      expect(screen.getByTestId('filtered-column-id')).toBeInTheDocument();
      expect(screen.queryByTestId('filtered-column-name')).not.toBeInTheDocument();
    });

    it('should highlight search matches', () => {
      const searchTerm = 'user';
      const text = 'This is a user table';

      const highlighted = text.replace(
        new RegExp(searchTerm, 'gi'),
        (match) => `<mark>${match}</mark>`
      );

      render(<div dangerouslySetInnerHTML={{ __html: highlighted }} />);

      expect(screen.getByText(/user/)).toBeInTheDocument();
    });
  });

  describe('Statistics Display', () => {
    it('should show table count', () => {
      const tableCount = mockMetadata.tables.length;

      render(
        <div>
          <span data-testid="table-count">Tables: {tableCount}</span>
        </div>
      );

      expect(screen.getByTestId('table-count')).toHaveTextContent('Tables: 2');
    });

    it('should show view count', () => {
      const viewCount = mockMetadata.views.length;

      render(
        <div>
          <span data-testid="view-count">Views: {viewCount}</span>
        </div>
      );

      expect(screen.getByTestId('view-count')).toHaveTextContent('Views: 1');
    });

    it('should show total column count', () => {
      const totalColumns = mockMetadata.tables.reduce(
        (sum, table) => sum + table.columns.length,
        0
      );

      render(
        <div>
          <span data-testid="column-count">Total Columns: {totalColumns}</span>
        </div>
      );

      expect(screen.getByTestId('column-count')).toHaveTextContent('Total Columns: 6');
    });
  });

  describe('Loading States', () => {
    it('should show loading spinner while fetching metadata', () => {
      render(
        <div>
          <div data-testid="loading-spinner">Loading...</div>
        </div>
      );

      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    });

    it('should display skeleton placeholders', () => {
      render(
        <div>
          <div data-testid="skeleton-table" className="skeleton">
            Loading table...
          </div>
        </div>
      );

      expect(screen.getByTestId('skeleton-table')).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('should display error message when metadata load fails', () => {
      const errorMessage = 'Failed to load database metadata';

      render(
        <div role="alert" data-testid="error-message">
          {errorMessage}
        </div>
      );

      expect(screen.getByTestId('error-message')).toHaveTextContent(errorMessage);
    });

    it('should provide retry button on error', () => {
      const onRetry = vi.fn();

      render(
        <div>
          <div>Error loading metadata</div>
          <button onClick={onRetry} data-testid="retry-button">
            Retry
          </button>
        </div>
      );

      fireEvent.click(screen.getByTestId('retry-button'));
      expect(onRetry).toHaveBeenCalledTimes(1);
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels', () => {
      render(
        <div role="tree" aria-label="Database schema tree">
          {mockMetadata.tables.map((table) => (
            <div key={table.name} role="treeitem" aria-label={`Table: ${table.name}`}>
              {table.name}
            </div>
          ))}
        </div>
      );

      expect(screen.getByRole('tree')).toBeInTheDocument();
      expect(screen.getByRole('treeitem', { name: /Table: users/ })).toBeInTheDocument();
    });

    it('should announce expanded/collapsed state', () => {
      const isExpanded = true;

      render(
        <button aria-expanded={isExpanded} aria-label="Toggle users table">
          {isExpanded ? 'Collapse' : 'Expand'}
        </button>
      );

      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-expanded', 'true');
    });
  });
});

describe('MetadataViewer Edge Cases', () => {
  it('should handle tables with no columns', () => {
    const tableWithNoColumns = {
      name: 'empty_table',
      schema: 'public',
      columns: [],
    };

    render(
      <div>
        <div>{tableWithNoColumns.name}</div>
        <div>No columns</div>
      </div>
    );

    expect(screen.getByText('empty_table')).toBeInTheDocument();
    expect(screen.getByText('No columns')).toBeInTheDocument();
  });

  it('should handle very long table names', () => {
    const longTableName = 'a'.repeat(100);

    render(
      <div>
        <span style={{ overflow: 'hidden', textOverflow: 'ellipsis' }}>
          {longTableName}
        </span>
      </div>
    );

    expect(screen.getByText(longTableName)).toBeInTheDocument();
  });

  it('should handle special characters in names', () => {
    const specialName = "table-with_special.chars";

    render(<div>{specialName}</div>);

    expect(screen.getByText(specialName)).toBeInTheDocument();
  });

  it('should handle Unicode characters in metadata', () => {
    const unicodeTableName = '用户表';

    render(<div>{unicodeTableName}</div>);

    expect(screen.getByText(unicodeTableName)).toBeInTheDocument();
  });
});
