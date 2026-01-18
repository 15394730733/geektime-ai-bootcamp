/**
 * MetadataViewer Component
 *
 * Displays database schema in expandable tree structure
 */

import React, { useMemo } from 'react';
import { Tree, Card, Typography, Badge, Tooltip, Empty, Spin } from 'antd';
import { 
  DatabaseOutlined, 
  TableOutlined, 
  EyeOutlined, 
  KeyOutlined,
  FieldStringOutlined,
  FieldNumberOutlined,
  FieldBinaryOutlined,
  FieldTimeOutlined,
  QuestionCircleOutlined
} from '@ant-design/icons';
import { DatabaseMetadata, TableMetadata, ColumnMetadata } from '../services/api';

const { Title, Text } = Typography;

export interface MetadataViewerProps {
  metadata?: DatabaseMetadata | null;
  selectedDatabase?: string;
  loading?: boolean;
  onTableSelect?: (tableName: string, schema: string) => void;
  onColumnSelect?: (columnName: string, tableName: string, schema: string) => void;
}

interface TreeNodeData {
  key: string;
  title: React.ReactNode;
  icon?: React.ReactNode;
  children?: TreeNodeData[];
  isLeaf?: boolean;
  selectable?: boolean;
  type: 'database' | 'schema' | 'table' | 'view' | 'column';
  metadata?: {
    tableName?: string;
    schema?: string;
    columnName?: string;
    dataType?: string;
    isNullable?: boolean;
    isPrimaryKey?: boolean;
    defaultValue?: string;
  };
}

const getDataTypeIcon = (dataType: string) => {
  const type = dataType.toLowerCase();
  
  if (type.includes('varchar') || type.includes('text') || type.includes('char')) {
    return <FieldStringOutlined style={{ color: '#52c41a' }} />;
  }
  if (type.includes('int') || type.includes('numeric') || type.includes('decimal') || type.includes('float')) {
    return <FieldNumberOutlined style={{ color: '#1890ff' }} />;
  }
  if (type.includes('timestamp') || type.includes('date') || type.includes('time')) {
    return <FieldTimeOutlined style={{ color: '#fa8c16' }} />;
  }
  if (type.includes('boolean') || type.includes('bit')) {
    return <FieldBinaryOutlined style={{ color: '#722ed1' }} />;
  }
  
  return <QuestionCircleOutlined style={{ color: '#8c8c8c' }} />;
};

const formatColumnTitle = (column: ColumnMetadata) => {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      {getDataTypeIcon(column.data_type)}
      <span style={{ fontWeight: column.is_primary_key ? 'bold' : 'normal' }}>
        {column.name}
      </span>
      {column.is_primary_key && (
        <Tooltip title="Primary Key">
          <KeyOutlined style={{ color: '#faad14', fontSize: '12px' }} />
        </Tooltip>
      )}
      <Text type="secondary" style={{ fontSize: '11px' }}>
        {column.data_type}
      </Text>
      {!column.is_nullable && (
        <Badge 
          count="NOT NULL" 
          style={{ 
            backgroundColor: '#ff4d4f', 
            fontSize: '9px', 
            height: '16px', 
            lineHeight: '16px' 
          }} 
        />
      )}
      {column.default_value && (
        <Tooltip title={`Default: ${column.default_value}`}>
          <Text type="secondary" style={{ fontSize: '10px' }}>
            = {column.default_value.length > 10 ? `${column.default_value.substring(0, 10)}...` : column.default_value}
          </Text>
        </Tooltip>
      )}
    </div>
  );
};

const formatTableTitle = (table: TableMetadata, isView: boolean = false) => {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      {isView ? (
        <EyeOutlined style={{ color: '#722ed1' }} />
      ) : (
        <TableOutlined style={{ color: '#1890ff' }} />
      )}
      <span style={{ fontWeight: 500 }}>
        {table.name}
      </span>
      <Badge 
        count={table.columns.length} 
        style={{ 
          backgroundColor: '#f0f0f0', 
          color: '#666',
          fontSize: '10px',
          height: '16px',
          lineHeight: '16px'
        }} 
      />
      {table.schema !== 'public' && (
        <Text type="secondary" style={{ fontSize: '11px' }}>
          ({table.schema})
        </Text>
      )}
    </div>
  );
};

export const MetadataViewer: React.FC<MetadataViewerProps> = ({
  metadata,
  selectedDatabase,
  loading = false,
  onTableSelect,
  onColumnSelect,
}) => {
  const treeData = useMemo(() => {
    if (!metadata) return [];

    const nodes: TreeNodeData[] = [];

    // Group tables and views by schema
    const schemaGroups = new Map<string, { tables: TableMetadata[], views: TableMetadata[] }>();
    
    metadata.tables.forEach(table => {
      if (!schemaGroups.has(table.schema)) {
        schemaGroups.set(table.schema, { tables: [], views: [] });
      }
      schemaGroups.get(table.schema)!.tables.push(table);
    });

    metadata.views.forEach(view => {
      if (!schemaGroups.has(view.schema)) {
        schemaGroups.set(view.schema, { tables: [], views: [] });
      }
      schemaGroups.get(view.schema)!.views.push(view);
    });

    // Create tree nodes for each schema
    Array.from(schemaGroups.entries()).forEach(([schema, { tables, views }]) => {
      const schemaChildren: TreeNodeData[] = [];

      // Add tables
      tables.forEach(table => {
        const tableChildren: TreeNodeData[] = table.columns.map(column => ({
          key: `${schema}.${table.name}.${column.name}`,
          title: formatColumnTitle(column),
          isLeaf: true,
          type: 'column' as const,
          metadata: {
            tableName: table.name,
            schema: schema,
            columnName: column.name,
            dataType: column.data_type,
            isNullable: column.is_nullable,
            isPrimaryKey: column.is_primary_key,
            defaultValue: column.default_value,
          },
        }));

        schemaChildren.push({
          key: `${schema}.${table.name}`,
          title: formatTableTitle(table, false),
          children: tableChildren,
          type: 'table' as const,
          metadata: {
            tableName: table.name,
            schema: schema,
          },
        });
      });

      // Add views
      views.forEach(view => {
        const viewChildren: TreeNodeData[] = view.columns.map(column => ({
          key: `${schema}.${view.name}.${column.name}`,
          title: formatColumnTitle(column),
          isLeaf: true,
          type: 'column' as const,
          metadata: {
            tableName: view.name,
            schema: schema,
            columnName: column.name,
            dataType: column.data_type,
            isNullable: column.is_nullable,
            isPrimaryKey: column.is_primary_key,
            defaultValue: column.default_value,
          },
        }));

        schemaChildren.push({
          key: `${schema}.${view.name}`,
          title: formatTableTitle(view, true),
          children: viewChildren,
          type: 'view' as const,
          metadata: {
            tableName: view.name,
            schema: schema,
          },
        });
      });

      // Add schema node (or skip if only public schema with few items)
      if (schemaGroups.size === 1 && schema === 'public') {
        nodes.push(...schemaChildren);
      } else {
        nodes.push({
          key: schema,
          title: (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <DatabaseOutlined style={{ color: '#fa8c16' }} />
              <span style={{ fontWeight: 600 }}>{schema}</span>
              <Badge 
                count={tables.length + views.length} 
                style={{ 
                  backgroundColor: '#f0f0f0', 
                  color: '#666',
                  fontSize: '10px',
                  height: '16px',
                  lineHeight: '16px'
                }} 
              />
            </div>
          ),
          children: schemaChildren,
          type: 'schema' as const,
        });
      }
    });

    return nodes;
  }, [metadata]);

  const handleSelect = (selectedKeys: React.Key[], info: any) => {
    const node = info.node as TreeNodeData;
    
    if (node.type === 'table' || node.type === 'view') {
      onTableSelect?.(node.metadata!.tableName!, node.metadata!.schema!);
    } else if (node.type === 'column') {
      onColumnSelect?.(
        node.metadata!.columnName!, 
        node.metadata!.tableName!, 
        node.metadata!.schema!
      );
    }
  };

  if (loading) {
    return (
      <Card style={{ height: '100%' }}>
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '200px' }}>
          <Spin size="large" />
        </div>
      </Card>
    );
  }

  if (!selectedDatabase) {
    return (
      <Card style={{ height: '100%' }}>
        <Empty
          image={<DatabaseOutlined style={{ fontSize: '48px', color: '#d9d9d9' }} />}
          description={
            <div>
              <Title level={4} type="secondary">
                No Database Selected
              </Title>
              <Text type="secondary">
                Select a database connection to view its schema
              </Text>
            </div>
          }
        />
      </Card>
    );
  }

  if (!metadata || (metadata.tables.length === 0 && metadata.views.length === 0)) {
    return (
      <Card 
        title={
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <DatabaseOutlined style={{ marginRight: 8, color: '#1890ff' }} />
            <Title level={4} style={{ margin: 0 }}>
              {selectedDatabase} Schema
            </Title>
          </div>
        }
        style={{ height: '100%' }}
      >
        <Empty
          image={<TableOutlined style={{ fontSize: '48px', color: '#d9d9d9' }} />}
          description={
            <div>
              <Title level={4} type="secondary">
                No Tables Found
              </Title>
              <Text type="secondary">
                This database appears to be empty or you may not have permission to view its schema
              </Text>
            </div>
          }
        />
      </Card>
    );
  }

  return (
    <Card 
      title={
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <DatabaseOutlined style={{ marginRight: 8, color: '#1890ff' }} />
            <Title level={4} style={{ margin: 0 }}>
              {selectedDatabase} Schema
            </Title>
          </div>
          <div style={{ display: 'flex', gap: 16 }}>
            <Badge count={metadata.tables.length} showZero>
              <Text type="secondary">Tables</Text>
            </Badge>
            <Badge count={metadata.views.length} showZero>
              <Text type="secondary">Views</Text>
            </Badge>
          </div>
        </div>
      }
      style={{ 
        height: '100%',
        display: 'flex',
        flexDirection: 'column'
      }}
      styles={{ 
        body: { 
          padding: '16px', 
          flex: 1,
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column'
        } 
      }}
    >
      <div 
        style={{ 
          flex: 1,
          overflow: 'auto',
          minHeight: 0
        }}
        className="custom-scrollbar-enhanced"
      >
        <Tree
          treeData={treeData}
          defaultExpandAll={treeData.length <= 5} // Auto-expand if few items
          showIcon={false}
          onSelect={handleSelect}
          style={{ 
            fontSize: '13px'
          }}
        />
      </div>
    </Card>
  );
};

export default MetadataViewer;