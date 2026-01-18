/**
 * TabBar Component Tests
 */

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { TabBar } from '../TabBar';
import { QueryTab } from '../../types/layout';

// Mock Ant Design Modal to avoid issues with portal rendering
vi.mock('antd', async () => {
  const actual = await vi.importActual('antd');
  return {
    ...actual,
    Modal: {
      confirm: vi.fn((config) => {
        // Simulate immediate confirmation for testing
        if (config.onOk) {
          config.onOk();
        }
      }),
    },
  };
});

describe('TabBar Component', () => {
  const mockOnTabChange = vi.fn();
  const mockOnTabCreate = vi.fn();
  const mockOnTabClose = vi.fn();

  const createMockTab = (id: string, name: string, isDirty = false): QueryTab => ({
    id,
    name,
    query: 'SELECT * FROM test',
    results: null,
    isDirty,
    createdAt: new Date(),
  });

  const defaultProps = {
    tabs: [
      createMockTab('tab1', 'Query 1'),
      createMockTab('tab2', 'Query 2'),
    ],
    activeTabId: 'tab1',
    databaseName: 'test_database',
    onTabChange: mockOnTabChange,
    onTabCreate: mockOnTabCreate,
    onTabClose: mockOnTabClose,
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('database name header is not rendered (as requested by user)', () => {
    render(<TabBar {...defaultProps} />);

    expect(screen.queryByText('Database: test_database')).not.toBeInTheDocument();
  });

  it('"No database selected" text is not displayed when database name is null (as requested by user)', () => {
    render(<TabBar {...defaultProps} databaseName={null} />);

    expect(screen.queryByText('No database selected')).not.toBeInTheDocument();
  });

  it('renders all tabs', () => {
    render(<TabBar {...defaultProps} />);

    expect(screen.getByText('Query 1')).toBeInTheDocument();
    expect(screen.getByText('Query 2')).toBeInTheDocument();
  });

  it('shows unsaved changes indicator for dirty tabs', () => {
    const tabsWithDirty = [
      createMockTab('tab1', 'Query 1', true),
      createMockTab('tab2', 'Query 2', false),
    ];

    render(<TabBar {...defaultProps} tabs={tabsWithDirty} />);

    // Check for the dirty indicator (bullet point)
    const dirtyTab = screen.getByText('Query 1').closest('.ant-tabs-tab');
    expect(dirtyTab).toHaveTextContent('•');

    const cleanTab = screen.getByText('Query 2').closest('.ant-tabs-tab');
    expect(cleanTab).not.toHaveTextContent('•');
  });

  it('calls onTabChange when tab is clicked', async () => {
    const user = userEvent.setup();
    render(<TabBar {...defaultProps} />);

    const tab2 = screen.getByText('Query 2');
    await user.click(tab2);

    expect(mockOnTabChange).toHaveBeenCalledWith('tab2');
  });

  it('calls onTabCreate when add button is clicked', async () => {
    const user = userEvent.setup();
    render(<TabBar {...defaultProps} />);

    // Find the add button (plus icon)
    const addButton = screen.getByRole('button', { name: /add/i });
    await user.click(addButton);

    expect(mockOnTabCreate).toHaveBeenCalled();
  });

  it('allows closing tabs when there are multiple tabs', () => {
    render(<TabBar {...defaultProps} />);

    // Both tabs should be closable when there are multiple tabs
    const removeButtons = screen.getAllByLabelText('remove');
    expect(removeButtons).toHaveLength(2);
    removeButtons.forEach(button => {
      expect(button).toBeInTheDocument();
    });
  });

  it('prevents closing the last tab', () => {
    const singleTabProps = {
      ...defaultProps,
      tabs: [createMockTab('tab1', 'Query 1')],
    };

    render(<TabBar {...singleTabProps} />);

    // Should not have any remove buttons when there's only one tab
    const removeButtons = screen.queryAllByLabelText('remove');
    expect(removeButtons).toHaveLength(0);
  });

  it('closes clean tab without confirmation', async () => {
    const user = userEvent.setup();
    render(<TabBar {...defaultProps} />);

    // Find and click the remove button for the first tab
    const removeButtons = screen.getAllByLabelText('remove');
    await user.click(removeButtons[0]);

    expect(mockOnTabClose).toHaveBeenCalledWith('tab1');
  });

  it('shows confirmation dialog for dirty tab before closing', async () => {
    const user = userEvent.setup();
    const tabsWithDirty = [
      createMockTab('tab1', 'Query 1', true),
      createMockTab('tab2', 'Query 2', false),
    ];

    render(<TabBar {...defaultProps} tabs={tabsWithDirty} />);

    // Find and click the remove button for the dirty tab
    const removeButtons = screen.getAllByLabelText('remove');
    await user.click(removeButtons[0]);

    // The mock Modal.confirm should have been called and onTabClose should be called
    expect(mockOnTabClose).toHaveBeenCalledWith('tab1');
  });

  it('applies correct styling classes', () => {
    render(<TabBar {...defaultProps} />);

    // Check the main container by finding the tablist and going up
    const tabList = screen.getByRole('tablist');
    const mainContainer = tabList.closest('.border-b.border-gray-200.bg-white');
    expect(mainContainer).toBeInTheDocument();
  });

  it('handles empty tabs array gracefully', () => {
    const emptyTabsProps = {
      ...defaultProps,
      tabs: [],
      activeTabId: '',
    };

    render(<TabBar {...emptyTabsProps} />);

    // Should still render the tabs container even with no tabs
    expect(screen.getByRole('tablist')).toBeInTheDocument();
  });

  it('highlights active tab correctly', () => {
    render(<TabBar {...defaultProps} />);

    const activeTab = screen.getByText('Query 1').closest('.ant-tabs-tab');
    expect(activeTab).toHaveClass('ant-tabs-tab-active');

    const inactiveTab = screen.getByText('Query 2').closest('.ant-tabs-tab');
    expect(inactiveTab).not.toHaveClass('ant-tabs-tab-active');
  });

  it('database information is not displayed in header (as requested by user)', () => {
    render(<TabBar {...defaultProps} />);

    // Check that database name is not displayed (as per user request to hide it)
    expect(screen.queryByText('Database: test_database')).not.toBeInTheDocument();
    expect(screen.queryByText('No database selected')).not.toBeInTheDocument();
  });
});