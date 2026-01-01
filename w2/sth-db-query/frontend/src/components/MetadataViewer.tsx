/**
 * Database Metadata Viewer Component
 *
 * Displays database structure (tables, views, columns)
 */

import React from 'react';
import { Card, Tree, Typography } from 'antd';
import { TableOutlined, EyeOutlined } from '@ant-design/icons';

const { Title } = Typography;

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

export const MetadataViewer: React.FC<MetadataViewerProps> = ({
  databaseName,
  tables,
  views,
  loading = false
}) => {
  // TODO: Implement metadata tree structure
  return (
    <Card
      title={`Database: ${databaseName}`}
      loading={loading}
    >
      <Title level={4}>Tables ({tables.length})</Title>
      {/* TODO: Implement table tree */}

      <Title level={4} style={{ marginTop: 24 }}>
        Views ({views.length})
      </Title>
      {/* TODO: Implement view tree */}
    </Card>
  );
};
