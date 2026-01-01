/**
 * Database Connection Form Component
 *
 * Form for creating and editing database connections
 */

import React, { useEffect } from 'react';
import { Form, Input, Button, Modal, message } from 'antd';
import { useCreate, useUpdate } from '@refinedev/core';

interface DatabaseConnection {
  id?: string;
  name: string;
  url: string;
  description?: string;
}

interface DatabaseFormProps {
  visible: boolean;
  onCancel: () => void;
  onSuccess: () => void;
  initialValues?: Partial<DatabaseConnection>;
  mode: 'create' | 'edit';
}

export const DatabaseForm: React.FC<DatabaseFormProps> = ({
  visible,
  onCancel,
  onSuccess,
  initialValues,
  mode
}) => {
  const [form] = Form.useForm();
  const { mutate: create, isLoading: isCreating } = useCreate();
  const { mutate: update, isLoading: isUpdating } = useUpdate();

  useEffect(() => {
    if (visible && initialValues) {
      form.setFieldsValue(initialValues);
    } else if (visible) {
      form.resetFields();
    }
  }, [visible, initialValues, form]);

  const handleSubmit = async (values: DatabaseConnection) => {
    try {
      if (mode === 'create') {
        await create({
          resource: 'dbs',
          values,
        });
        message.success('Database connection created successfully');
      } else {
        await update({
          resource: 'dbs',
          id: initialValues?.name || '',
          values,
        });
        message.success('Database connection updated successfully');
      }
      onSuccess();
      form.resetFields();
    } catch (error) {
      message.error(`Failed to ${mode} database connection`);
    }
  };

  const handleCancel = () => {
    form.resetFields();
    onCancel();
  };

  return (
    <Modal
      title={mode === 'create' ? 'Add Database Connection' : 'Edit Database Connection'}
      open={visible}
      onCancel={handleCancel}
      footer={null}
      width={600}
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        initialValues={initialValues}
      >
        <Form.Item
          name="name"
          label="Connection Name"
          rules={[
            { required: true, message: 'Please enter a connection name' },
            { pattern: /^[a-zA-Z0-9_-]+$/, message: 'Name can only contain letters, numbers, hyphens, and underscores' },
            { min: 1, max: 50, message: 'Name must be between 1 and 50 characters' }
          ]}
        >
          <Input placeholder="e.g., production_db, analytics_db" />
        </Form.Item>

        <Form.Item
          name="url"
          label="Database URL"
          rules={[
            { required: true, message: 'Please enter a database URL' },
            {
              pattern: /^postgresql:\/\/|^postgres:\/\//,
              message: 'URL must be a valid PostgreSQL connection string'
            }
          ]}
        >
          <Input placeholder="postgresql://user:password@host:port/database" />
        </Form.Item>

        <Form.Item
          name="description"
          label="Description (Optional)"
          rules={[
            { max: 200, message: 'Description cannot exceed 200 characters' }
          ]}
        >
          <Input.TextArea
            placeholder="Brief description of this database connection"
            rows={3}
          />
        </Form.Item>

        <Form.Item style={{ textAlign: 'right', marginBottom: 0 }}>
          <Button onClick={handleCancel} style={{ marginRight: 8 }}>
            Cancel
          </Button>
          <Button
            type="primary"
            htmlType="submit"
            loading={isCreating || isUpdating}
          >
            {mode === 'create' ? 'Create' : 'Update'}
          </Button>
        </Form.Item>
      </Form>
    </Modal>
  );
};
