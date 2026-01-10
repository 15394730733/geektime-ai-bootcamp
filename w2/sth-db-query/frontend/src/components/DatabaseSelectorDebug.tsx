/**
 * Database Selector Debug Component
 * 
 * Temporary component to help diagnose database selector issues
 */

import React, { useEffect } from 'react';
import { Card, Typography, Space } from 'antd';
import { useAppState } from '../contexts/AppStateContext';

const { Text, Title } = Typography;

export const DatabaseSelectorDebug: React.FC = () => {
  const { state } = useAppState();

  useEffect(() => {
    console.log('=== DatabaseSelectorDebug: State Changed ===');
    console.log('selectedDatabase:', state.selectedDatabase);
    console.log('switchingDatabase:', state.switchingDatabase);
    console.log('databases count:', state.databases.length);
    console.log('metadata:', state.metadata ? 'loaded' : 'null');
    console.log('loading.metadata:', state.loading.metadata);
  }, [state.selectedDatabase, state.switchingDatabase, state.metadata, state.loading.metadata]);

  return (
    <Card 
      title="Debug Info" 
      size="small" 
      style={{ 
        position: 'fixed', 
        bottom: 20, 
        right: 20, 
        width: 300,
        zIndex: 9999,
        opacity: 0.9
      }}
    >
      <Space direction="vertical" size="small" style={{ width: '100%' }}>
        <div>
          <Text strong>Selected Database:</Text>
          <br />
          <Text code>{state.selectedDatabase || 'null'}</Text>
        </div>
        
        <div>
          <Text strong>Switching:</Text>
          <br />
          <Text code>{state.switchingDatabase ? 'true' : 'false'}</Text>
        </div>
        
        <div>
          <Text strong>Databases Count:</Text>
          <br />
          <Text code>{state.databases.length}</Text>
        </div>
        
        <div>
          <Text strong>Metadata:</Text>
          <br />
          <Text code>{state.metadata ? 'loaded' : 'null'}</Text>
        </div>
        
        <div>
          <Text strong>Loading Metadata:</Text>
          <br />
          <Text code>{state.loading.metadata ? 'true' : 'false'}</Text>
        </div>
        
        {state.databases.length > 0 && (
          <div>
            <Text strong>Available DBs:</Text>
            <br />
            {state.databases.filter(db => db.isActive).map(db => (
              <Text key={db.name} style={{ display: 'block', fontSize: '11px' }}>
                • {db.name}
              </Text>
            ))}
          </div>
        )}
      </Space>
    </Card>
  );
};
