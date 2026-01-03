/**
 * Query Results Display Component
 *
 * Displays SQL query results in a table format
 */

import React from 'react';
import { Table, Card, Typography, Tag, Space, Button } from 'antd';
import { DownloadOutlined, CopyOutlined } from '@ant-design/icons';

const { Text } = Typography;

interface QueryResultsProps {
  columns: string[];
  rows: any[][];
  rowCount: number;
  executionTimeMs: number;
  truncated?: boolean;
  loading?: boolean;
}

export const QueryResults: React.FC<QueryResultsProps> = ({
  columns,
  rows,
  rowCount,
  executionTimeMs,
  truncated = false,
  loading = false
}) => {
  console.log('QueryResults props:', { columns, rows, rowCount, executionTimeMs, truncated, loading });

  const tableColumns = columns.map((col, index) => ({
    title: col,
    dataIndex: index,
    key: col,
    ellipsis: true,
  }));

  const tableData = rows.map((row, index) => {
    const rowData: any = { key: index };
    row.forEach((value, colIndex) => {
      rowData[colIndex] = value;
    });
    return rowData;
  });

  console.log('Table data:', tableData);

  const handleExport = () => {
    // TODO: Implement CSV/JSON export
    console.log('Export functionality to be implemented');
  };

  const handleCopy = () => {
    // TODO: Implement copy to clipboard
    console.log('Copy functionality to be implemented');
  };

  return (
    <Card
      title={
        <Space>
          Query Results
          {truncated && <Tag color="orange">Truncated</Tag>}
        </Space>
      }
      extra={
        <Space>
          <Text type="secondary">
            {rowCount} rows • {executionTimeMs}ms
          </Text>
          <Button
            icon={<CopyOutlined />}
            size="small"
            onClick={handleCopy}
          >
            Copy
          </Button>
          <Button
            icon={<DownloadOutlined />}
            size="small"
            onClick={handleExport}
          >
            Export
          </Button>
        </Space>
      }
    >
      <Table
        columns={tableColumns}
        dataSource={tableData}
        loading={loading}
        size="small"
        scroll={{ x: true }}
        pagination={{
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total, range) =>
            `${range[0]}-${range[1]} of ${total} rows`,
        }}
      />
    </Card>
  );
};
