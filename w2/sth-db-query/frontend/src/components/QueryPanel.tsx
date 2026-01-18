/**
 * QueryPanel Component
 * 
 * Right-side panel containing TabBar, QueryEditor, and QueryResults
 * with vertical split layout using react-resizable-panels.
 * Manages multiple query tabs with independent state for each tab.
 */

import React, { useEffect, useState } from 'react';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';
import { TabBar } from './TabBar';
import { QueryEditor } from './QueryEditor';
import { QueryResults } from './QueryResults';
import { QueryTab, QueryResult } from '../types/layout';
import { validateTabState } from '../utils/tabManager';
import '../styles/ResizeHandles.css';
import '../styles/PanelResize.css';

interface QueryPanelProps {
  tabs: QueryTab[];
  activeTabId: string;
  databaseName: string | null;
  verticalSplitSize: number;
  loading?: boolean;
  onTabChange: (tabId: string) => void;
  onTabCreate: () => void;
  onTabClose: (tabId: string) => void;
  onQueryChange: (tabId: string, query: string) => void;
  onExecute: (tabId: string) => void;
  onVerticalSplitChange: (size: number) => void;
  onNaturalLanguageQuery?: (prompt: string) => Promise<void>;
}

export const QueryPanel: React.FC<QueryPanelProps> = ({
  tabs,
  activeTabId,
  databaseName,
  verticalSplitSize,
  loading = false,
  onTabChange,
  onTabCreate,
  onTabClose,
  onQueryChange,
  onExecute,
  onVerticalSplitChange,
  onNaturalLanguageQuery,
}) => {
  // Auto-export state (default: both checked)
  const [autoExportCSV, setAutoExportCSV] = useState(true);
  const [autoExportJSON, setAutoExportJSON] = useState(true);

  const handleAutoExportChange = (csv: boolean, json: boolean) => {
    setAutoExportCSV(csv);
    setAutoExportJSON(json);
  };

  // Debug: Log when databaseName prop changes
  React.useEffect(() => {
    console.log('QueryPanel: databaseName prop changed to:', databaseName);
  }, [databaseName]);
  
  // Validate tab state on mount and when tabs change
  useEffect(() => {
    const validation = validateTabState(tabs, activeTabId);
    if (!validation.isValid) {
      console.warn('Tab state validation failed:', validation.issues);
    }
  }, [tabs, activeTabId]);

  // Get the active tab
  const activeTab = tabs.find(tab => tab.id === activeTabId);
  
  if (!activeTab) {
    return (
      <div className="flex items-center justify-center h-full text-gray-500">
        <div className="text-center">
          <p>No active tab found</p>
          <p className="text-sm mt-2">Active tab ID: {activeTabId}</p>
          <p className="text-sm">Available tabs: {tabs.map(t => t.id).join(', ')}</p>
        </div>
      </div>
    );
  }

  const handleQueryChange = (query: string) => {
    onQueryChange(activeTabId, query);
  };

  const handleExecute = () => {
    onExecute(activeTabId);
  };

  const handleVerticalResize = (sizes: number[]) => {
    // sizes[0] is the top panel (editor), sizes[1] is the bottom panel (results)
    onVerticalSplitChange(sizes[0]);
  };

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Tab Bar */}
      <TabBar
        tabs={tabs}
        activeTabId={activeTabId}
        databaseName={databaseName}
        onTabChange={onTabChange}
        onTabCreate={onTabCreate}
        onTabClose={onTabClose}
      />

      {/* Vertical Split: Editor (top) and Results (bottom) */}
      <div style={{ flex: 1, minHeight: 0 }}>
        <PanelGroup
          direction="vertical"
          onLayout={handleVerticalResize}
        >
          {/* Query Editor Panel */}
          <Panel
            defaultSize={verticalSplitSize}
            minSize={20}
            maxSize={80}
          >
            <div style={{ height: '100%', padding: '16px', display: 'flex', flexDirection: 'column' }}>
              <div style={{ flex: 1, minHeight: 0 }}>
                <QueryEditor
                  value={activeTab.query}
                  onChange={handleQueryChange}
                  onExecute={handleExecute}
                  loading={loading}
                  height={undefined}
                  onNaturalLanguageQuery={onNaturalLanguageQuery}
                  autoExportCSV={autoExportCSV}
                  autoExportJSON={autoExportJSON}
                  onAutoExportChange={handleAutoExportChange}
                />
              </div>
            </div>
          </Panel>

          {/* Resize Handle */}
          <PanelResizeHandle 
            className="resize-handle resize-handle-vertical"
            style={{ 
              background: '#e8e8e8',
              borderTop: '1px solid #d9d9d9',
              borderBottom: '1px solid #d9d9d9'
            }}
          />

          {/* Query Results Panel */}
          <Panel
            defaultSize={100 - verticalSplitSize}
            minSize={20}
            maxSize={80}
          >
            <div style={{ height: '100%', padding: '16px', display: 'flex', flexDirection: 'column' }}>
              <div style={{ flex: 1, minHeight: 0 }}>
                {activeTab.results ? (
                  <QueryResults
                    columns={activeTab.results.columns}
                    rows={activeTab.results.rows}
                    rowCount={activeTab.results.rowCount}
                    executionTimeMs={activeTab.results.executionTimeMs}
                    truncated={activeTab.results.truncated}
                    loading={loading}
                    query={activeTab.query}
                    autoExportCSV={autoExportCSV}
                    autoExportJSON={autoExportJSON}
                  />
                ) : (
                  <QueryResults
                    columns={[]}
                    rows={[]}
                    rowCount={0}
                    executionTimeMs={0}
                    truncated={false}
                    loading={loading}
                    query={activeTab.query}
                    autoExportCSV={autoExportCSV}
                    autoExportJSON={autoExportJSON}
                  />
                )}
              </div>
            </div>
          </Panel>
        </PanelGroup>
      </div>
    </div>
  );
};

export default QueryPanel;