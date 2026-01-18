/**
 * Tests for MobileMetadataDrawer component
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { vi } from 'vitest';
import { MobileMetadataDrawer, MobileMetadataToggle } from '../MobileMetadataDrawer';

// Mock the MetadataPanel component to avoid complex dependencies
vi.mock('../MetadataPanel', () => ({
  MetadataPanel: ({ onTableClick, onColumnClick }: any) => (
    <div data-testid="metadata-panel">
      <button onClick={() => onTableClick('public', 'users')}>
        Click Table
      </button>
      <button onClick={() => onColumnClick('public', 'users', 'id')}>
        Click Column
      </button>
    </div>
  ),
}));

describe('MobileMetadataDrawer', () => {
  const defaultProps = {
    visible: true,
    onClose: vi.fn(),
    databaseName: 'test-db',
    metadata: null,
    loading: false,
    onTableClick: vi.fn(),
    onColumnClick: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render drawer when visible', () => {
    render(<MobileMetadataDrawer {...defaultProps} />);
    
    expect(screen.getByText('Database Schema')).toBeInTheDocument();
    expect(screen.getByTestId('metadata-panel')).toBeInTheDocument();
  });

  it('should not render drawer when not visible', () => {
    render(<MobileMetadataDrawer {...defaultProps} visible={false} />);
    
    expect(screen.queryByText('Database Schema')).not.toBeInTheDocument();
  });

  it('should call onClose when close button is clicked', () => {
    render(<MobileMetadataDrawer {...defaultProps} />);
    
    const closeButton = screen.getByLabelText('Close');
    fireEvent.click(closeButton);
    
    expect(defaultProps.onClose).toHaveBeenCalledTimes(1);
  });

  it('should call onTableClick and onClose when table is clicked', () => {
    render(<MobileMetadataDrawer {...defaultProps} />);
    
    const tableButton = screen.getByText('Click Table');
    fireEvent.click(tableButton);
    
    expect(defaultProps.onTableClick).toHaveBeenCalledWith('public', 'users');
    expect(defaultProps.onClose).toHaveBeenCalledTimes(1);
  });

  it('should call onColumnClick and onClose when column is clicked', () => {
    render(<MobileMetadataDrawer {...defaultProps} />);
    
    const columnButton = screen.getByText('Click Column');
    fireEvent.click(columnButton);
    
    expect(defaultProps.onColumnClick).toHaveBeenCalledWith('public', 'users', 'id');
    expect(defaultProps.onClose).toHaveBeenCalledTimes(1);
  });
});

describe('MobileMetadataToggle', () => {
  it('should render toggle button', () => {
    const onClick = vi.fn();
    render(<MobileMetadataToggle onClick={onClick} />);
    
    expect(screen.getByText('Schema')).toBeInTheDocument();
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('should call onClick when button is clicked', () => {
    const onClick = vi.fn();
    render(<MobileMetadataToggle onClick={onClick} />);
    
    const button = screen.getByRole('button');
    fireEvent.click(button);
    
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it('should apply custom className', () => {
    const onClick = vi.fn();
    render(<MobileMetadataToggle onClick={onClick} className="custom-class" />);
    
    const button = screen.getByRole('button');
    expect(button).toHaveClass('mobile-metadata-toggle');
    expect(button).toHaveClass('custom-class');
  });
});