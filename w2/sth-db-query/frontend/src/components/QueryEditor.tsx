/**
 * SQL Query Editor Component
 *
 * Monaco-based SQL editor with syntax highlighting
 */

import React, { useRef } from 'react';
import { Button, Space } from 'antd';
import { PlayCircleOutlined, ClearOutlined } from '@ant-design/icons';
import Editor from '@monaco-editor/react';
import * as monaco from 'monaco-editor';

interface QueryEditorProps {
  value: string;
  onChange: (value: string) => void;
  onExecute: () => void;
  loading?: boolean;
  height?: number;
}

export const QueryEditor: React.FC<QueryEditorProps> = ({
  value,
  onChange,
  onExecute,
  loading = false,
  height
}) => {
  const editorRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(null);

  console.log('QueryEditor rendering, value:', value, 'height:', height);

  const handleEditorDidMount = (editor: monaco.editor.IStandaloneCodeEditor) => {
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
    onChange('');
    if (editorRef.current) {
      editorRef.current.focus();
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
        <span style={{ fontWeight: 600, fontSize: '14px' }}>SQL Query</span>
        <Space>
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
            onClick={onExecute}
            loading={loading}
            size="small"
          >
            Execute (Ctrl+Enter)
          </Button>
        </Space>
      </div>
      
      {/* Editor */}
      <div style={{ 
        flex: 1, 
        minHeight: '300px', 
        background: 'white',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden'
      }}>
        <Editor
          height="100%"
          language="sql"
          value={value}
          onChange={handleEditorChange}
          onMount={handleEditorDidMount}
          loading="Loading editor..."
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
        />
      </div>
    </div>
  );
};
