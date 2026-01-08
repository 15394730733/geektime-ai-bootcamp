import React from 'react';
import { Card, Typography, Tag } from 'antd';
import { useAppState } from '../contexts/AppStateContext';

const { Title, Text } = Typography;

export const DebugInfo: React.FC = () => {
  const { state } = useAppState();

  return (
    <Card title="Debug Information" style={{ margin: '16px 0' }}>
      <div style={{ marginBottom: '16px' }}>
        <Title level={5}>Loading States:</Title>
        <Tag color={state.loading.databases ? 'orange' : 'green'}>
          Databases: {state.loading.databases ? 'Loading' : 'Loaded'}
        </Tag>
        <Tag color={state.loading.metadata ? 'orange' : 'green'}>
          Metadata: {state.loading.metadata ? 'Loading' : 'Loaded'}
        </Tag>
      </div>

      <div style={{ marginBottom: '16px' }}>
        <Title level={5}>Databases ({state.databases.length}):</Title>
        {state.databases.length === 0 ? (
          <Text type="secondary">No databases found</Text>
        ) : (
          state.databases.map(db => (
            <div key={db.id} style={{ marginBottom: '8px' }}>
              <Tag color={db.isActive ? 'green' : 'red'}>
                {db.name} - {db.isActive ? 'Active' : 'Inactive'}
              </Tag>
              <Text type="secondary"> {db.description}</Text>
            </div>
          ))
        )}
      </div>

      <div style={{ marginBottom: '16px' }}>
        <Title level={5}>Selected Database:</Title>
        <Text>{state.selectedDatabase || 'None selected'}</Text>
      </div>

      {state.error && (
        <div style={{ marginBottom: '16px' }}>
          <Title level={5}>Error:</Title>
          <Text type="danger">{state.error}</Text>
        </div>
      )}

      <div>
        <Title level={5}>Active Databases:</Title>
        {state.databases.filter(db => db.isActive).map(db => (
          <Tag key={db.id} color="blue">{db.name}</Tag>
        ))}
      </div>
    </Card>
  );
};