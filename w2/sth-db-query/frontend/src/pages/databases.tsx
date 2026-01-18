import React, { useState } from 'react';
import { List, CreateButton } from "@refinedev/antd";
import { Modal, message } from "antd";
import { useNavigate } from 'react-router-dom';
import { DatabaseList, DatabaseFormModal } from '../components';
import { useAppState } from '../contexts/AppStateContext';
import { apiClient } from '../services/api';

export const DatabaseListPage = () => {
  const { state, actions } = useAppState();
  const navigate = useNavigate();
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
    // Refresh the database list to show the updated data
    await actions.loadDatabases();
  };

  const handleFormCancel = () => {
    setFormVisible(false);
  };

  const handleDelete = async (id: string) => {
    try {
      // Find the database to delete
      const dbToDelete = state.databases.find(db => db.id === id);
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

  const handleDatabaseClick = (databaseId: string) => {
    // Navigate to query page with database id as URL parameter
    navigate(`/query?db=${encodeURIComponent(databaseId)}`);
  };

  const handleRefreshAll = async () => {
    try {
      // First refresh the database list
      await actions.loadDatabases();
      
      // Then refresh metadata for all databases
      const refreshPromises = state.databases.map(db => 
        actions.refreshDatabaseMetadata(db.id)
      );
      await Promise.all(refreshPromises);
      
      message.success('All databases refreshed successfully');
    } catch (error: any) {
      message.error(error.message || 'Failed to refresh databases');
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
            onRefresh={handleRefreshAll}
            onDatabaseClick={handleDatabaseClick}
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
