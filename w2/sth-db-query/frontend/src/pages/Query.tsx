/**
 * Query Execution Page
 *
 * Main page for SQL query execution with horizontal split layout
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Select, Space, Typography, message, Button } from 'antd';
import { DatabaseOutlined, ArrowLeftOutlined } from '@ant-design/icons';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';
import { useNavigate, useSearchParams } from 'react-router-dom';

import { MetadataPanel } from '../components/MetadataPanel';
import { QueryPanel } from '../components/QueryPanel';
import { NaturalLanguageInput } from '../components/NaturalLanguageInput';
import { MobileMetadataDrawer, MobileMetadataToggle } from '../components/MobileMetadataDrawer';
import { apiClient } from '../services/api';
import { useAppState } from '../contexts/AppStateContext';
import { QueryTab, QueryResult, LayoutPreferences } from '../types/layout';
import { loadLayoutPreferences, saveLayoutPreferences, calculateSafePanelSizes } from '../utils/layout';
import { createNewTab } from '../utils/tabManager';
import { useResponsive } from '../hooks/useResponsive';
import type { NaturalLanguageQueryResult } from '../services/api';
import '../styles/MobileMetadata.css';
import '../styles/ResizeHandles.css';
import '../styles/LayoutEnhancements.css';
import '../styles/PanelResize.css';



export const QueryPage: React.FC = () => {
  const { state, actions } = useAppState();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { screenWidth, layoutMode } = useResponsive();
  
  // Check if screen can accommodate both panels with minimum widths
  const canShowSplitLayout = layoutMode === 'desktop';
  
  // Layout state
  const [layoutPreferences, setLayoutPreferences] = useState<LayoutPreferences>(() => loadLayoutPreferences());
  
  // Mobile drawer state
  const [mobileDrawerVisible, setMobileDrawerVisible] = useState(false);
  
  // Query tabs state
  const [tabs, setTabs] = useState<QueryTab[]>(() => {
    const initialTab = createNewTab();
    return [initialTab];
  });
  const [activeTabId, setActiveTabId] = useState<string>('');

  // Initialize active tab ID when tabs change
  useEffect(() => {
    if (tabs.length > 0 && (!activeTabId || !tabs.find(tab => tab.id === activeTabId))) {
      setActiveTabId(tabs[0].id);
    }
  }, [tabs, activeTabId]);

  const [loading, setLoading] = useState(false);

  // Filter active databases
  const activeDatabases = state.databases.filter(db => db.isActive);

  // Auto-select database from URL parameter
  useEffect(() => {
    const dbParam = searchParams.get('db');
    if (dbParam && dbParam !== state.selectedDatabase) {
      // Check if the database exists in the list
      const dbExists = activeDatabases.some(db => db.name === dbParam);
      if (dbExists) {
        actions.selectDatabase(dbParam);
      }
    }
  }, [searchParams, activeDatabases, state.selectedDatabase, actions]);

  // Save layout preferences when they change
  useEffect(() => {
    saveLayoutPreferences(layoutPreferences);
  }, [layoutPreferences]);

  // Handle horizontal panel resize
  const handleHorizontalResize = useCallback((sizes: number[]) => {
    const leftPanelSize = sizes[0];
    
    // Validate constraints and adjust if necessary
    const safeSizes = calculateSafePanelSizes(leftPanelSize);
    
    setLayoutPreferences(prev => ({
      ...prev,
      horizontalSplitSize: safeSizes.leftPercentage,
    }));
  }, []);

  // Handle vertical panel resize
  const handleVerticalResize = useCallback((size: number) => {
    setLayoutPreferences(prev => ({
      ...prev,
      verticalSplitSize: size,
    }));
  }, []);

  // Tab management functions
  const handleTabCreate = useCallback(() => {
    const newTab = createNewTab();
    setTabs(prev => [...prev, newTab]);
    setActiveTabId(newTab.id);
  }, []);

  const handleTabChange = useCallback((tabId: string) => {
    setActiveTabId(tabId);
  }, []);

  const handleTabClose = useCallback((tabId: string) => {
    setTabs(prev => {
      const newTabs = prev.filter(tab => tab.id !== tabId);
      
      // If we're closing the active tab, switch to another tab
      if (tabId === activeTabId && newTabs.length > 0) {
        const currentIndex = prev.findIndex(tab => tab.id === tabId);
        const nextTab = newTabs[Math.min(currentIndex, newTabs.length - 1)];
        setActiveTabId(nextTab.id);
      }
      
      // Always keep at least one tab
      return newTabs.length === 0 ? [createNewTab()] : newTabs;
    });
  }, [activeTabId]);

  const handleQueryChange = useCallback((tabId: string, query: string) => {
    setTabs(prev => prev.map(tab => 
      tab.id === tabId 
        ? { ...tab, query, isDirty: query !== '' }
        : tab
    ));
  }, []);

  const handleExecuteQuery = useCallback(async (tabId: string) => {
    if (!state.selectedDatabase) {
      message.warning('Please select a database first');
      return;
    }

    const tab = tabs.find(t => t.id === tabId);
    if (!tab || !tab.query.trim()) {
      message.warning('Please enter a query');
      return;
    }

    setLoading(true);
    try {
      console.log('Executing query:', tab.query, 'on database:', state.selectedDatabase);
      const result = await apiClient.executeQuery(state.selectedDatabase, { sql: tab.query });
      console.log('Query result:', result);
      
      const queryResult: QueryResult = {
        columns: result.columns,
        rows: result.rows,
        rowCount: result.row_count,
        executionTimeMs: result.execution_time_ms,
        truncated: result.truncated,
      };

      setTabs(prev => prev.map(t => 
        t.id === tabId 
          ? { ...t, results: queryResult, isDirty: false }
          : t
      ));
      
      message.success(`Query executed successfully (${result.execution_time_ms}ms)`);
    } catch (error: any) {
      console.error('Query execution error:', error);
      message.error(error.message || 'Query execution failed');
      
      // Clear results on error
      setTabs(prev => prev.map(t => 
        t.id === tabId 
          ? { ...t, results: null }
          : t
      ));
    } finally {
      setLoading(false);
    }
  }, [state.selectedDatabase, tabs]);

  const handleNaturalLanguageQuery = async (prompt: string): Promise<NaturalLanguageQueryResult> => {
    if (!state.selectedDatabase) {
      message.warning('Please select a database first');
      throw new Error('No database selected');
    }

    setLoading(true);
    try {
      const result = await apiClient.executeNaturalLanguageQuery(state.selectedDatabase, { prompt });
      
      // Update the active tab with generated SQL and results
      const queryResult: QueryResult = {
        columns: result.columns,
        rows: result.rows,
        rowCount: result.row_count,
        executionTimeMs: result.execution_time_ms,
        truncated: result.truncated,
      };

      setTabs(prev => prev.map(tab => 
        tab.id === activeTabId 
          ? { ...tab, query: result.generated_sql, results: queryResult, isDirty: false }
          : tab
      ));
      
      message.success(`Natural language query converted and executed (${result.execution_time_ms}ms)`);
      
      return result;
    } catch (error: any) {
      message.error(error.message || 'Natural language query failed');
      // Re-throw to maintain the expected return type
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Handle table/column clicks for insertion
  const handleTableClick = useCallback((schema: string, tableName: string) => {
    const fullTableName = schema ? `${schema}.${tableName}` : tableName;
    const activeTab = tabs.find(tab => tab.id === activeTabId);
    if (activeTab) {
      const newQuery = activeTab.query + (activeTab.query ? ' ' : '') + fullTableName;
      handleQueryChange(activeTabId, newQuery);
    }
  }, [activeTabId, tabs, handleQueryChange]);

  const handleColumnClick = useCallback((_schema: string, _tableName: string, columnName: string) => {
    const activeTab = tabs.find(tab => tab.id === activeTabId);
    if (activeTab) {
      const newQuery = activeTab.query + (activeTab.query ? ' ' : '') + columnName;
      handleQueryChange(activeTabId, newQuery);
    }
  }, [activeTabId, tabs, handleQueryChange]);

  // Mobile drawer handlers
  const handleMobileDrawerToggle = useCallback(() => {
    setMobileDrawerVisible(prev => !prev);
  }, []);

  const handleMobileDrawerClose = useCallback(() => {
    setMobileDrawerVisible(false);
  }, []);

  // Handle SQL execution from natural language input
  const handleExecuteSQL = useCallback(async (sql: string) => {
    if (!state.selectedDatabase) {
      message.warning('Please select a database first');
      throw new Error('No database selected');
    }

    // Update the active tab with the SQL
    setTabs(prev => prev.map(tab => 
      tab.id === activeTabId 
        ? { ...tab, query: sql, isDirty: true }
        : tab
    ));

    // Execute the query
    return handleExecuteQuery(activeTabId);
  }, [state.selectedDatabase, activeTabId, handleExecuteQuery]);

  return (
    <div className="page-container">
      <div className="content-wrapper">
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          {/* Header with Back Button */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <Button
                icon={<ArrowLeftOutlined />}
                onClick={() => navigate('/databases')}
                type="text"
                size="large"
              >
                Back to Databases
              </Button>
              <Typography.Title level={2} style={{ margin: 0 }}>
                <DatabaseOutlined style={{ marginRight: '8px' }} />
                Query Tool
              </Typography.Title>
            </div>
          </div>

          {/* Database Selection */}
          <div className="database-selector-enhanced">
            <Space>
              <span style={{ fontWeight: 500 }}>Current Database:</span>
              <Select
                style={{ minWidth: 250 }}
                placeholder="Choose a database"
                value={state.selectedDatabase || undefined}
                onChange={actions.selectDatabase}
                loading={state.loading.databases}
              >
                {activeDatabases.map(db => (
                  <Select.Option key={db.name} value={db.name}>
                    {db.name}
                    {db.description && ` - ${db.description}`}
                  </Select.Option>
                ))}
              </Select>
            </Space>
          </div>

          {/* Natural Language Input */}
          {state.selectedDatabase && (
            <div className="natural-language-enhanced">
              <NaturalLanguageInput
                onSubmit={handleNaturalLanguageQuery}
                onExecuteSQL={handleExecuteSQL}
                loading={loading}
              />
            </div>
          )}

          {/* Layout constraint warning */}
          {layoutMode === 'constrained' && (
            <div style={{
              padding: '8px 12px',
              backgroundColor: '#fff7e6',
              border: '1px solid #ffd591',
              borderRadius: '4px',
              fontSize: '12px',
              color: '#d46b08',
              marginBottom: '8px'
            }}>
              Screen too narrow for split layout. Using mobile view for better experience.
            </div>
          )}

          {/* Main Layout: Responsive Split */}
          <div style={{ height: '70vh', width: '100%' }}>
            {!canShowSplitLayout ? (
              // Mobile Layout: Full-width query panel with drawer
              <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                {/* Mobile Header with Schema Toggle */}
                <div style={{ 
                  padding: '8px 16px', 
                  borderBottom: '1px solid #f0f0f0',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}>
                  <MobileMetadataToggle onClick={handleMobileDrawerToggle} />
                  {state.selectedDatabase && (
                    <span style={{ fontSize: '12px', color: '#666' }}>
                      {state.selectedDatabase}
                    </span>
                  )}
                </div>
                
                {/* Full-width Query Panel */}
                <div style={{ flex: 1, minHeight: 0 }}>
                  <QueryPanel
                    tabs={tabs}
                    activeTabId={activeTabId}
                    databaseName={state.selectedDatabase}
                    verticalSplitSize={layoutPreferences.verticalSplitSize}
                    loading={loading}
                    onTabChange={handleTabChange}
                    onTabCreate={handleTabCreate}
                    onTabClose={handleTabClose}
                    onQueryChange={handleQueryChange}
                    onExecute={handleExecuteQuery}
                    onVerticalSplitChange={handleVerticalResize}
                  />
                </div>

                {/* Mobile Metadata Drawer */}
                <MobileMetadataDrawer
                  visible={mobileDrawerVisible}
                  onClose={handleMobileDrawerClose}
                  databaseName={state.selectedDatabase}
                  metadata={state.metadata}
                  loading={state.loading.metadata}
                  onTableClick={handleTableClick}
                  onColumnClick={handleColumnClick}
                />
              </div>
            ) : (
              // Desktop Layout: Horizontal Split
              <PanelGroup
                direction="horizontal"
                onLayout={handleHorizontalResize}
              >
                {/* Left Panel - Metadata */}
                <Panel
                  defaultSize={layoutPreferences.horizontalSplitSize}
                  minSize={Math.max(15, (200 / screenWidth) * 100)} // Ensure 200px minimum
                  maxSize={Math.min(50, ((screenWidth - 400) / screenWidth) * 100)} // Ensure 400px minimum for right panel
                  style={{ minWidth: '200px' }}
                >
                  <MetadataPanel
                    databaseName={state.selectedDatabase}
                    metadata={state.metadata}
                    loading={state.loading.metadata}
                    onTableClick={handleTableClick}
                    onColumnClick={handleColumnClick}
                  />
                </Panel>

                {/* Resize Handle */}
                <PanelResizeHandle className="resize-handle resize-handle-horizontal" />

                {/* Right Panel - Query */}
                <Panel
                  defaultSize={100 - layoutPreferences.horizontalSplitSize}
                  minSize={Math.max(50, (400 / screenWidth) * 100)} // Ensure 400px minimum
                  maxSize={Math.min(85, ((screenWidth - 200) / screenWidth) * 100)} // Ensure 200px minimum for left panel
                  style={{ minWidth: '400px' }}
                >
                  <QueryPanel
                    tabs={tabs}
                    activeTabId={activeTabId}
                    databaseName={state.selectedDatabase}
                    verticalSplitSize={layoutPreferences.verticalSplitSize}
                    loading={loading}
                    onTabChange={handleTabChange}
                    onTabCreate={handleTabCreate}
                    onTabClose={handleTabClose}
                    onQueryChange={handleQueryChange}
                    onExecute={handleExecuteQuery}
                    onVerticalSplitChange={handleVerticalResize}
                  />
                </Panel>
              </PanelGroup>
            )}
          </div>
        </Space>
      </div>
    </div>
  );
};
