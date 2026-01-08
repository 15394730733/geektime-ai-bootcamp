/**
 * DatabaseList Component Tests
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { DatabaseList } from '../DatabaseList';
import { DatabaseConnection } from '../../services/api';

const mockDatabases: DatabaseConnection[] = [
  {
    id: '1',
    name: 'test-db-1',
    url: 'postgresql://user:pass@localhost:5432/testdb1',
    description: 'Test database 1',
    isActive: true,
    createdAt: '2024-01-01T10:00:00Z',
    updatedAt: '2024-01-01T12:00:00Z',
  },
  {
    id: '2',
    name: 'test-db-2',
    url: 'postgresql://user:pass@localhost:5432/testdb2',
    description: 'Test database 2',
    isActive: false,
    createdAt: '2024-01-01T10:00:00Z',
    updatedAt: '2024-01-01T11:00:00Z',
  },
  {
    id: '3',
    name: 'test-db-3',
    url: 'postgresql://user:pass@localhost:5432/testdb3',
    description: '',
    isActive: true,
    createdAt: '2024-01-01T10:00:00Z',
    updatedAt: '2024-01-01T13:00:00Z',
  },
];

describe('DatabaseList Component', () => {
  const mockOnSelect = vi.fn();
  const mockOnRefresh = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders database list with connections', () => {
    render(
      <DatabaseList
        databases={mockDatabases}
        onSelect={mockOnSelect}
        onRefresh={mockOnRefresh}
      />
    );

    // Check if title is rendered
    expect(screen.getByText('Database Connections')).toBeInTheDocument();

    // Check if all databases are rendered
    expect(screen.getByText('test-db-1')).toBeInTheDocument();
    expect(screen.getByText('test-db-2')).toBeInTheDocument();
    expect(screen.getByText('test-db-3')).toBeInTheDocument();

    // Check descriptions
    expect(screen.getByText('Test database 1')).toBeInTheDocument();
    expect(screen.getByText('Test database 2')).toBeInTheDocument();
  });

  it('renders empty state when no databases', () => {
    render(
      <DatabaseList
        databases={[]}
        onSelect={mockOnSelect}
      />
    );

    expect(screen.getByText('No Database Connections')).toBeInTheDocument();
    expect(screen.getByText('Add your first database connection to get started')).toBeInTheDocument();
  });

  it('shows loading state', () => {
    render(
      <DatabaseList
        databases={[]}
        loading={true}
        onSelect={mockOnSelect}
      />
    );

    // Ant Design List component shows loading spinner
    expect(document.querySelector('.ant-spin')).toBeInTheDocument();
  });

  it('displays connection status correctly', () => {
    render(
      <DatabaseList
        databases={mockDatabases}
        onSelect={mockOnSelect}
      />
    );

    // Check for active status
    const activeStatuses = screen.getAllByText('Active');
    expect(activeStatuses).toHaveLength(2); // test-db-1 and test-db-3

    // Check for inactive status
    const inactiveStatuses = screen.getAllByText('Inactive');
    expect(inactiveStatuses).toHaveLength(1); // test-db-2
  });

  it('highlights selected database', () => {
    render(
      <DatabaseList
        databases={mockDatabases}
        selectedDatabase="test-db-1"
        onSelect={mockOnSelect}
      />
    );

    // Check if selected badge is shown
    expect(screen.getByText('Selected')).toBeInTheDocument();
  });

  it('calls onSelect when database is clicked', () => {
    render(
      <DatabaseList
        databases={mockDatabases}
        onSelect={mockOnSelect}
      />
    );

    // Click on first database
    const firstDatabase = screen.getByText('test-db-1').closest('.ant-card');
    expect(firstDatabase).toBeInTheDocument();
    
    fireEvent.click(firstDatabase!);
    
    expect(mockOnSelect).toHaveBeenCalledWith(mockDatabases[0]);
  });

  it('calls onRefresh when refresh button is clicked', () => {
    render(
      <DatabaseList
        databases={mockDatabases}
        onSelect={mockOnSelect}
        onRefresh={mockOnRefresh}
      />
    );

    const refreshButton = screen.getByText('Refresh');
    fireEvent.click(refreshButton);
    
    expect(mockOnRefresh).toHaveBeenCalled();
  });

  it('does not show refresh button when onRefresh is not provided', () => {
    render(
      <DatabaseList
        databases={mockDatabases}
        onSelect={mockOnSelect}
      />
    );

    expect(screen.queryByText('Refresh')).not.toBeInTheDocument();
  });

  it('handles databases without descriptions', () => {
    const dbWithoutDescription: DatabaseConnection = {
      id: '4',
      name: 'no-desc-db',
      url: 'postgresql://user:pass@localhost:5432/nodb',
      description: '',
      isActive: true,
      createdAt: '2024-01-01T10:00:00Z',
      updatedAt: '2024-01-01T12:00:00Z',
    };

    render(
      <DatabaseList
        databases={[dbWithoutDescription]}
        onSelect={mockOnSelect}
      />
    );

    expect(screen.getByText('no-desc-db')).toBeInTheDocument();
  });

  it('handles databases without updatedAt timestamp', () => {
    const dbWithoutTimestamp: DatabaseConnection = {
      id: '5',
      name: 'no-timestamp-db',
      url: 'postgresql://user:pass@localhost:5432/nodb',
      description: 'No timestamp',
      isActive: true,
      createdAt: '2024-01-01T10:00:00Z',
      updatedAt: '',
    };

    render(
      <DatabaseList
        databases={[dbWithoutTimestamp]}
        onSelect={mockOnSelect}
      />
    );

    expect(screen.getByText('no-timestamp-db')).toBeInTheDocument();
    expect(screen.getByText('No timestamp')).toBeInTheDocument();
  });

  it('formats last connected time correctly', () => {
    // Create a database with a recent timestamp
    const recentTime = new Date(Date.now() - 2 * 60 * 60 * 1000); // 2 hours ago
    const recentDb: DatabaseConnection = {
      id: '6',
      name: 'recent-db',
      url: 'postgresql://user:pass@localhost:5432/recent',
      description: 'Recent database',
      isActive: true,
      createdAt: '2024-01-01T10:00:00Z',
      updatedAt: recentTime.toISOString(),
    };

    render(
      <DatabaseList
        databases={[recentDb]}
        onSelect={mockOnSelect}
      />
    );

    expect(screen.getByText('recent-db')).toBeInTheDocument();
    // Should show "2 hours ago" or similar
    expect(screen.getByText(/hours? ago/)).toBeInTheDocument();
  });
});