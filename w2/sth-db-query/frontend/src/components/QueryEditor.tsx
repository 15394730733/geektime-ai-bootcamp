/**
 * SQL Query Editor Component
 *
 * Monaco-based SQL editor with syntax highlighting
 */

import React, { useRef, useState } from 'react';
import { Button, Space, Segmented, Checkbox } from 'antd';
import { PlayCircleOutlined, ClearOutlined, CodeOutlined, MessageOutlined } from '@ant-design/icons';
import Editor, { OnMount } from '@monaco-editor/react';
import type * as monaco from 'monaco-editor';

// Configure Monaco to avoid CDN worker loading issues
const beforeMount = (monaco: typeof import('monaco-editor')) => {
  // Disable worker loading to prevent CDN timeout
  (self as any).MonacoEnvironment = {
    getWorker: () => null as any
  };
};

interface QueryEditorProps {
  value: string;
  onChange: (value: string) => void;
  onExecute: () => void;
  loading?: boolean;
  height?: number;
  onNaturalLanguageQuery?: (prompt: string) => Promise<void>;
  autoExportCSV?: boolean;
  autoExportJSON?: boolean;
  onAutoExportChange?: (csv: boolean, json: boolean) => void;
}

type QueryMode = 'sql' | 'natural';

export const QueryEditor: React.FC<QueryEditorProps> = ({
  value,
  onChange,
  onExecute,
  loading = false,
  height,
  onNaturalLanguageQuery,
  autoExportCSV = true,
  autoExportJSON = true,
  onAutoExportChange,
}) => {
  const editorRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(null);
  const [queryMode, setQueryMode] = useState<QueryMode>('sql');
  const [naturalLanguageInput, setNaturalLanguageInput] = useState('');
  const [editorReady, setEditorReady] = useState(false);

  console.log('QueryEditor rendering, value:', value, 'height:', height);

  const handleEditorDidMount: OnMount = (editor, monaco) => {
    editorRef.current = editor;

    console.log('Monaco Editor mounted', editor);

    // Configure SQL language features
    monaco.languages.setLanguageConfiguration('sql', {
      comments: {
        lineComment: '--',
        blockComment: ['/*', '*/']
      },
      brackets: [
        ['(', ')'],
        ['[', ']']
      ],
      autoClosingPairs: [
        { open: '(', close: ')' },
        { open: '[', close: ']' },
        { open: "'", close: "'" },
        { open: '"', close: '"' }
      ],
      surroundingPairs: [
        { open: '(', close: ')' },
        { open: '[', close: ']' },
        { open: "'", close: "'" },
        { open: '"', close: '"' }
      ]
    });

    // Add keyboard shortcut for query execution (Ctrl+Enter or Cmd+Enter)
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
      if (!loading) {
        onExecute();
      }
    });

    // Mark editor as ready
    setEditorReady(true);

    // Focus the editor after a short delay
    setTimeout(() => {
      editor.focus();
      console.log('Editor focused, readOnly:', editor.getOption(monaco.editor.EditorOption.readOnly));
    }, 100);
  };

  const handleEditorChange = (newValue: string | undefined) => {
    console.log('Editor value changed:', newValue);
    onChange(newValue || '');
  };

  const handleClear = () => {
    if (queryMode === 'sql') {
      onChange('');
      if (editorRef.current) {
        editorRef.current.focus();
      }
    } else {
      setNaturalLanguageInput('');
    }
  };

  const handleNaturalLanguageSubmit = async () => {
    if (!naturalLanguageInput.trim() || !onNaturalLanguageQuery) return;
    
    try {
      await onNaturalLanguageQuery(naturalLanguageInput);
      // After successful conversion, switch to SQL mode to show the generated SQL
      setQueryMode('sql');
    } catch (error) {
      console.error('Natural language query failed:', error);
    }
  };

  console.log('About to render Editor component');

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Toolbar */}
      <div style={{ 
        padding: '12px 16px', 
        borderBottom: '1px solid #d9d9d9',
        background: '#fafafa',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <Space>
          <Segmented
            value={queryMode}
            onChange={(value) => setQueryMode(value as QueryMode)}
            options={[
              {
                label: 'SQL',
                value: 'sql',
                icon: <CodeOutlined />,
              },
              {
                label: 'Natural Language',
                value: 'natural',
                icon: <MessageOutlined />,
              },
            ]}
            style={{ padding: '4px', fontSize: '14px' }}
          />
        </Space>
        <Space>
          <Checkbox
            checked={autoExportCSV}
            onChange={(e) => onAutoExportChange?.(e.target.checked, autoExportJSON)}
          >
            CSV
          </Checkbox>
          <Checkbox
            checked={autoExportJSON}
            onChange={(e) => onAutoExportChange?.(autoExportCSV, e.target.checked)}
          >
            JSON
          </Checkbox>
          <Button
            icon={<ClearOutlined />}
            onClick={handleClear}
            size="small"
          >
            Clear
          </Button>
          <Button
            type="primary"
            icon={<PlayCircleOutlined />}
            onClick={queryMode === 'sql' ? onExecute : handleNaturalLanguageSubmit}
            loading={loading}
            size="small"
          >
            {queryMode === 'sql' ? 'Execute (Ctrl+Enter)' : 'Convert & Execute'}
          </Button>
        </Space>
      </div>
      
      {/* Editor or Natural Language Input */}
      <div style={{ 
        flex: 1, 
        minHeight: '100px', 
        background: 'white',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden'
      }}>
        {queryMode === 'sql' ? (
          <Editor
            height="100%"
            language="sql"
            value={value}
            onChange={handleEditorChange}
            onMount={handleEditorDidMount}
            beforeMount={beforeMount}
            options={{
              minimap: { enabled: false },
              scrollBeyondLastLine: false,
              fontSize: 14,
              fontFamily: 'Monaco, Menlo, "Ubuntu Mono", monospace',
              lineNumbers: 'on',
              roundedSelection: false,
              scrollbar: {
                vertical: 'auto',
                horizontal: 'auto'
              },
              automaticLayout: true,
              wordWrap: 'on',
              tabSize: 2,
              insertSpaces: true,
              folding: true,
              foldingStrategy: 'indentation',
              showFoldingControls: 'always',
              matchBrackets: 'always',
              autoIndent: 'full',
              formatOnPaste: true,
              formatOnType: true,
              suggest: {
                showKeywords: true,
                showSnippets: true,
                showFunctions: true
              },
              readOnly: false,
              domReadOnly: false,
            }}
            theme="vs"
            loading={loading && !editorReady ? <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>Loading editor...</div> : undefined}
          />
        ) : (
          <div style={{ padding: '16px', height: '100%', display: 'flex', flexDirection: 'column' }}>
            <textarea
              value={naturalLanguageInput}
              onChange={(e) => setNaturalLanguageInput(e.target.value)}
              placeholder="Describe what data you want to see... (e.g., 'Show me all users who registered in the last 7 days')"
              style={{
                flex: 1,
                width: '100%',
                padding: '12px',
                fontSize: '14px',
                fontFamily: 'system-ui, -apple-system, sans-serif',
                border: '1px solid #d9d9d9',
                borderRadius: '4px',
                resize: 'none',
                outline: 'none',
              }}
              onFocus={(e) => {
                e.target.style.borderColor = '#1890ff';
                e.target.style.boxShadow = '0 0 0 2px rgba(24, 144, 255, 0.2)';
              }}
              onBlur={(e) => {
                e.target.style.borderColor = '#d9d9d9';
                e.target.style.boxShadow = 'none';
              }}
            />
            <div style={{ marginTop: '8px', fontSize: '12px', color: '#8c8c8c' }}>
              💡 Tip: Describe your query in plain English, and we'll convert it to SQL for you.
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
