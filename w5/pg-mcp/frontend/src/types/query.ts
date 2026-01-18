/**
 * Query-related types for the application
 */

import { QueryTab } from './layout';

export interface TabBarProps {
  tabs: QueryTab[];
  activeTabId: string;
  databaseName: string | null;
  onTabChange: (tabId: string) => void;
  onTabCreate: () => void;
  onTabClose: (tabId: string) => void;
}

// Re-export from layout types for convenience
export type { QueryTab, QueryResult } from './layout';