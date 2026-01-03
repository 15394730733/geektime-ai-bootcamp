/**
 * Query Execution Page
 *
 * Main page for SQL query execution and natural language queries
 */

import React, { useState } from 'react';
import { Row, Col, Card, Select, Space, Typography, message } from 'antd';
import { DatabaseOutlined } from '@ant-design/icons';

import { QueryEditor } from '../components/QueryEditor';
import { QueryResults } from '../components/QueryResults';
import { NaturalLanguageInput } from '../components/NaturalLanguageInput';
import { MetadataViewer } from '../components/MetadataViewer';
import { apiClient, DatabaseConnection, DatabaseMetadata } from '../services/api';

const { Title } = Typography;
const { Option } = Select;

export const QueryPage: React.FC = () => {
  const [selectedDatabase, setSelectedDatabase] = useState<string>('');
  const [databases, setDatabases] = useState<DatabaseConnection[]>([]);
  const [metadata, setMetadata] = useState<DatabaseMetadata | null>(null);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [metadataLoading, setMetadataLoading] = useState(false);

  // Load databases on component mount
  React.useEffect(() => {
    loadDatabases();
  }, []);

  // Load metadata when database changes
  React.useEffect(() => {
    if (selectedDatabase) {
      loadMetadata(selectedDatabase);
    } else {
      setMetadata(null);
    }
  }, [selectedDatabase]);

  const loadDatabases = async () => {
    try {
      const dbList = await apiClient.getDatabases();
      setDatabases(dbList.filter(db => db.is_active));
    } catch (error) {
      message.error('Failed to load databases');
    }
  };

  // Expose loadDatabases function globally for cross-page communication
  React.useEffect(() => {
    (window as any).refreshQueryPageDatabases = loadDatabases;
    return () => {
      delete (window as any).refreshQueryPageDatabases;
    };
  }, []);

  const loadMetadata = async (databaseName: string) => {
    setMetadataLoading(true);
    try {
      const meta = await apiClient.getDatabaseMetadata(databaseName);
      setMetadata(meta);
    } catch (error) {
      message.error('Failed to load database metadata');
      setMetadata(null);
    } finally {
      setMetadataLoading(false);
    }
  };

  const handleExecuteQuery = async () => {
    if (!selectedDatabase || !query.trim()) {
      message.warning('Please select a database and enter a query');
      return;
    }

    setLoading(true);
    try {
      console.log('Executing query:', query, 'on database:', selectedDatabase);
      const result = await apiClient.executeQuery(selectedDatabase, { sql: query });
      console.log('Query result:', result);
      setResults(result);
      message.success(`Query executed successfully (${result.execution_time_ms}ms)`);
    } catch (error: any) {
      console.error('Query execution error:', error);
      message.error(error.message || 'Query execution failed');
      setResults(null);
    } finally {
      setLoading(false);
    }
  };

  const handleNaturalLanguageQuery = async (prompt: string) => {
    if (!selectedDatabase) {
      message.warning('Please select a database first');
      return;
    }

    setLoading(true);
    try {
      const result = await apiClient.executeNaturalLanguageQuery(selectedDatabase, { prompt });
      setQuery(result.generated_sql); // Show the generated SQL
      setResults({
        columns: result.columns,
        rows: result.rows,
        row_count: result.row_count,
        execution_time_ms: result.execution_time_ms,
        truncated: result.truncated,
      });
      message.success(`Natural language query converted and executed (${result.execution_time_ms}ms)`);
    } catch (error: any) {
      message.error(error.message || 'Natural language query failed');
      setResults(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '24px' }}>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <div>
          <Title level={2}>
            <DatabaseOutlined style={{ marginRight: '8px' }} />
            Database Query Tool
          </Title>
        </div>

        {/* Database Selection */}
        <Card size="small">
          <Space>
            <span>Select Database:</span>
            <Select
              style={{ minWidth: 200 }}
              placeholder="Choose a database"
              value={selectedDatabase || undefined}
              onChange={setSelectedDatabase}
            >
              {databases.map(db => (
                <Option key={db.name} value={db.name}>
                  {db.name}
                  {db.description && ` - ${db.description}`}
                </Option>
              ))}
            </Select>
          </Space>
        </Card>

        <Row gutter={24}>
          {/* Left Column - Query Interface */}
          <Col span={12}>
            <Space direction="vertical" size="large" style={{ width: '100%' }}>
              {/* Natural Language Input */}
              {selectedDatabase && (
                <NaturalLanguageInput
                  onSubmit={handleNaturalLanguageQuery}
                  loading={loading}
                />
              )}

              {/* SQL Query Editor */}
              <QueryEditor
                value={query}
                onChange={setQuery}
                onExecute={handleExecuteQuery}
                loading={loading}
              />

              {/* Query Results */}
              {results && (
                <QueryResults
                  columns={results.columns}
                  rows={results.rows}
                  rowCount={results.row_count}
                  executionTimeMs={results.execution_time_ms}
                  truncated={results.truncated}
                  loading={false}
                />
              )}
            </Space>
          </Col>

          {/* Right Column - Metadata Viewer */}
          <Col span={12}>
            {selectedDatabase ? (
              <MetadataViewer
                databaseName={selectedDatabase}
                tables={metadata?.tables || []}
                views={metadata?.views || []}
                loading={metadataLoading}
              />
            ) : (
              <Card>
                <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
                  Select a database to view its metadata
                </div>
              </Card>
            )}
          </Col>
        </Row>
      </Space>
    </div>
  );
};
