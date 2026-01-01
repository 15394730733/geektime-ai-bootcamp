/**
 * Database Connection List Component
 *
 * Displays a list of database connections with management options
 */

import React from 'react';
import { List, Button, Space, Tag, Modal, message } from 'antd';
import { EditOutlined, DeleteOutlined, DatabaseOutlined } from '@ant-design/icons';
import { useList, useDelete } from '@refinedev/core';

interface DatabaseConnection {
  id: string;
  name: string;
  url: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface DatabaseListProps {
  onEdit?: (record: DatabaseConnection) => void;
  onDelete?: (id: string) => void;
}

export const DatabaseList: React.FC<DatabaseListProps> = ({
  onEdit,
  onDelete
}) => {
  const { data, isLoading, refetch } = useList<DatabaseConnection>({
    resource: 'dbs',
  });

  const { mutate: deleteMutation } = useDelete();

  const handleDelete = (id: string) => {
    if (onDelete) {
      onDelete(id);
    } else {
      // Fallback delete logic
      Modal.confirm({
        title: 'Confirm Deletion',
        content: 'Are you sure you want to delete this database connection?',
        onOk: () => {
          deleteMutation(
            { resource: 'dbs', id },
            {
              onSuccess: () => {
                message.success('Database connection deleted successfully');
                refetch();
              },
              onError: () => {
                message.error('Failed to delete database connection');
              }
            }
          );
        },
      });
    }
  };

  return (
    <List
      loading={isLoading}
      dataSource={data?.data || []}
      renderItem={(item) => (
        <List.Item
          actions={[
            <Button
              key="edit"
              type="link"
              icon={<EditOutlined />}
              onClick={() => onEdit?.(item)}
            >
              Edit
            </Button>,
            <Popconfirm
              key="delete"
              title="Are you sure you want to delete this database connection?"
              onConfirm={() => handleDelete(item.id)}
              okText="Yes"
              cancelText="No"
            >
              <Button
                type="link"
                danger
                icon={<DeleteOutlined />}
              >
                Delete
              </Button>
            </Popconfirm>
          ]}
        >
          <List.Item.Meta
            avatar={<DatabaseOutlined style={{ color: '#1890ff' }} />}
            title={
              <Space>
                {item.name}
                {item.is_active ? (
                  <Tag color="green">Active</Tag>
                ) : (
                  <Tag color="red">Inactive</Tag>
                )}
              </Space>
            }
            description={
              <div>
                <div>{item.description || 'No description'}</div>
                <div style={{ color: '#666', fontSize: '12px' }}>
                  Created: {new Date(item.created_at).toLocaleDateString()}
                </div>
              </div>
            }
          />
        </List.Item>
      )}
    />
  );
};
