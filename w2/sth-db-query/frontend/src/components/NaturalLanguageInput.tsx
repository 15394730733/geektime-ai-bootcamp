/**
 * Natural Language Query Input Component
 *
 * Input component for natural language queries that get converted to SQL
 */

import React, { useState } from 'react';
import { Card, Input, Button, Space, Typography } from 'antd';
import { SendOutlined, LoadingOutlined } from '@ant-design/icons';

const { TextArea } = Input;
const { Text } = Typography;

interface NaturalLanguageInputProps {
  onSubmit: (query: string) => Promise<void>;
  loading?: boolean;
  placeholder?: string;
}

export const NaturalLanguageInput: React.FC<NaturalLanguageInputProps> = ({
  onSubmit,
  loading = false,
  placeholder = "Describe what data you want to see..."
}) => {
  const [query, setQuery] = useState('');

  const handleSubmit = async () => {
    if (!query.trim()) return;

    try {
      await onSubmit(query.trim());
      // Optionally clear input after successful submission
      // setQuery('');
    } catch (error) {
      // Error handling is done in parent component
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
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
      </Space>
    </Card>
  );
};
