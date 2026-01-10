/**
 * MetadataPanel Component
 *
 * Left panel containing search input and schema tree for database metadata
 */

import React, { useState } from 'react';
import { Card, Input, Typography } from 'antd';
import { SearchOutlined, DatabaseOutlined } from '@ant-design/icons';
import { DatabaseMetadata } from '../services/api';
import { SchemaTree } from './SchemaTree';
import '../styles/LayoutEnhancements.css';

const { Title } = Typography;

export interface MetadataPanelProps {
  databaseName: string | null;
  metadata: DatabaseMetadata | null;
  loading: boolean;
  onTableClick: (schema: string, tableName: string) => void;
  onColumnClick: (schema: string, tableName: string, columnName: string) => void;
}

export const MetadataPanel: React.FC<MetadataPanelProps> = ({
  databaseName,
  metadata,
  loading,
  onTableClick,
  onColumnClick,
}) => {
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };

  return (
    <div className="metadata-panel-container">
      <Card 
        title={
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <DatabaseOutlined style={{ marginRight: 8, color: '#1890ff' }} />
            <Title level={4} style={{ margin: 0 }}>
              {databaseName || 'Database Schema'}
            </Title>
          </div>
        }
        style={{ height: '100%', display: 'flex', flexDirection: 'column', border: 'none' }}
        styles={{ 
          body: { 
            padding: '16px', 
            flex: 1, 
            display: 'flex', 
            flexDirection: 'column'
          } 
        }}
      >
        {/* Search Input */}
        <div style={{ marginBottom: 16 }}>
          <Input
            placeholder="Search tables and columns..."
            prefix={<SearchOutlined />}
            value={searchQuery}
            onChange={handleSearchChange}
            allowClear
            className="metadata-search-input"
          />
        </div>

        {/* Schema Tree Container */}
        <div className="schema-tree-container custom-scrollbar-enhanced" style={{ flex: 1, overflowY: 'auto', overflowX: 'hidden' }}>
          <SchemaTree
            metadata={metadata}
            searchQuery={searchQuery}
            loading={loading}
            databaseName={databaseName}
            onTableSelect={onTableClick}
            onColumnSelect={onColumnClick}
          />
        </div>
      </Card>
    </div>
  );
};

export default MetadataPanel;