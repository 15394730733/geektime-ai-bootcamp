/**
 * Query Results Display Component
 *
 * Displays SQL query results in a table format with export functionality
 */

import React from 'react';
import { Table, Card, Typography, Tag, Space, Button, message } from 'antd';
import { DownloadOutlined, CopyOutlined } from '@ant-design/icons';

const { Text } = Typography;

interface QueryResultsProps {
  columns: string[];
  rows: any[][];
  rowCount: number;
  executionTimeMs: number;
  truncated?: boolean;
  loading?: boolean;
  query?: string;
}

export const QueryResults: React.FC<QueryResultsProps> = ({
  columns,
  rows,
  rowCount,
  executionTimeMs,
  truncated = false,
  loading = false,
  query = ''
}) => {
  console.log('QueryResults props:', { columns, rows, rowCount, executionTimeMs, truncated, loading });

  const tableColumns = columns.map((col, index) => ({
    title: col,
    dataIndex: index,
    key: col,
    ellipsis: true,
    sorter: (a: any, b: any) => {
      const aVal = a[index];
      const bVal = b[index];
      
      // Handle null/undefined values
      if (aVal == null && bVal == null) return 0;
      if (aVal == null) return -1;
      if (bVal == null) return 1;
      
      // Handle numeric values
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return aVal - bVal;
      }
      
      // Handle string values
      return String(aVal).localeCompare(String(bVal));
    },
  }));

  const tableData = rows.map((row, index) => {
    const rowData: any = { key: index };
    row.forEach((value, colIndex) => {
      rowData[colIndex] = value;
    });
    return rowData;
  });

  console.log('Table data:', tableData);

  const convertToCSV = (data: any[], columns: string[]): string => {
    const headers = columns.join(',');
    const csvRows = data.map(row => 
      columns.map((_, colIndex) => {
        const value = row[colIndex];
        // Handle null/undefined values
        if (value == null) return '';
        // Escape quotes and wrap in quotes if contains comma, quote, or newline
        const stringValue = String(value);
        if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n')) {
          return `"${stringValue.replace(/"/g, '""')}"`;
        }
        return stringValue;
      }).join(',')
    );
    return [headers, ...csvRows].join('\n');
  };

  const convertToJSON = (data: any[], columns: string[]): string => {
    const jsonData = data.map(row => {
      const obj: any = {};
      columns.forEach((col, colIndex) => {
        obj[col] = row[colIndex];
      });
      return obj;
    });
    return JSON.stringify(jsonData, null, 2);
  };

  const downloadFile = (content: string, filename: string, mimeType: string) => {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleExportCSV = () => {
    try {
      const csvContent = convertToCSV(tableData, columns);
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      downloadFile(csvContent, `query-results-${timestamp}.csv`, 'text/csv');
      message.success('CSV file downloaded successfully');
    } catch (error) {
      console.error('Error exporting CSV:', error);
      message.error('Failed to export CSV file');
    }
  };

  const handleExportJSON = () => {
    try {
      const jsonContent = convertToJSON(tableData, columns);
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      downloadFile(jsonContent, `query-results-${timestamp}.json`, 'application/json');
      message.success('JSON file downloaded successfully');
    } catch (error) {
      console.error('Error exporting JSON:', error);
      message.error('Failed to export JSON file');
    }
  };

  const handleCopy = async () => {
    try {
      // Copy as tab-separated values for better pasting into spreadsheets
      const tsvContent = [
        columns.join('\t'),
        ...tableData.map(row => 
          columns.map((_, colIndex) => {
            const value = row[colIndex];
            return value == null ? '' : String(value);
          }).join('\t')
        )
      ].join('\n');
      
      await navigator.clipboard.writeText(tsvContent);
      message.success('Results copied to clipboard');
    } catch (error) {
      console.error('Error copying to clipboard:', error);
      message.error('Failed to copy to clipboard');
    }
  };

  const formatExecutionTime = (timeMs: number): string => {
    if (timeMs < 1000) {
      return `${timeMs}ms`;
    } else if (timeMs < 60000) {
      return `${(timeMs / 1000).toFixed(2)}s`;
    } else {
      const minutes = Math.floor(timeMs / 60000);
      const seconds = ((timeMs % 60000) / 1000).toFixed(2);
      return `${minutes}m ${seconds}s`;
    }
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
            {rowCount.toLocaleString()} rows • {formatExecutionTime(executionTimeMs)}
          </Text>
          <Button
            icon={<CopyOutlined />}
            size="small"
            onClick={handleCopy}
            disabled={loading || rows.length === 0}
          >
            Copy
          </Button>
          <Space.Compact size="small">
            <Button
              icon={<DownloadOutlined />}
              onClick={handleExportCSV}
              disabled={loading || rows.length === 0}
            >
              CSV
            </Button>
            <Button
              icon={<DownloadOutlined />}
              onClick={handleExportJSON}
              disabled={loading || rows.length === 0}
            >
              JSON
            </Button>
          </Space.Compact>
        </Space>
      }
    >
      {rows.length === 0 && !loading ? (
        <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
          {query ? 'No results found for the query.' : 'Execute a query to see results here.'}
        </div>
      ) : (
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
            pageSizeOptions: ['10', '25', '50', '100', '200'],
            defaultPageSize: 25,
          }}
          rowClassName={(_record, index) => 
            index % 2 === 0 ? 'table-row-even' : 'table-row-odd'
          }
        />
      )}
      
      <style>{`
        .table-row-even {
          background-color: #fafafa;
        }
        .table-row-odd {
          background-color: #ffffff;
        }
      `}</style>
    </Card>
  );
};
