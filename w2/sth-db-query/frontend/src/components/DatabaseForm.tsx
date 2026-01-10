/**
 * DatabaseForm Component
 *
 * Form for adding new database connections with validation
 */

import React, { useState } from 'react';
import { Form, Input, Button, Card, Typography, Space } from 'antd';
import { DatabaseOutlined, SaveOutlined, ReloadOutlined } from '@ant-design/icons';
import { CompactErrorDisplay } from './ErrorDisplay';

const { Title, Text } = Typography;
const { TextArea } = Input;

export interface DatabaseFormData {
  name: string;
  url: string;
  description?: string;
}

export interface DatabaseFormProps {
  loading?: boolean;
  error?: string | Error | null;
  onSubmit: (data: DatabaseFormData) => void;
  onTest?: (data: DatabaseFormData) => Promise<{ success: boolean; message: string; latency_ms?: number }>;
  initialValues?: Partial<DatabaseFormData>;
  submitButtonText?: string;
  showTestConnection?: boolean;
}

const validatePostgreSQLUrl = (url: string): boolean => {
  // Basic PostgreSQL URL validation
  const postgresUrlPattern = /^postgresql:\/\/[^:]+:[^@]+@[^:]+:\d+\/[^\/]+$/;
  return postgresUrlPattern.test(url);
};

export const DatabaseForm: React.FC<DatabaseFormProps> = ({
  loading = false,
  error = null,
  onSubmit,
  onTest,
  initialValues,
  submitButtonText = 'Add Database',
  showTestConnection = true,
}) => {
  const [form] = Form.useForm();
  const [testLoading, setTestLoading] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);

  const handleSubmit = async (values: DatabaseFormData) => {
    try {
      await onSubmit(values);
      // Reset form on successful submission
      if (!initialValues) {
        form.resetFields();
        setTestResult(null);
      }
    } catch (err) {
      // Error handling is done by parent component
    }
  };

  const handleTestConnection = async () => {
    try {
      const values = await form.validateFields();
      setTestLoading(true);
      setTestResult(null);
      
      if (onTest) {
        const result = await onTest(values);
        setTestResult({ 
          success: true, 
          message: result.message || 'Connection successful!' 
        });
      }
    } catch (err: any) {
      setTestResult({ 
        success: false, 
        message: err.message || 'Connection failed. Please check your credentials.' 
      });
    } finally {
      setTestLoading(false);
    }
  };

  const validateDatabaseName = (_: any, value: string) => {
    if (!value) {
      return Promise.reject(new Error('Database name is required'));
    }
    if (value.length < 2) {
      return Promise.reject(new Error('Database name must be at least 2 characters'));
    }
    if (!/^[a-zA-Z0-9_-]+$/.test(value)) {
      return Promise.reject(new Error('Database name can only contain letters, numbers, hyphens, and underscores'));
    }
    return Promise.resolve();
  };

  const validateDatabaseUrl = (_: any, value: string) => {
    if (!value) {
      return Promise.reject(new Error('Database URL is required'));
    }
    if (!validatePostgreSQLUrl(value)) {
      return Promise.reject(new Error('Please enter a valid PostgreSQL URL (postgresql://user:password@host:port/database)'));
    }
    return Promise.resolve();
  };

  return (
    <Card
      title={
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <DatabaseOutlined style={{ marginRight: 8, color: '#1890ff' }} />
          <Title level={4} style={{ margin: 0 }}>
            {initialValues ? 'Edit Database Connection' : 'Add New Database Connection'}
          </Title>
        </div>
      }
      style={{ width: '100%', maxWidth: 600 }}
    >
      {error && (
        <CompactErrorDisplay
          error={error}
          onDismiss={() => {
            // Parent component should handle error clearing
          }}
        />
      )}

      {testResult && (
        <CompactErrorDisplay
          error={testResult.success ? 
            { 
              category: 'internal' as any, 
              severity: 'low' as any, 
              code: 'CONNECTION_SUCCESS', 
              message: testResult.message, 
              userMessage: testResult.message,
              suggestions: []
            } : 
            testResult.message
          }
        />
      )}

      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        initialValues={initialValues}
        autoComplete="off"
      >
        <Form.Item
          label="Database Name"
          name="name"
          rules={[{ validator: validateDatabaseName }]}
          extra="A unique identifier for this database connection"
        >
          <Input
            placeholder="e.g., production-db, analytics-db"
            disabled={loading}
          />
        </Form.Item>

        <Form.Item
          label="Database URL"
          name="url"
          rules={[{ validator: validateDatabaseUrl }]}
          extra="PostgreSQL connection string (postgresql://user:password@host:port/database)"
        >
          <Input
            placeholder="postgresql://username:password@localhost:5432/database_name"
            disabled={loading}
          />
        </Form.Item>

        <Form.Item
          label="Description"
          name="description"
          extra="Optional description to help identify this database"
        >
          <TextArea
            rows={3}
            placeholder="e.g., Production database for customer data"
            disabled={loading}
            maxLength={500}
            showCount
          />
        </Form.Item>

        <Form.Item style={{ marginBottom: 0 }}>
          <Space>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              icon={<SaveOutlined />}
            >
              {submitButtonText}
            </Button>

            {showTestConnection && onTest && (
              <Button
                type="default"
                onClick={handleTestConnection}
                loading={testLoading}
                icon={<ReloadOutlined />}
              >
                Test Connection
              </Button>
            )}

            <Button
              type="default"
              onClick={() => {
                // 如果是编辑模式，清空所有字段；否则使用resetFields()
                if (initialValues) {
                  form.setFieldsValue({ name: '', url: '', description: '' });
                } else {
                  form.resetFields();
                }
                setTestResult(null);
              }}
              disabled={loading}
            >
              Reset
            </Button>
          </Space>
        </Form.Item>
      </Form>

      <div style={{ marginTop: 16, padding: '12px 16px', backgroundColor: '#f5f5f5', borderRadius: 6 }}>
        <Text type="secondary" style={{ fontSize: '12px' }}>
          <strong>Security Note:</strong> Database credentials are stored locally and used only for establishing connections. 
          Ensure you have proper permissions and follow your organization's security policies.
        </Text>
      </div>
    </Card>
  );
};

export default DatabaseForm;