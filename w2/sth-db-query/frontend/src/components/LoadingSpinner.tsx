/**
 * Loading Spinner Component
 *
 * Provides consistent loading states across the application
 */

import React from 'react';
import { Spin, Space } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';

interface LoadingSpinnerProps {
  size?: 'small' | 'default' | 'large';
  tip?: string;
  spinning?: boolean;
  children?: React.ReactNode;
}

const antIcon = <LoadingOutlined style={{ fontSize: 24 }} spin />;

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'default',
  tip = 'Loading...',
  spinning = true,
  children,
}) => {
  if (children) {
    return (
      <Spin spinning={spinning} tip={tip} indicator={antIcon}>
        {children}
      </Spin>
    );
  }

  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      padding: '40px' 
    }}>
      <Space direction="vertical" align="center">
        <Spin size={size} indicator={antIcon} />
        <span style={{ color: '#666', marginTop: '8px' }}>{tip}</span>
      </Space>
    </div>
  );
};

export default LoadingSpinner;