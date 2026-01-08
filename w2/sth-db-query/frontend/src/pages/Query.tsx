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
import { apiClient } from '../services/api';
import { useAppState } from '../contexts/AppStateContext';

const { Title } = Typography;
const { Option } = Select;

export const QueryPage: React.FC = () => {
  const { state, actions } = useAppState();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  // Filter active databases
  const activeDatabases = state.databases.filter(db => db.isActive);

  const handleExecuteQuery = async () => {
    if (!state.selectedDatabase || !query.trim()) {
      message.warning('Please select a database and enter a query');
      return;
    }

    setLoading(true);
    try {
      console.log('Executing query:', query, 'on database:', state.selectedDatabase);
      const result = await apiClient.executeQuery(state.selectedDatabase, { sql: query });
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
    if (!state.selectedDatabase) {
      message.warning('Please select a database first');
      return;
    }

    setLoading(true);
    try {
      const result = await apiClient.executeNaturalLanguageQuery(state.selectedDatabase, { prompt });
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
    <div className="page-container">
      <div className="content-wrapper">
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div>
            <Title level={2}>
              <DatabaseOutlined style={{ marginRight: '8px' }} />
              Database Query Tool
            </Title>
          </div>

          {/* Database Selection */}
          <div className="database-selector">
            <Space>
              <span style={{ fontWeight: 500 }}>Select Database:</span>
              <Select
                style={{ minWidth: 250 }}
                placeholder="Choose a database"
                value={state.selectedDatabase || undefined}
                onChange={actions.selectDatabase}
                loading={state.loading.databases}
              >
                {activeDatabases.map(db => (
                  <Option key={db.name} value={db.name}>
                    {db.name}
                    {db.description && ` - ${db.description}`}
                  </Option>
                ))}
              </Select>
            </Space>
          </div>

          <Row gutter={24} className="query-layout" style={{ minHeight: '70vh' }}>
            {/* Left Column - Query Interface */}
            <Col xs={24} lg={14} style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <Space direction="vertical" size="large" style={{ width: '100%', flex: 1 }}>
                {/* Natural Language Input */}
                {state.selectedDatabase && (
                  <div className="natural-language-input">
                    <NaturalLanguageInput
                      onSubmit={handleNaturalLanguageQuery}
                      loading={loading}
                    />
                  </div>
                )}

                {/* SQL Query Editor */}
                <div style={{ flex: 1, minHeight: '300px' }}>
                  <QueryEditor
                    value={query}
                    onChange={setQuery}
                    onExecute={handleExecuteQuery}
                    loading={loading}
                  />
                </div>

                {/* Query Results */}
                {results && (
                  <div className="query-results" style={{ flex: 1 }}>
                    <QueryResults
                      columns={results.columns}
                      rows={results.rows}
                      rowCount={results.row_count}
                      executionTimeMs={results.execution_time_ms}
                      truncated={results.truncated}
                      loading={false}
                    />
                  </div>
                )}
              </Space>
            </Col>

            {/* Right Column - Metadata Viewer */}
            <Col xs={24} lg={10} style={{ height: '100%' }}>
              {state.selectedDatabase ? (
                <div className="metadata-viewer">
                  <MetadataViewer
                    databaseName={state.selectedDatabase}
                    tables={state.metadata?.tables || []}
                    views={state.metadata?.views || []}
                    loading={state.loading.metadata}
                  />
                </div>
              ) : (
                <Card style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
                    <DatabaseOutlined style={{ fontSize: '48px', marginBottom: '16px', color: '#d9d9d9' }} />
                    <div>Select a database to view its metadata</div>
                  </div>
                </Card>
              )}
            </Col>
          </Row>
        </Space>
      </div>
    </div>
  );
};
