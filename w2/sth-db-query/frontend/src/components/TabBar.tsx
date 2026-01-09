/**
 * TabBar Component
 * 
 * Displays query tabs with support for creating, switching, and closing tabs.
 * Shows the current database name and handles unsaved changes warnings.
 */

import React from 'react';
import { Tabs, Button, Typography, Modal } from 'antd';
import { PlusOutlined, DatabaseOutlined } from '@ant-design/icons';
import { TabBarProps } from '../types/query';
import { QueryTab } from '../types/layout';
import '../styles/TabBar.css';

const { Text } = Typography;

export const TabBar: React.FC<TabBarProps> = ({
  tabs,
  activeTabId,
  databaseName,
  onTabChange,
  onTabCreate,
  onTabClose,
}) => {
  const handleTabEdit = (
    targetKey: React.MouseEvent | React.KeyboardEvent | string,
    action: 'add' | 'remove'
  ) => {
    if (action === 'add') {
      onTabCreate();
    } else if (action === 'remove' && typeof targetKey === 'string') {
      handleTabClose(targetKey);
    }
  };

  const handleTabClose = (tabId: string) => {
    const tab = tabs.find(t => t.id === tabId);
    
    // If tab has unsaved changes, show confirmation dialog
    if (tab?.isDirty) {
      Modal.confirm({
        title: 'Unsaved Changes',
        content: `Tab "${tab.name}" has unsaved changes. Are you sure you want to close it?`,
        okText: 'Close',
        okType: 'danger',
        cancelText: 'Cancel',
        onOk: () => onTabClose(tabId),
      });
    } else {
      onTabClose(tabId);
    }
  };

  const renderTabLabel = (tab: QueryTab) => (
    <div className="flex items-center gap-1">
      <span className={tab.isDirty ? 'text-orange-500' : ''}>
        {tab.name}
        {tab.isDirty && <span className="ml-1">•</span>}
      </span>
    </div>
  );

  const tabItems = tabs.map(tab => ({
    key: tab.id,
    label: renderTabLabel(tab),
    closable: tabs.length > 1, // Don't allow closing the last tab
  }));

  return (
    <div className="border-b border-gray-200 bg-white">
      {/* Database name header */}
      <div className="px-4 py-2 bg-gray-50 border-b border-gray-100">
        <div className="flex items-center gap-2">
          <DatabaseOutlined className="text-blue-500" />
          <Text strong className="text-sm">
            {databaseName ? `Database: ${databaseName}` : 'No database selected'}
          </Text>
        </div>
      </div>

      {/* Tabs */}
      <Tabs
        type="editable-card"
        activeKey={activeTabId}
        onChange={onTabChange}
        onEdit={handleTabEdit}
        className="query-tabs"
        size="small"
        items={tabItems}
        addIcon={
          <Button
            type="text"
            size="small"
            icon={<PlusOutlined />}
            className="flex items-center justify-center"
          />
        }
      />
    </div>
  );
};

export default TabBar;