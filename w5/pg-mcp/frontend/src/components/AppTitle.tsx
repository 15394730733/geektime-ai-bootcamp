/**
 * Custom App Title Component
 *
 * Provides branded title for the database query tool
 */

import React from 'react';
import { Typography, Space } from 'antd';
import { DatabaseOutlined } from '@ant-design/icons';

const { Title } = Typography;

export const AppTitle: React.FC = () => {
  return (
    <Space align="center" style={{ padding: '16px' }}>
      <DatabaseOutlined 
        style={{ 
          fontSize: '24px', 
          color: '#1890ff',
          marginRight: '8px'
        }} 
      />
      <Title 
        level={4} 
        style={{ 
          margin: 0, 
          color: '#1890ff',
          fontWeight: 600
        }}
      >
        DB Query Tool
      </Title>
    </Space>
  );
};

export default AppTitle;