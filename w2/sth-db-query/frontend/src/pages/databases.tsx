import React, { useState } from 'react';
import { List, CreateButton } from "@refinedev/antd";
import { Modal, message } from "antd";
import { DatabaseList, DatabaseFormModal } from '../components';
import { useAppState } from '../contexts/AppStateContext';
import { apiClient } from '../services/api';

export const DatabaseListPage = () => {
  const { state, actions } = useAppState();
  const [formVisible, setFormVisible] = useState(false);
  const [editingRecord, setEditingRecord] = useState<any>(undefined);
  const [formMode, setFormMode] = useState<'create' | 'edit'>('create');

  const handleCreate = () => {
    setFormMode('create');
    setEditingRecord(undefined);
    setFormVisible(true);
  };

  const handleEdit = (record: any) => {
    setFormMode('edit');
    setEditingRecord(record);
    setFormVisible(true);
  };

  const handleFormSuccess = async () => {
    setFormVisible(false);
    message.success('Database connection saved successfully');
  };

  const handleFormCancel = () => {
    setFormVisible(false);
  };

  const handleDelete = async (id: string) => {
    try {
      // Find the database to delete
      const dbToDelete = state.databases.find(db => db.name === id);
      if (!dbToDelete) {
        message.error('Database not found');
        return;
      }

      // Call API to delete
      await apiClient.deleteDatabase(id);
      
      // Update local state
      actions.removeDatabase(id);
      message.success('Database connection deleted successfully');
    } catch (error: any) {
      message.error(error.message || 'Failed to delete database connection');
    }
  };

  return (
    <div className="page-container">
      <div className="content-wrapper">
        <List
          headerButtons={<CreateButton onClick={handleCreate} />}
        >
          <DatabaseList
            data={state.databases}
            loading={state.loading.databases}
            onEdit={handleEdit}
            onDelete={(id) => {
              Modal.confirm({
                title: 'Confirm Deletion',
                content: 'Are you sure you want to delete this database connection?',
                onOk: () => handleDelete(id),
              });
            }}
            onRefresh={actions.loadDatabases}
          />

          <DatabaseFormModal
            visible={formVisible}
            onCancel={handleFormCancel}
            onSuccess={handleFormSuccess}
            initialValues={editingRecord}
            mode={formMode}
          />
        </List>
      </div>
    </div>
  );
};
