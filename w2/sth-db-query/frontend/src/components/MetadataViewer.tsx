/**
 * Database Metadata Viewer Component
 *
 * Displays database structure (tables, views, columns)
 */

import React from 'react';
import { Card, Tree, Typography, Tag, Space, Tooltip } from 'antd';
import { TableOutlined, EyeOutlined, KeyOutlined, DatabaseOutlined } from '@ant-design/icons';
import type { DataNode } from 'antd/es/tree';

const { Title, Text } = Typography;

interface ColumnInfo {
  name: string;
  data_type: string;
  is_nullable: boolean;
  is_primary_key: boolean;
  default_value?: string;
}

interface TableInfo {
  name: string;
  schema: string;
  columns: ColumnInfo[];
}

interface MetadataViewerProps {
  databaseName: string;
  tables: TableInfo[];
  views: TableInfo[];
  loading?: boolean;
}

const getColumnIcon = (column: ColumnInfo) => {
  if (column.is_primary_key) {
    return <KeyOutlined style={{ color: '#1890ff' }} />;
  }
  return null;
};

const getColumnTags = (column: ColumnInfo) => {
  const tags = [];

  if (column.is_primary_key) {
    tags.push(<Tag key="pk" color="blue" size="small">PK</Tag>);
  }

  if (!column.is_nullable) {
    tags.push(<Tag key="notnull" color="orange" size="small">NOT NULL</Tag>);
  }

  return tags;
};

const formatDataType = (dataType: string) => {
  // 简化数据类型显示
  const typeMap: { [key: string]: string } = {
    'character varying': 'varchar',
    'timestamp with time zone': 'timestamptz',
    'timestamp without time zone': 'timestamp',
    'USER-DEFINED': 'enum'
  };

  return typeMap[dataType] || dataType;
};

export const MetadataViewer: React.FC<MetadataViewerProps> = ({
  databaseName,
  tables,
  views,
  loading = false
}) => {
  // Build tree data for tables
  const buildTableTreeData = (tableList: TableInfo[], type: 'table' | 'view'): DataNode[] => {
    return tableList.map((table, tableIndex) => ({
      title: (
        <Space>
          {type === 'table' ? <TableOutlined /> : <EyeOutlined />}
          <span style={{ fontWeight: 500 }}>{table.name}</span>
          <Text type="secondary" style={{ fontSize: '12px' }}>
            {table.schema}
          </Text>
          <Tag size="small">{table.columns.length} columns</Tag>
        </Space>
      ),
      key: `${type}-${tableIndex}`,
      children: table.columns.map((column, columnIndex) => ({
        title: (
          <Space size="small">
            {getColumnIcon(column)}
            <Tooltip title={`${column.name}: ${formatDataType(column.data_type)}${column.is_nullable ? ' (nullable)' : ' (not null)'}${column.default_value ? ` default: ${column.default_value}` : ''}`}>
              <span>
                <Text strong>{column.name}</Text>
                <Text type="secondary" style={{ marginLeft: 8, fontSize: '12px' }}>
                  {formatDataType(column.data_type)}
                </Text>
              </span>
            </Tooltip>
            {getColumnTags(column)}
          </Space>
        ),
        key: `${type}-${tableIndex}-${columnIndex}`,
        isLeaf: true
      }))
    }));
  };

  const tableTreeData = buildTableTreeData(tables, 'table');
  const viewTreeData = buildTableTreeData(views, 'view');

  return (
    <Card
      title={
        <Space>
          <DatabaseOutlined />
          <span>Database: {databaseName}</span>
        </Space>
      }
      loading={loading}
      style={{ height: '100%', overflow: 'auto' }}
    >
      {tables.length > 0 && (
        <div style={{ marginBottom: 24 }}>
          <Title level={4} style={{ marginBottom: 16 }}>
            <TableOutlined style={{ marginRight: 8 }} />
            Tables ({tables.length})
          </Title>
          <Tree
            treeData={tableTreeData}
            defaultExpandAll={false}
            showLine
            style={{ background: 'transparent' }}
          />
        </div>
      )}

      {views.length > 0 && (
        <div>
          <Title level={4} style={{ marginBottom: 16 }}>
            <EyeOutlined style={{ marginRight: 8 }} />
            Views ({views.length})
          </Title>
          <Tree
            treeData={viewTreeData}
            defaultExpandAll={false}
            showLine
            style={{ background: 'transparent' }}
          />
        </div>
      )}

      {tables.length === 0 && views.length === 0 && !loading && (
        <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
          <DatabaseOutlined style={{ fontSize: '48px', marginBottom: '16px', display: 'block' }} />
          <Text type="secondary">No tables or views found in this database</Text>
        </div>
      )}
    </Card>
  );
};
