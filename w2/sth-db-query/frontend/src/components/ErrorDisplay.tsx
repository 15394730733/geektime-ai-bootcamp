/**
 * ErrorDisplay Component
 * 
 * Provides consistent error display formatting across all components.
 * Handles different error types and provides user-friendly messaging.
 */

import React from 'react';
import { Alert, Button, Collapse, Typography } from 'antd';
import { ExclamationCircleOutlined, InfoCircleOutlined, WarningOutlined } from '@ant-design/icons';

const { Text, Paragraph } = Typography;
const { Panel } = Collapse;

// Error types that match backend error categories
export enum ErrorCategory {
  NETWORK = 'network',
  AUTHENTICATION = 'authentication',
  CONFIGURATION = 'configuration',
  VALIDATION = 'validation',
  SYNTAX = 'syntax',
  PERMISSION = 'permission',
  TIMEOUT = 'timeout',
  RESOURCE = 'resource',
  LLM_SERVICE = 'llm_service',
  INTERNAL = 'internal'
}

export enum ErrorSeverity {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical'
}

export interface ErrorInfo {
  category: ErrorCategory;
  severity: ErrorSeverity;
  code: string;
  message: string;
  userMessage: string;
  technicalDetails?: string;
  suggestions?: string[];
  context?: Record<string, any>;
}

export interface ErrorDisplayProps {
  error: string | ErrorInfo | Error;
  title?: string;
  showDetails?: boolean;
  onDismiss?: () => void;
  className?: string;
  style?: React.CSSProperties;
}

/**
 * Parse error from various formats into structured ErrorInfo
 */
function parseError(error: string | ErrorInfo | Error): ErrorInfo {
  // If it's already structured error info
  if (typeof error === 'object' && error !== null && 'category' in error) {
    return error as ErrorInfo;
  }

  // If it's an Error object
  if (error instanceof Error) {
    return {
      category: ErrorCategory.INTERNAL,
      severity: ErrorSeverity.MEDIUM,
      code: 'INTERNAL_ERROR',
      message: error.message,
      userMessage: 'An unexpected error occurred. Please try again.',
      suggestions: ['Refresh the page and try again', 'Contact support if the issue persists'],
      technicalDetails: error.stack
    };
  }

  // If it's a string, try to parse it as JSON (from API responses)
  if (typeof error === 'string') {
    try {
      const parsed = JSON.parse(error);
      if (parsed.error && typeof parsed.error === 'object') {
        return {
          category: parsed.error.category || ErrorCategory.INTERNAL,
          severity: parsed.error.severity || ErrorSeverity.MEDIUM,
          code: parsed.error.code || 'UNKNOWN_ERROR',
          message: parsed.error.message || parsed.message || error,
          userMessage: parsed.error.userMessage || parsed.message || error,
          suggestions: parsed.error.suggestions || [],
          technicalDetails: parsed.error.technicalDetails,
          context: parsed.error.context
        };
      }
    } catch {
      // Not JSON, treat as plain string
    }

    return {
      category: ErrorCategory.INTERNAL,
      severity: ErrorSeverity.MEDIUM,
      code: 'UNKNOWN_ERROR',
      message: error,
      userMessage: error,
      suggestions: ['Please try again', 'Contact support if the issue persists']
    };
  }

  // Fallback
  return {
    category: ErrorCategory.INTERNAL,
    severity: ErrorSeverity.MEDIUM,
    code: 'UNKNOWN_ERROR',
    message: 'An unknown error occurred',
    userMessage: 'An unexpected error occurred. Please try again.',
    suggestions: ['Refresh the page and try again', 'Contact support if the issue persists']
  };
}

/**
 * Get Alert type based on error severity
 */
function getAlertType(severity: ErrorSeverity): 'error' | 'warning' | 'info' {
  switch (severity) {
    case ErrorSeverity.CRITICAL:
    case ErrorSeverity.HIGH:
      return 'error';
    case ErrorSeverity.MEDIUM:
      return 'warning';
    case ErrorSeverity.LOW:
    default:
      return 'info';
  }
}

/**
 * Get icon based on error category
 */
function getErrorIcon(category: ErrorCategory) {
  switch (category) {
    case ErrorCategory.NETWORK:
    case ErrorCategory.TIMEOUT:
      return <ExclamationCircleOutlined />;
    case ErrorCategory.AUTHENTICATION:
    case ErrorCategory.PERMISSION:
      return <WarningOutlined />;
    case ErrorCategory.VALIDATION:
    case ErrorCategory.SYNTAX:
    case ErrorCategory.CONFIGURATION:
      return <InfoCircleOutlined />;
    default:
      return <ExclamationCircleOutlined />;
  }
}

/**
 * Get user-friendly category name
 */
function getCategoryDisplayName(category: ErrorCategory): string {
  switch (category) {
    case ErrorCategory.NETWORK:
      return 'Connection Error';
    case ErrorCategory.AUTHENTICATION:
      return 'Authentication Error';
    case ErrorCategory.CONFIGURATION:
      return 'Configuration Error';
    case ErrorCategory.VALIDATION:
      return 'Validation Error';
    case ErrorCategory.SYNTAX:
      return 'SQL Syntax Error';
    case ErrorCategory.PERMISSION:
      return 'Permission Error';
    case ErrorCategory.TIMEOUT:
      return 'Timeout Error';
    case ErrorCategory.RESOURCE:
      return 'Resource Error';
    case ErrorCategory.LLM_SERVICE:
      return 'AI Service Error';
    case ErrorCategory.INTERNAL:
    default:
      return 'System Error';
  }
}

export const ErrorDisplay: React.FC<ErrorDisplayProps> = ({
  error,
  title,
  showDetails = false,
  onDismiss,
  className,
  style
}) => {
  const errorInfo = parseError(error);
  const alertType = getAlertType(errorInfo.severity);
  const displayTitle = title || getCategoryDisplayName(errorInfo.category);

  const renderSuggestions = () => {
    if (!errorInfo.suggestions || errorInfo.suggestions.length === 0) {
      return null;
    }

    return (
      <div style={{ marginTop: 12 }}>
        <Text strong>Suggestions:</Text>
        <ul style={{ marginTop: 4, marginBottom: 0, paddingLeft: 20 }}>
          {errorInfo.suggestions.map((suggestion, index) => (
            <li key={index}>
              <Text>{suggestion}</Text>
            </li>
          ))}
        </ul>
      </div>
    );
  };

  const renderTechnicalDetails = () => {
    if (!showDetails || !errorInfo.technicalDetails) {
      return null;
    }

    return (
      <Collapse size="small" style={{ marginTop: 12 }}>
        <Panel header="Technical Details" key="1">
          <Text code style={{ fontSize: '12px', wordBreak: 'break-all' }}>
            {errorInfo.technicalDetails}
          </Text>
        </Panel>
      </Collapse>
    );
  };

  const renderContext = () => {
    if (!showDetails || !errorInfo.context || Object.keys(errorInfo.context).length === 0) {
      return null;
    }

    return (
      <Collapse size="small" style={{ marginTop: 8 }}>
        <Panel header="Error Context" key="1">
          <pre style={{ fontSize: '12px', margin: 0, whiteSpace: 'pre-wrap' }}>
            {JSON.stringify(errorInfo.context, null, 2)}
          </pre>
        </Panel>
      </Collapse>
    );
  };

  return (
    <Alert
      type={alertType}
      showIcon
      icon={getErrorIcon(errorInfo.category)}
      message={displayTitle}
      description={
        <div>
          <Paragraph style={{ marginBottom: 0 }}>
            {errorInfo.userMessage}
          </Paragraph>
          {renderSuggestions()}
          {renderTechnicalDetails()}
          {renderContext()}
        </div>
      }
      closable={!!onDismiss}
      onClose={onDismiss}
      className={className}
      style={style}
      action={
        showDetails && errorInfo.code ? (
          <Text type="secondary" style={{ fontSize: '12px' }}>
            Error Code: {errorInfo.code}
          </Text>
        ) : undefined
      }
    />
  );
};

/**
 * Compact error display for inline use
 */
export const CompactErrorDisplay: React.FC<{
  error: string | ErrorInfo | Error;
  onDismiss?: () => void;
}> = ({ error, onDismiss }) => {
  const errorInfo = parseError(error);
  const alertType = getAlertType(errorInfo.severity);

  return (
    <Alert
      type={alertType}
      message={errorInfo.userMessage}
      showIcon
      closable={!!onDismiss}
      onClose={onDismiss}
      style={{ marginBottom: 16 }}
    />
  );
};

/**
 * Error boundary component for catching React errors
 */
interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends React.Component<
  React.PropsWithChildren<{ fallback?: React.ComponentType<{ error: Error }> }>,
  ErrorBoundaryState
> {
  constructor(props: React.PropsWithChildren<{ fallback?: React.ComponentType<{ error: Error }> }>) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError && this.state.error) {
      if (this.props.fallback) {
        const FallbackComponent = this.props.fallback;
        return <FallbackComponent error={this.state.error} />;
      }

      return (
        <ErrorDisplay
          error={this.state.error}
          title="Application Error"
          showDetails={true}
        />
      );
    }

    return this.props.children;
  }
}

export default ErrorDisplay;