/**
 * Layout-related type definitions for the Query Page
 */

/**
 * Represents a single query tab in the query editor
 */
export interface QueryTab {
  id: string;           // UUID
  name: string;         // "Query HH:MM:SS"
  query: string;        // SQL content
  results: QueryResult | null;
  isDirty: boolean;     // Has unsaved changes
  createdAt: Date;
}

/**
 * Query execution result
 */
export interface QueryResult {
  columns: string[];
  rows: any[][];
  rowCount: number;
  executionTimeMs: number;
  truncated: boolean;
}

/**
 * Layout preferences stored in localStorage
 */
export interface LayoutPreferences {
  horizontalSplitSize: number;  // 0-100, default 20
  verticalSplitSize: number;    // 0-100, default 50
  metadataPanelCollapsed: boolean;
}

/**
 * Query page state
 */
export interface QueryPageState {
  tabs: QueryTab[];
  activeTabId: string;
  horizontalSplitSize: number; // percentage
  verticalSplitSize: number;   // percentage
}

/**
 * Default layout preferences
 */
export const DEFAULT_LAYOUT_PREFERENCES: LayoutPreferences = {
  horizontalSplitSize: 20,
  verticalSplitSize: 30,  // Editor takes 30%, Results take 70%
  metadataPanelCollapsed: false,
};

/**
 * Layout constraints
 */
export const LAYOUT_CONSTRAINTS = {
  MIN_LEFT_PANEL_WIDTH: 200,    // pixels
  MAX_LEFT_PANEL_WIDTH: 50,     // percentage of viewport
  MIN_RIGHT_PANEL_WIDTH: 400,   // pixels
  MIN_EDITOR_HEIGHT: 150,       // pixels
  MIN_RESULTS_HEIGHT: 150,      // pixels
  MOBILE_BREAKPOINT: 768,       // pixels
} as const;
