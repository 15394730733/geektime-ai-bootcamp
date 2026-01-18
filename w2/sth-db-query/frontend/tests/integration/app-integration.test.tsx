/**
 * Frontend Integration Tests
 *
 * Tests the complete frontend application flow including component interactions,
 * state management, and API communication.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { message } from 'antd';

import App from '../../src/App';
import { apiClient } from '../../src/services/api';

// Mock the API client
vi.mock('../../src/services/api', () => ({
  apiClient: {
    getDatabases: vi.fn(),
    createDatabase: vi.fn(),
    updateDatabase: vi.fn(),
    deleteDatabase: vi.fn(),
    getDatabaseMetadata: vi.fn(),
    executeQuery: vi.fn(),
    executeNaturalLanguageQuery: vi.fn(),
  },
}));

// Mock antd message
vi.mock('antd', async () => {
  const actual = await vi.importActual('antd');
  return {
    ...actual,
    message: {
      success: vi.fn(),
      error: vi.fn(),
      warning: vi.fn(),
    },
  };
});

const mockApiClient = apiClient as any;

describe('Frontend Integration Tests', () => {
  const user = userEvent.setup();

  beforeEach(() => {
    vi.clearAllMocks();
    
    // Default mock responses
    mockApiClient.getDatabases.mockResolvedValue([]);
    mockApiClient.getDatabaseMetadata.mockResolvedValue({
      database: 'test_db',
      tables: [],
      views: [],
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  const renderApp = () => {
    return render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
  };

  describe('Database Management Flow', () => {
    it('should complete full database management workflow', async () => {
      const mockDatabases = [
        {
          id: '1',
          name: 'test_db',
          url: 'postgresql://user:pass@localhost:5432/testdb',
          description: 'Test database',
          is_active: true,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        },
      ];

      mockApiClient.getDatabases.mockResolvedValue(mockDatabases);
      mockApiClient.createDatabase.mockResolvedValue(mockDatabases[0]);

      renderApp();

      // Should start on databases page
      await waitFor(() => {
        expect(screen.getByText('Databases')).toBeInTheDocument();
      });

      // Should load databases on mount
      await waitFor(() => {
        expect(mockApiClient.getDatabases).toHaveBeenCalled();
      });

      // Click add database button
      const addButton = screen.getByRole('button', { name: /add/i });
      await user.click(addButton);

      // Should open database form modal
      await waitFor(() => {
        expect(screen.getByText('Add Database Connection')).toBeInTheDocument();
      });

      // Fill out the form
      const nameInput = screen.getByLabelText(/database name/i);
      const urlInput = screen.getByLabelText(/database url/i);
      const descriptionInput = screen.getByLabelText(/description/i);

      await user.type(nameInput, 'test_db');
      await user.type(urlInput, 'postgresql://user:pass@localhost:5432/testdb');
      await user.type(descriptionInput, 'Test database');

      // Submit the form
      const submitButton = screen.getByRole('button', { name: /add database/i });
      await user.click(submitButton);

      // Should call create API
      await waitFor(() => {
        expect(mockApiClient.createDatabase).toHaveBeenCalledWith({
          name: 'test_db',
          url: 'postgresql://user:pass@localhost:5432/testdb',
          description: 'Test database',
          is_active: true,
        });
      });

      // Should show success message
      expect(message.success).toHaveBeenCalledWith('Database connection saved successfully');
    });

    it('should handle database deletion workflow', async () => {
      const mockDatabases = [
        {
          id: '1',
          name: 'test_db',
          url: 'postgresql://user:pass@localhost:5432/testdb',
          description: 'Test database',
          is_active: true,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        },
      ];

      mockApiClient.getDatabases.mockResolvedValue(mockDatabases);
      mockApiClient.deleteDatabase.mockResolvedValue(undefined);

      renderApp();

      await waitFor(() => {
        expect(screen.getByText('test_db')).toBeInTheDocument();
      });

      // Find and click delete button
      const deleteButton = screen.getByRole('button', { name: /delete/i });
      await user.click(deleteButton);

      // Should show confirmation modal
      await waitFor(() => {
        expect(screen.getByText('Confirm Deletion')).toBeInTheDocument();
      });

      // Confirm deletion
      const confirmButton = screen.getByRole('button', { name: /ok/i });
      await user.click(confirmButton);

      // Should call delete API
      await waitFor(() => {
        expect(mockApiClient.deleteDatabase).toHaveBeenCalledWith('test_db');
      });
    });
  });

  describe('Query Execution Flow', () => {
    it('should complete SQL query execution workflow', async () => {
      const mockDatabases = [
        {
          id: '1',
          name: 'test_db',
          url: 'postgresql://user:pass@localhost:5432/testdb',
          description: 'Test database',
          is_active: true,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        },
      ];

      const mockMetadata = {
        database: 'test_db',
        tables: [
          {
            name: 'users',
            schema: 'public',
            columns: [
              { name: 'id', data_type: 'integer', is_nullable: false, is_primary_key: true },
              { name: 'name', data_type: 'varchar', is_nullable: false, is_primary_key: false },
            ],
          },
        ],
        views: [],
      };

      const mockQueryResult = {
        columns: ['id', 'name'],
        rows: [[1, 'John Doe'], [2, 'Jane Smith']],
        row_count: 2,
        execution_time_ms: 150,
        truncated: false,
      };

      mockApiClient.getDatabases.mockResolvedValue(mockDatabases);
      mockApiClient.getDatabaseMetadata.mockResolvedValue(mockMetadata);
      mockApiClient.executeQuery.mockResolvedValue(mockQueryResult);

      renderApp();

      // Navigate to query page
      const queryLink = screen.getByText('Query');
      await user.click(queryLink);

      await waitFor(() => {
        expect(screen.getByText('Database Query Tool')).toBeInTheDocument();
      });

      // Select database
      const databaseSelect = screen.getByRole('combobox');
      await user.click(databaseSelect);
      
      const databaseOption = screen.getByText('test_db - Test database');
      await user.click(databaseOption);

      // Should load metadata
      await waitFor(() => {
        expect(mockApiClient.getDatabaseMetadata).toHaveBeenCalledWith('test_db');
      });

      // Should show metadata in sidebar
      await waitFor(() => {
        expect(screen.getByText('users')).toBeInTheDocument();
      });

      // Enter SQL query
      const queryEditor = screen.getByRole('textbox');
      await user.type(queryEditor, 'SELECT * FROM users');

      // Execute query
      const executeButton = screen.getByRole('button', { name: /execute/i });
      await user.click(executeButton);

      // Should call execute API
      await waitFor(() => {
        expect(mockApiClient.executeQuery).toHaveBeenCalledWith('test_db', {
          sql: 'SELECT * FROM users',
        });
      });

      // Should show results
      await waitFor(() => {
        expect(screen.getByText('John Doe')).toBeInTheDocument();
        expect(screen.getByText('Jane Smith')).toBeInTheDocument();
      });

      // Should show execution time
      expect(screen.getByText(/150ms/)).toBeInTheDocument();
    });

    it('should complete natural language query workflow', async () => {
      const mockDatabases = [
        {
          id: '1',
          name: 'test_db',
          url: 'postgresql://user:pass@localhost:5432/testdb',
          description: 'Test database',
          is_active: true,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        },
      ];

      const mockNLResult = {
        generated_sql: 'SELECT * FROM users LIMIT 10',
        columns: ['id', 'name'],
        rows: [[1, 'John Doe']],
        row_count: 1,
        execution_time_ms: 200,
        truncated: false,
      };

      mockApiClient.getDatabases.mockResolvedValue(mockDatabases);
      mockApiClient.executeNaturalLanguageQuery.mockResolvedValue(mockNLResult);

      renderApp();

      // Navigate to query page
      const queryLink = screen.getByText('Query');
      await user.click(queryLink);

      // Select database
      const databaseSelect = screen.getByRole('combobox');
      await user.click(databaseSelect);
      const databaseOption = screen.getByText('test_db - Test database');
      await user.click(databaseOption);

      // Should show natural language input
      await waitFor(() => {
        expect(screen.getByPlaceholderText(/describe what you want to query/i)).toBeInTheDocument();
      });

      // Enter natural language query
      const nlInput = screen.getByPlaceholderText(/describe what you want to query/i);
      await user.type(nlInput, 'Show me all users');

      // Submit natural language query
      const nlSubmitButton = screen.getByRole('button', { name: /generate sql/i });
      await user.click(nlSubmitButton);

      // Should call natural language API
      await waitFor(() => {
        expect(mockApiClient.executeNaturalLanguageQuery).toHaveBeenCalledWith('test_db', {
          prompt: 'Show me all users',
        });
      });

      // Should show generated SQL in editor
      await waitFor(() => {
        expect(screen.getByDisplayValue('SELECT * FROM users LIMIT 10')).toBeInTheDocument();
      });

      // Should show results
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });
  });

  describe('Error Handling Flow', () => {
    it('should handle API errors gracefully', async () => {
      mockApiClient.getDatabases.mockRejectedValue(new Error('Network error'));

      renderApp();

      // Should show error message
      await waitFor(() => {
        expect(message.error).toHaveBeenCalledWith('Network error');
      });
    });

    it('should handle query execution errors', async () => {
      const mockDatabases = [
        {
          id: '1',
          name: 'test_db',
          url: 'postgresql://user:pass@localhost:5432/testdb',
          description: 'Test database',
          is_active: true,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        },
      ];

      mockApiClient.getDatabases.mockResolvedValue(mockDatabases);
      mockApiClient.executeQuery.mockRejectedValue(new Error('SQL syntax error'));

      renderApp();

      // Navigate to query page and select database
      const queryLink = screen.getByText('Query');
      await user.click(queryLink);

      const databaseSelect = screen.getByRole('combobox');
      await user.click(databaseSelect);
      const databaseOption = screen.getByText('test_db - Test database');
      await user.click(databaseOption);

      // Enter invalid SQL
      const queryEditor = screen.getByRole('textbox');
      await user.type(queryEditor, 'INVALID SQL');

      // Execute query
      const executeButton = screen.getByRole('button', { name: /execute/i });
      await user.click(executeButton);

      // Should show error message
      await waitFor(() => {
        expect(message.error).toHaveBeenCalledWith('SQL syntax error');
      });
    });

    it('should handle natural language processing errors', async () => {
      const mockDatabases = [
        {
          id: '1',
          name: 'test_db',
          url: 'postgresql://user:pass@localhost:5432/testdb',
          description: 'Test database',
          is_active: true,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        },
      ];

      mockApiClient.getDatabases.mockResolvedValue(mockDatabases);
      mockApiClient.executeNaturalLanguageQuery.mockRejectedValue(
        new Error('Unable to generate SQL from prompt')
      );

      renderApp();

      // Navigate to query page and select database
      const queryLink = screen.getByText('Query');
      await user.click(queryLink);

      const databaseSelect = screen.getByRole('combobox');
      await user.click(databaseSelect);
      const databaseOption = screen.getByText('test_db - Test database');
      await user.click(databaseOption);

      // Enter natural language query
      const nlInput = screen.getByPlaceholderText(/describe what you want to query/i);
      await user.type(nlInput, 'Complex ambiguous query');

      // Submit natural language query
      const nlSubmitButton = screen.getByRole('button', { name: /generate sql/i });
      await user.click(nlSubmitButton);

      // Should show error message
      await waitFor(() => {
        expect(message.error).toHaveBeenCalledWith('Unable to generate SQL from prompt');
      });
    });
  });

  describe('State Management Integration', () => {
    it('should maintain state consistency across page navigation', async () => {
      const mockDatabases = [
        {
          id: '1',
          name: 'test_db',
          url: 'postgresql://user:pass@localhost:5432/testdb',
          description: 'Test database',
          is_active: true,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        },
      ];

      mockApiClient.getDatabases.mockResolvedValue(mockDatabases);

      renderApp();

      // Start on databases page
      await waitFor(() => {
        expect(screen.getByText('test_db')).toBeInTheDocument();
      });

      // Navigate to query page
      const queryLink = screen.getByText('Query');
      await user.click(queryLink);

      // Should still have databases loaded
      await waitFor(() => {
        const databaseSelect = screen.getByRole('combobox');
        expect(databaseSelect).toBeInTheDocument();
      });

      // Navigate back to databases page
      const databasesLink = screen.getByText('Databases');
      await user.click(databasesLink);

      // Should still show databases without reloading
      expect(screen.getByText('test_db')).toBeInTheDocument();
      
      // Should not call getDatabases again (already loaded)
      expect(mockApiClient.getDatabases).toHaveBeenCalledTimes(1);
    });

    it('should update state when database is added from databases page', async () => {
      const initialDatabases: any[] = [];
      const newDatabase = {
        id: '1',
        name: 'new_db',
        url: 'postgresql://user:pass@localhost:5432/newdb',
        description: 'New database',
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      mockApiClient.getDatabases.mockResolvedValue(initialDatabases);
      mockApiClient.createDatabase.mockResolvedValue(newDatabase);

      renderApp();

      // Add database
      const addButton = screen.getByRole('button', { name: /add/i });
      await user.click(addButton);

      // Fill form and submit
      const nameInput = screen.getByLabelText(/database name/i);
      await user.type(nameInput, 'new_db');
      
      const urlInput = screen.getByLabelText(/database url/i);
      await user.type(urlInput, 'postgresql://user:pass@localhost:5432/newdb');

      const submitButton = screen.getByRole('button', { name: /add database/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockApiClient.createDatabase).toHaveBeenCalled();
      });

      // Navigate to query page
      const queryLink = screen.getByText('Query');
      await user.click(queryLink);

      // Should see new database in dropdown
      const databaseSelect = screen.getByRole('combobox');
      await user.click(databaseSelect);

      await waitFor(() => {
        expect(screen.getByText('new_db - New database')).toBeInTheDocument();
      });
    });
  });
});