/**
 * DatabaseFormModal Component
 *
 * Modal wrapper for the DatabaseForm component
 */

import React, { useState } from 'react';
import { Modal, message } from 'antd';
import { DatabaseForm, DatabaseFormData } from './DatabaseForm';
import { apiClient, DatabaseConnection } from '../services/api';
import { useAppState } from '../contexts/AppStateContext';

export interface DatabaseFormModalProps {
  visible: boolean;
  onCancel: () => void;
  onSuccess: () => void;
  initialValues?: Partial<DatabaseConnection>;
  mode: 'create' | 'edit';
}

export const DatabaseFormModal: React.FC<DatabaseFormModalProps> = ({
  visible,
  onCancel,
  onSuccess,
  initialValues,
  mode,
}) => {
  const { actions } = useAppState();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (data: DatabaseFormData) => {
    setLoading(true);
    setError(null);

    try {
      if (mode === 'create') {
        const newDatabase = await apiClient.createDatabase({
          name: data.name,
          url: data.url,
          description: data.description || '',
          is_active: true,
        });
        actions.addDatabase(newDatabase);
      } else {
        // 编辑模式：传递用户输入的新名称
        const updatedDatabase = await apiClient.updateDatabase(initialValues?.name || '', {
          name: data.name, // 使用用户输入的新名称
          url: data.url,
          description: data.description || '',
        });
        actions.updateDatabase(updatedDatabase);
      }
      
      onSuccess();
    } catch (err: any) {
      setError(err.message || 'Failed to save database connection');
    } finally {
      setLoading(false);
    }
  };

  const handleTestConnection = async (data: DatabaseFormData) => {
    try {
      const result = await apiClient.testDatabaseConnection({
        name: data.name,
        url: data.url,
        description: data.description || '',
      });
      return result;
    } catch (error: any) {
      throw new Error(error.message || 'Connection test failed');
    }
  };

  const handleCancel = () => {
    setError(null);
    onCancel();
  };

  return (
    <Modal
      title={mode === 'create' ? 'Add Database Connection' : 'Edit Database Connection'}
      open={visible}
      onCancel={handleCancel}
      footer={null}
      width={700}
      destroyOnClose
    >
      <DatabaseForm
        loading={loading}
        error={error}
        onSubmit={handleSubmit}
        onTest={handleTestConnection}
        initialValues={initialValues}
        submitButtonText={mode === 'create' ? 'Add Database' : 'Update Database'}
        showTestConnection={true}
      />
    </Modal>
  );
};

export default DatabaseFormModal;