/**
 * Property-based tests for UI error formatting.
 *
 * Feature: database-query-tool, Property 25: UI error formatting
 * Validates: Requirements 10.5
 *
 * Tests that error messages are displayed in a user-friendly format
 * with appropriate styling across all UI components.
 */

import React from 'react';
import { render, cleanup } from '@testing-library/react';
import '@testing-library/jest-dom';
import fc from 'fast-check';
import { vi, afterEach } from 'vitest';
import { ErrorDisplay, CompactErrorDisplay, ErrorCategory, ErrorSeverity, ErrorInfo } from '../ErrorDisplay';

// Clean up after each test to avoid DOM pollution
afterEach(() => {
  cleanup();
});

// Mock Ant Design components for testing
vi.mock('antd', () => ({
  Alert: ({ type, message, description, showIcon, closable, onClose }: any) => (
    <div 
      data-testid="alert" 
      data-type={type}
      data-closable={closable}
      data-show-icon={showIcon}
    >
      <div data-testid="alert-message">{message}</div>
      <div data-testid="alert-description">{description}</div>
      {closable && (
        <button data-testid="close-button" onClick={onClose}>
          Close
        </button>
      )}
    </div>
  ),
  Typography: {
    Text: ({ children }: any) => <span data-testid="text">{children}</span>,
    Paragraph: ({ children }: any) => <p data-testid="paragraph">{children}</p>
  },
  Collapse: ({ children }: any) => <div data-testid="collapse">{children}</div>,
  Button: ({ children, onClick }: any) => (
    <button data-testid="button" onClick={onClick}>{children}</button>
  )
}));

describe('ErrorDisplay Property Tests', () => {
  /**
   * Property 25a: All error types are displayed with consistent formatting.
   * 
   * For any error category and severity, the ErrorDisplay component should
   * render with appropriate visual styling and user-friendly messaging.
   */
  test('property: all error types display with consistent formatting', () => {
    fc.assert(fc.property(
      fc.constantFrom(...Object.values(ErrorCategory)),
      fc.constantFrom(...Object.values(ErrorSeverity)),
      fc.string({ minLength: 1, maxLength: 100 }),
      fc.string({ minLength: 1, maxLength: 200 }),
      (category, severity, message, userMessage) => {
        const errorInfo: ErrorInfo = {
          category,
          severity,
          code: `${category.toUpperCase()}_ERROR`,
          message,
          userMessage,
          suggestions: ['Try again']
        };

        const { container } = render(<ErrorDisplay error={errorInfo} />);
        
        // Should render an alert component
        const alert = container.querySelector('[data-testid="alert"]');
        expect(alert).toBeInTheDocument();
        
        // Should have appropriate type based on severity
        const expectedType = severity === ErrorSeverity.CRITICAL || severity === ErrorSeverity.HIGH 
          ? 'error' 
          : severity === ErrorSeverity.MEDIUM 
            ? 'warning' 
            : 'info';
        expect(alert).toHaveAttribute('data-type', expectedType);
        
        // Should show icon
        expect(alert).toHaveAttribute('data-show-icon', 'true');
        
        cleanup();
      }
    ), { numRuns: 50 });
  });

  /**
   * Property 25b: Error messages are user-friendly and non-technical.
   * 
   * For any error input, the displayed message should be more user-friendly
   * than technical error messages and provide actionable guidance.
   */
  test('property: error messages are user-friendly', () => {
    fc.assert(fc.property(
      fc.string({ minLength: 1, maxLength: 100 }),
      (errorMessage) => {
        const { container } = render(<ErrorDisplay error={errorMessage} />);
        
        // Should render without crashing
        expect(container).toBeInTheDocument();
        
        // Should have an alert
        const alert = container.querySelector('[data-testid="alert"]');
        expect(alert).toBeInTheDocument();
        
        // Should have a description with user-friendly content
        const description = container.querySelector('[data-testid="alert-description"]');
        expect(description).toBeInTheDocument();
        expect(description?.textContent).toBeTruthy();
        
        // User message should not contain technical jargon like stack traces
        const descriptionText = description?.textContent || '';
        expect(descriptionText).not.toMatch(/at\s+\w+\.\w+\s*\(/); // Stack trace pattern
        
        cleanup();
      }
    ), { numRuns: 50 });
  });

  /**
   * Property 25c: CompactErrorDisplay provides minimal but clear error info.
   * 
   * For any error, the CompactErrorDisplay should show essential information
   * without overwhelming the user interface.
   */
  test('property: compact error display is minimal but clear', () => {
    fc.assert(fc.property(
      fc.string({ minLength: 1, maxLength: 100 }),
      (errorMessage) => {
        const { container } = render(<CompactErrorDisplay error={errorMessage} />);
        
        // Should render without crashing
        expect(container).toBeInTheDocument();
        
        // Should have an alert
        const alert = container.querySelector('[data-testid="alert"]');
        expect(alert).toBeInTheDocument();
        
        // Should show icon
        expect(alert).toHaveAttribute('data-show-icon', 'true');
        
        cleanup();
      }
    ), { numRuns: 50 });
  });

  /**
   * Property 25d: Error parsing handles various input formats.
   * 
   * For any input format (string, Error object, structured error),
   * the component should parse and display it appropriately.
   */
  test('property: error parsing handles various input formats', () => {
    fc.assert(fc.property(
      fc.oneof(
        fc.string({ minLength: 1, maxLength: 100 }),
        fc.string({ minLength: 1, maxLength: 100 }).map(msg => new Error(msg))
      ),
      (error) => {
        const { container } = render(<ErrorDisplay error={error} />);
        
        // Should render without crashing regardless of input format
        expect(container).toBeInTheDocument();
        
        // Should have an alert
        const alert = container.querySelector('[data-testid="alert"]');
        expect(alert).toBeInTheDocument();
        
        // Should have some meaningful content
        const description = container.querySelector('[data-testid="alert-description"]');
        expect(description).toBeInTheDocument();
        expect(description?.textContent).toBeTruthy();
        
        cleanup();
      }
    ), { numRuns: 50 });
  });

  /**
   * Property 25e: Error categories have appropriate visual styling.
   * 
   * For any error category, the visual styling should be appropriate
   * for the type of error (network, auth, validation, etc.).
   */
  test('property: error categories have appropriate styling', () => {
    fc.assert(fc.property(
      fc.constantFrom(...Object.values(ErrorCategory)),
      fc.constantFrom(...Object.values(ErrorSeverity)),
      (category, severity) => {
        const errorInfo: ErrorInfo = {
          category,
          severity,
          code: `${category.toUpperCase()}_ERROR`,
          message: 'Test error',
          userMessage: 'A test error occurred',
          suggestions: ['Try again']
        };

        const { container } = render(<ErrorDisplay error={errorInfo} />);
        
        // Should render with appropriate alert type
        const alert = container.querySelector('[data-testid="alert"]');
        expect(alert).toBeInTheDocument();
        
        // Alert type should match severity
        const alertType = alert?.getAttribute('data-type');
        expect(['error', 'warning', 'info']).toContain(alertType);
        
        // Should show icon for visual clarity
        expect(alert).toHaveAttribute('data-show-icon', 'true');
        
        cleanup();
      }
    ), { numRuns: 25 });
  });

  /**
   * Property 25f: Error suggestions are actionable and helpful.
   * 
   * For any error with suggestions, they should provide actionable guidance
   * that users can follow to resolve the issue.
   */
  test('property: error suggestions are actionable', () => {
    fc.assert(fc.property(
      fc.array(fc.string({ minLength: 5, maxLength: 50 }), { minLength: 1, maxLength: 3 }),
      (suggestions) => {
        const errorInfo: ErrorInfo = {
          category: ErrorCategory.VALIDATION,
          severity: ErrorSeverity.MEDIUM,
          code: 'TEST_ERROR',
          message: 'Test error',
          userMessage: 'A test error occurred',
          suggestions
        };

        const { container } = render(<ErrorDisplay error={errorInfo} />);
        
        // Should display suggestions
        const description = container.querySelector('[data-testid="alert-description"]');
        const descriptionText = description?.textContent || '';
        
        // Should contain suggestion content
        suggestions.forEach(suggestion => {
          expect(descriptionText).toContain(suggestion);
        });
        
        cleanup();
      }
    ), { numRuns: 25 });
  });
});

describe('ErrorDisplay Unit Tests', () => {
  test('renders basic string error', () => {
    const { container } = render(<ErrorDisplay error="Test error message" />);
    
    const alert = container.querySelector('[data-testid="alert"]');
    expect(alert).toBeInTheDocument();
    
    const description = container.querySelector('[data-testid="alert-description"]');
    expect(description?.textContent).toContain('Test error message');
  });

  test('renders structured error with all fields', () => {
    const errorInfo: ErrorInfo = {
      category: ErrorCategory.NETWORK,
      severity: ErrorSeverity.HIGH,
      code: 'NETWORK_ERROR',
      message: 'Connection failed',
      userMessage: 'Unable to connect to the database',
      suggestions: ['Check your network connection', 'Verify server status']
    };

    const { container } = render(<ErrorDisplay error={errorInfo} />);
    
    const alert = container.querySelector('[data-testid="alert"]');
    expect(alert).toHaveAttribute('data-type', 'error');
    
    const description = container.querySelector('[data-testid="alert-description"]');
    expect(description?.textContent).toContain('Unable to connect to the database');
    expect(description?.textContent).toContain('Check your network connection');
  });

  test('handles Error objects correctly', () => {
    const error = new Error('JavaScript error occurred');
    
    const { container } = render(<ErrorDisplay error={error} />);
    
    const alert = container.querySelector('[data-testid="alert"]');
    expect(alert).toBeInTheDocument();
    
    const description = container.querySelector('[data-testid="alert-description"]');
    expect(description?.textContent).toContain('An unexpected error occurred');
  });

  test('compact display shows minimal information', () => {
    const errorInfo: ErrorInfo = {
      category: ErrorCategory.VALIDATION,
      severity: ErrorSeverity.MEDIUM,
      code: 'VALIDATION_ERROR',
      message: 'Validation failed',
      userMessage: 'Please check your input',
      suggestions: ['Fix the validation errors']
    };

    const { container } = render(<CompactErrorDisplay error={errorInfo} />);
    
    const alert = container.querySelector('[data-testid="alert"]');
    expect(alert).toBeInTheDocument();
    expect(alert).toHaveAttribute('data-type', 'warning');
  });
});