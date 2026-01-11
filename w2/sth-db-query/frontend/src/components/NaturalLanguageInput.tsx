/**
 * Natural Language Query Input Component
 *
 * Input component for natural language queries that get converted to SQL
 */

import React, { useState } from 'react';
import { Card, Input, Button, Space, Typography, Divider } from 'antd';
import { SendOutlined, LoadingOutlined, PlayCircleOutlined, EditOutlined } from '@ant-design/icons';
import Editor from '@monaco-editor/react';
import { QueryResults } from './QueryResults';
import { CompactErrorDisplay } from './ErrorDisplay';
import { NaturalLanguageQueryResult } from '../services/api';

const { TextArea } = Input;
const { Text, Title } = Typography;

interface NaturalLanguageInputProps {
  onSubmit: (query: string) => Promise<NaturalLanguageQueryResult>;
  onExecuteSQL: (sql: string) => Promise<any>;
  loading?: boolean;
  placeholder?: string;
  error?: string | Error | null;
}

export const NaturalLanguageInput: React.FC<NaturalLanguageInputProps> = ({
  onSubmit,
  onExecuteSQL,
  loading = false,
  placeholder = "Describe what data you want to see...",
  error = null
}) => {
  const [query, setQuery] = useState('');
  const [generatedSQL, setGeneratedSQL] = useState('');
  const [isEditingSQL, setIsEditingSQL] = useState(false);
  const [queryResult, setQueryResult] = useState<NaturalLanguageQueryResult | null>(null);
  const [sqlExecutionLoading, setSqlExecutionLoading] = useState(false);
  const [sqlError, setSqlError] = useState<string | Error | null>(null);

  const handleSubmit = async () => {
    if (!query.trim()) return;

    try {
      setQueryResult(null);
      setSqlError(null);
      const result = await onSubmit(query.trim());
      setGeneratedSQL(result.generatedSql);
      setIsEditingSQL(false);
    } catch (error) {
      // Error handling is done in parent component
      setGeneratedSQL('');
      setQueryResult(null);
    }
  };

  const handleExecuteSQL = async () => {
    if (!generatedSQL.trim()) return;

    try {
      setSqlExecutionLoading(true);
      setSqlError(null);
      const result = await onExecuteSQL(generatedSQL);
      setQueryResult({
        generatedSql: generatedSQL,
        columns: result.columns,
        rows: result.rows,
        rowCount: result.rowCount,
        executionTimeMs: result.executionTimeMs,
        truncated: result.truncated
      });
    } catch (error) {
      setSqlError(error instanceof Error ? error : String(error));
      setQueryResult(null);
    } finally {
      setSqlExecutionLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSQLChange = (value: string | undefined) => {
    setGeneratedSQL(value || '');
  };

  const toggleSQLEdit = () => {
    setIsEditingSQL(!isEditingSQL);
  };

  return (
    <Space direction="vertical" style={{ width: '100%' }} size="large">
      {/* Natural Language Input */}
      <Card title="Natural Language Query">
        <Space direction="vertical" style={{ width: '100%' }}>
          <TextArea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={placeholder}
            autoSize={{ minRows: 3, maxRows: 6 }}
            disabled={loading}
          />
          <Space>
            <Button
              type="primary"
              icon={loading ? <LoadingOutlined /> : <SendOutlined />}
              onClick={handleSubmit}
              disabled={!query.trim() || loading}
              loading={loading}
            >
              {loading ? 'Converting...' : 'Convert to SQL'}
            </Button>
            <Text type="secondary">
              Press Enter to submit, Shift+Enter for new line
            </Text>
          </Space>
          
          {error && (
            <CompactErrorDisplay
              error={error}
              onDismiss={() => {
                // Parent component should handle error clearing
              }}
            />
          )}
        </Space>
      </Card>

      {/* Generated SQL Display and Editor */}
      {generatedSQL && (
        <Card
          title={
            <Space>
              <Title level={5} style={{ margin: 0 }}>Generated SQL</Title>
              <Button
                size="small"
                icon={<EditOutlined />}
                onClick={toggleSQLEdit}
                type={isEditingSQL ? "primary" : "default"}
              >
                {isEditingSQL ? 'View' : 'Edit'}
              </Button>
            </Space>
          }
          extra={
            <Button
              type="primary"
              icon={sqlExecutionLoading ? <LoadingOutlined /> : <PlayCircleOutlined />}
              onClick={handleExecuteSQL}
              disabled={!generatedSQL.trim() || sqlExecutionLoading}
              loading={sqlExecutionLoading}
            >
              Execute SQL
            </Button>
          }
        >
          {isEditingSQL ? (
            <div style={{ border: '1px solid #d9d9d9', borderRadius: '4px' }}>
              <Editor
                height={200}
                language="sql"
                value={generatedSQL}
                onChange={handleSQLChange}
                options={{
                  minimap: { enabled: false },
                  scrollBeyondLastLine: false,
                  fontSize: 14,
                  fontFamily: 'Monaco, Menlo, "Ubuntu Mono", monospace',
                  lineNumbers: 'on',
                  wordWrap: 'on',
                  tabSize: 2,
                  insertSpaces: true,
                  automaticLayout: true,
                  suggest: {
                    showKeywords: true,
                    showSnippets: true,
                    showFunctions: true
                  }
                }}
                theme="vs"
              />
            </div>
          ) : (
            <pre style={{
              background: '#f5f5f5',
              padding: '12px',
              borderRadius: '4px',
              overflow: 'auto',
              fontFamily: 'Monaco, Menlo, "Ubuntu Mono", monospace',
              fontSize: '14px',
              margin: 0
            }}>
              {generatedSQL}
            </pre>
          )}

          {sqlError && (
            <CompactErrorDisplay
              error={sqlError}
              onDismiss={() => setSqlError(null)}
            />
          )}
        </Card>
      )}

      {/* Query Results */}
      {queryResult && (
        <>
          <Divider />
          <QueryResults
            columns={queryResult.columns}
            rows={queryResult.rows}
            rowCount={queryResult.rowCount || 0}
            executionTimeMs={queryResult.executionTimeMs || 0}
            truncated={queryResult.truncated || false}
            loading={sqlExecutionLoading}
            query={generatedSQL}
          />
        </>
      )}
    </Space>
  );
};
