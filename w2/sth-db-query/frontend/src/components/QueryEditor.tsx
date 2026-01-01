/**
 * SQL Query Editor Component
 *
 * Monaco-based SQL editor with syntax highlighting
 */

import React, { useRef, useEffect } from 'react';
import { Card, Button, Space } from 'antd';
import { PlayCircleOutlined, ClearOutlined } from '@ant-design/icons';
// TODO: Import Monaco Editor when available

interface QueryEditorProps {
  value: string;
  onChange: (value: string) => void;
  onExecute: () => void;
  loading?: boolean;
  height?: number;
}

export const QueryEditor: React.FC<QueryEditorProps> = ({
  value,
  onChange,
  onExecute,
  loading = false,
  height = 300
}) => {
  // TODO: Integrate Monaco Editor for SQL syntax highlighting
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = `${height}px`;
    }
  }, [height]);

  const handleClear = () => {
    onChange('');
  };

  return (
    <Card
      title="SQL Query"
      extra={
        <Space>
          <Button
            icon={<ClearOutlined />}
            onClick={handleClear}
            size="small"
          >
            Clear
          </Button>
          <Button
            type="primary"
            icon={<PlayCircleOutlined />}
            onClick={onExecute}
            loading={loading}
            size="small"
          >
            Execute
          </Button>
        </Space>
      }
    >
      <textarea
        ref={textareaRef}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Enter your SQL query here..."
        style={{
          width: '100%',
          minHeight: `${height}px`,
          fontFamily: 'monospace',
          fontSize: '14px',
          padding: '8px',
          border: '1px solid #d9d9d9',
          borderRadius: '4px',
          resize: 'vertical'
        }}
      />
    </Card>
  );
};
