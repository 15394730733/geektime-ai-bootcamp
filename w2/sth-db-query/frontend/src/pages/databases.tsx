import React, { useState } from 'react';
import { List, CreateButton, useTable } from "@refinedev/antd";
import { Table, Space, Button, Modal } from "antd";
import { DatabaseList, DatabaseForm } from '../components';

interface DatabaseConnection {
  id: string;
  name: string;
  url: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export const DatabaseListPage = () => {
  const [formVisible, setFormVisible] = useState(false);
  const [editingRecord, setEditingRecord] = useState<DatabaseConnection | undefined>();
  const [formMode, setFormMode] = useState<'create' | 'edit'>('create');

  const { tableProps, create, update, delete: deleteMutation } = useTable({
    resource: "dbs",
  });

  console.log("DatabaseListPage tableProps:", tableProps);

  const handleCreate = () => {
    setFormMode('create');
    setEditingRecord(undefined);
    setFormVisible(true);
  };

  const handleEdit = (record: DatabaseConnection) => {
    setFormMode('edit');
    setEditingRecord(record);
    setFormVisible(true);
  };

  const handleFormSuccess = () => {
    setFormVisible(false);
    // Refresh the table data after successful form submission
    tableProps.refetch?.();
    // Also refresh the query page databases if it's loaded
    if ((window as any).refreshQueryPageDatabases) {
      (window as any).refreshQueryPageDatabases();
    }
  };

  const handleFormCancel = () => {
    setFormVisible(false);
  };

  return (
    <List
      headerButtons={<CreateButton onClick={handleCreate} />}
    >
      <DatabaseList
        data={tableProps.dataSource}
        loading={tableProps.loading}
        onEdit={handleEdit}
        onDelete={(id) => {
          Modal.confirm({
            title: 'Confirm Deletion',
            content: 'Are you sure you want to delete this database connection?',
            onOk: () => {
              deleteMutation.mutate({ id });
            },
          });
        }}
        onRefresh={() => tableProps.refetch?.()}
      />

      <DatabaseForm
        visible={formVisible}
        onCancel={handleFormCancel}
        onSuccess={handleFormSuccess}
        initialValues={editingRecord}
        mode={formMode}
      />
    </List>
  );
};
