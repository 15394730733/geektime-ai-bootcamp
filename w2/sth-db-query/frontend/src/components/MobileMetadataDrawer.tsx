/**
 * Mobile drawer component for metadata panel
 */

import React from 'react';
import { Drawer, Button } from 'antd';
import { MenuOutlined, CloseOutlined } from '@ant-design/icons';
import { MetadataPanel } from './MetadataPanel';
import type { DatabaseMetadata } from '../services/api';

interface MobileMetadataDrawerProps {
  visible: boolean;
  onClose: () => void;
  databaseName: string | null;
  metadata: DatabaseMetadata | null;
  loading: boolean;
  onTableClick: (schema: string, tableName: string) => void;
  onColumnClick: (schema: string, tableName: string, columnName: string) => void;
}

export const MobileMetadataDrawer: React.FC<MobileMetadataDrawerProps> = ({
  visible,
  onClose,
  databaseName,
  metadata,
  loading,
  onTableClick,
  onColumnClick,
}) => {
  return (
    <Drawer
      title="Database Schema"
      placement="left"
      onClose={onClose}
      open={visible}
      width={320}
      styles={{
        body: { padding: 0 },
      }}
      extra={
        <Button
          type="text"
          icon={<CloseOutlined />}
          onClick={onClose}
          size="small"
        />
      }
    >
      <div style={{ height: '100%' }}>
        <MetadataPanel
          databaseName={databaseName}
          metadata={metadata}
          loading={loading}
          onTableClick={(schema, tableName) => {
            onTableClick(schema, tableName);
            onClose(); // Close drawer after selection
          }}
          onColumnClick={(schema, tableName, columnName) => {
            onColumnClick(schema, tableName, columnName);
            onClose(); // Close drawer after selection
          }}
        />
      </div>
    </Drawer>
  );
};

/**
 * Toggle button for mobile metadata drawer
 */
interface MobileMetadataToggleProps {
  onClick: () => void;
  className?: string;
}

export const MobileMetadataToggle: React.FC<MobileMetadataToggleProps> = ({
  onClick,
  className = '',
}) => {
  return (
    <Button
      type="primary"
      icon={<MenuOutlined />}
      onClick={onClick}
      className={`mobile-metadata-toggle ${className}`}
      size="small"
    >
      Schema
    </Button>
  );
};