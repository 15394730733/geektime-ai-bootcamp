/**
 * DatabaseList Component
 *
 * Displays all stored database connections with status and selection functionality
 */

import React from 'react';
import { List, Card, Badge, Typography, Button, Tooltip } from 'antd';
import { DatabaseOutlined, CheckCircleOutlined, ExclamationCircleOutlined, ClockCircleOutlined } from '@ant-design/icons';
import { DatabaseConnection } from '../services/api';

const { Text, Title } = Typography;

export interface DatabaseListProps {
  data?: DatabaseConnection[];
  loading?: boolean;
  onEdit?: (database: DatabaseConnection) => void;
  onDelete?: (id: string) => void;
  onRefresh?: () => void;
  onRefreshDatabase?: (databaseName: string) => void;
  onDatabaseClick?: (databaseName: string) => void;
}

const getStatusIcon = (isActive: boolean) => {
  if (isActive) {
    return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
  }
  return <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />;
};

const getStatusBadge = (isActive: boolean) => {
  return (
    <Badge
      status={isActive ? 'success' : 'error'}
      text={isActive ? 'Active' : 'Inactive'}
    />
  );
};

const formatLastConnected = (dateString: string) => {
  const date = new Date(dateString);
  const now = new Date();
  const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
  
  if (diffInHours < 1) {
    return 'Just now';
  } else if (diffInHours < 24) {
    return `${diffInHours} hour${diffInHours > 1 ? 's' : ''} ago`;
  } else {
    const diffInDays = Math.floor(diffInHours / 24);
    return `${diffInDays} day${diffInDays > 1 ? 's' : ''} ago`;
  }
};

export const DatabaseList: React.FC<DatabaseListProps> = ({
  data = [],
  loading = false,
  onEdit,
  onDelete,
  onRefresh,
  onRefreshDatabase,
  onDatabaseClick,
}) => {
  const databases = data || [];
  const renderDatabaseItem = (database: DatabaseConnection) => {
    return (
      <List.Item
        key={database.id}
        style={{
          padding: 0,
          border: 'none',
        }}
      >
        <Card
          hoverable
          size="small"
          style={{
            width: '100%',
            marginBottom: 8,
            border: '1px solid #d9d9d9',
            backgroundColor: 'white',
            cursor: 'pointer',
          }}
          styles={{ body: { padding: '12px 16px' } }}
          onClick={() => onDatabaseClick?.(database.name)}
        >
          <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ display: 'flex', alignItems: 'center', marginBottom: 4 }}>
                <DatabaseOutlined style={{ marginRight: 8, color: '#1890ff' }} />
                <Title level={5} style={{ margin: 0, fontSize: '14px' }} ellipsis>
                  {database.name}
                </Title>
              </div>
              
              {database.description && (
                <Text
                  type="secondary"
                  style={{ fontSize: '12px', display: 'block', marginBottom: 4 }}
                  ellipsis
                >
                  {database.description}
                </Text>
              )}
              
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center' }}>
                  {getStatusIcon(database.isActive)}
                  <span style={{ marginLeft: 4, fontSize: '12px' }}>
                    {getStatusBadge(database.isActive)}
                  </span>
                </div>
                
                {database.updatedAt && (
                  <Tooltip title={`Last connected: ${new Date(database.updatedAt).toLocaleString()}`}>
                    <div style={{ display: 'flex', alignItems: 'center', fontSize: '11px', color: '#8c8c8c' }}>
                      <ClockCircleOutlined style={{ marginRight: 4 }} />
                      {formatLastConnected(database.updatedAt)}
                    </div>
                  </Tooltip>
                )}
              </div>
            </div>
          </div>
          
          {/* Custom Actions Bar */}
          <div style={{
            display: 'flex',
            justifyContent: 'flex-end',
            alignItems: 'center',
            marginTop: '12px',
            paddingTop: '12px',
            borderTop: '1px solid #f0f0f0',
          }}>
            {/* Edit Button */}
            <div
              style={{
                marginRight: '8px',
                flex: 1,
                textAlign: 'right',
              }}
              onClick={(e) => {
                e.stopPropagation();
                onEdit?.(database);
              }}
            >
              <Button
                type="link"
                size="small"
                style={{ 
                  padding: '8px 16px', 
                  width: '100%',
                  textAlign: 'right'
                }}
              >
                Edit
              </Button>
            </div>
            
            {/* Update Button */}
            <div
              style={{
                marginRight: '8px',
                flex: 1,
                textAlign: 'right',
              }}
              onClick={(e) => {
                e.stopPropagation();
                onRefreshDatabase?.(database.name);
              }}
            >
              <Button
                type="link"
                size="small"
                style={{ 
                  padding: '8px 16px', 
                  width: '100%',
                  textAlign: 'right'
                }}
              >
                Update
              </Button>
            </div>
            
            {/* Delete Button */}
            <div
              style={{
                flex: 1,
                textAlign: 'right',
              }}
              onClick={(e) => {
                e.stopPropagation();
                onDelete?.(database.name);
              }}
            >
              <Button
                type="link"
                size="small"
                danger
                style={{ 
                  padding: '8px 16px', 
                  width: '100%',
                  textAlign: 'right'
                }}
              >
                Delete
              </Button>
            </div>
          </div>
        </Card>
      </List.Item>
    );
  };

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Title level={4} style={{ margin: 0 }}>
          Database Connections
        </Title>
        {onRefresh && (
          <Button
            type="text"
            size="small"
            onClick={onRefresh}
            loading={loading}
          >
            Refresh
          </Button>
        )}
      </div>

      {databases.length === 0 && !loading ? (
        <Card style={{ textAlign: 'center', padding: '40px 20px' }}>
          <DatabaseOutlined style={{ fontSize: '48px', color: '#d9d9d9', marginBottom: 16 }} />
          <Title level={4} type="secondary">
            No Database Connections
          </Title>
          <Text type="secondary">
            Add your first database connection to get started
          </Text>
        </Card>
      ) : (
        <div style={{ flex: 1, overflow: 'auto' }}>
          <List
            loading={loading}
            dataSource={databases}
            renderItem={renderDatabaseItem}
            style={{ height: '100%' }}
          />
        </div>
      )}
    </div>
  );
};

export default DatabaseList;