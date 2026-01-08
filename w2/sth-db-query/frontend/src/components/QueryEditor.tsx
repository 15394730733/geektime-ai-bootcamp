/**
 * SQL Query Editor Component
 *
 * Monaco-based SQL editor with syntax highlighting
 */

import React, { useRef, useEffect } from 'react';
import { Card, Button, Space } from 'antd';
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
  height = 300
}) => {
  const editorRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(null);

  const handleEditorDidMount = (editor: monaco.editor.IStandaloneCodeEditor) => {
    editorRef.current = editor;
    
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

    // Focus the editor
    editor.focus();
  };

  const handleEditorChange = (newValue: string | undefined) => {
    onChange(newValue || '');
  };

  const handleClear = () => {
    onChange('');
    if (editorRef.current) {
      editorRef.current.focus();
    }
  };

  return (
    <Card
      title="SQL Query"
      extra={
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
            Execute
          </Button>
        </Space>
      }
    >
      <div style={{ border: '1px solid #d9d9d9', borderRadius: '4px' }}>
        <Editor
          height={height}
          language="sql"
          value={value}
          onChange={handleEditorChange}
          onMount={handleEditorDidMount}
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
            }
          }}
          theme="vs"
        />
      </div>
    </Card>
  );
};
