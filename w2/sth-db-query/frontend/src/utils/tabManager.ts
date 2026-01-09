/**
 * Tab management utility functions
 */

import { QueryTab, QueryResult } from '../types/layout';

/**
 * Generate a unique tab ID
 * @returns Unique tab ID string
 */
export function generateTabId(): string {
  return `tab-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Generate a tab name based on creation time
 * @param createdAt - Creation timestamp
 * @returns Formatted tab name
 */
export function generateTabName(createdAt: Date = new Date()): string {
  const timeString = createdAt.toLocaleTimeString('en-US', {
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
  return `Query ${timeString}`;
}

/**
 * Create a new empty query tab
 * @returns New QueryTab instance
 */
export function createNewTab(): QueryTab {
  const createdAt = new Date();
  return {
    id: generateTabId(),
    name: generateTabName(createdAt),
    query: '',
    results: null,
    isDirty: false,
    createdAt,
  };
}

/**
 * Update a tab's query content and mark as dirty if changed
 * @param tab - Tab to update
 * @param query - New query content
 * @returns Updated tab
 */
export function updateTabQuery(tab: QueryTab, query: string): QueryTab {
  const isDirty = query !== '' && query !== tab.query;
  return {
    ...tab,
    query,
    isDirty,
  };
}

/**
 * Update a tab's results and clear dirty flag
 * @param tab - Tab to update
 * @param results - Query results
 * @returns Updated tab
 */
export function updateTabResults(tab: QueryTab, results: QueryResult | null): QueryTab {
  return {
    ...tab,
    results,
    isDirty: false, // Clear dirty flag after successful execution
  };
}

/**
 * Mark a tab as clean (not dirty)
 * @param tab - Tab to mark as clean
 * @returns Updated tab
 */
export function markTabClean(tab: QueryTab): QueryTab {
  return {
    ...tab,
    isDirty: false,
  };
}

/**
 * Check if a tab has unsaved changes
 * @param tab - Tab to check
 * @returns true if tab has unsaved changes
 */
export function hasUnsavedChanges(tab: QueryTab): boolean {
  return tab.isDirty && tab.query.trim() !== '';
}

/**
 * Find the next available tab ID when closing a tab
 * @param tabs - Array of tabs
 * @param closingTabId - ID of tab being closed
 * @param currentActiveId - Currently active tab ID
 * @returns ID of tab to activate next, or null if no tabs remain
 */
export function getNextActiveTabId(
  tabs: QueryTab[],
  closingTabId: string,
  currentActiveId: string
): string | null {
  const remainingTabs = tabs.filter(tab => tab.id !== closingTabId);
  
  if (remainingTabs.length === 0) {
    return null;
  }

  // If we're not closing the active tab, keep the current active tab
  if (closingTabId !== currentActiveId) {
    return currentActiveId;
  }

  // Find the index of the closing tab
  const closingIndex = tabs.findIndex(tab => tab.id === closingTabId);
  
  // Try to activate the tab to the right, then left
  if (closingIndex < remainingTabs.length) {
    return remainingTabs[closingIndex].id;
  } else if (closingIndex > 0) {
    return remainingTabs[closingIndex - 1].id;
  } else {
    return remainingTabs[0].id;
  }
}

/**
 * Validate tab state consistency
 * @param tabs - Array of tabs to validate
 * @param activeTabId - Currently active tab ID
 * @returns Validation result with any issues found
 */
export function validateTabState(tabs: QueryTab[], activeTabId: string): {
  isValid: boolean;
  issues: string[];
} {
  const issues: string[] = [];

  // Check if tabs array is valid
  if (!Array.isArray(tabs)) {
    issues.push('Tabs must be an array');
    return { isValid: false, issues };
  }

  // Check if there's at least one tab
  if (tabs.length === 0) {
    issues.push('At least one tab must exist');
  }

  // Check for duplicate tab IDs
  const tabIds = tabs.map(tab => tab.id);
  const uniqueIds = new Set(tabIds);
  if (tabIds.length !== uniqueIds.size) {
    issues.push('Duplicate tab IDs found');
  }

  // Check if active tab exists
  const activeTabExists = tabs.some(tab => tab.id === activeTabId);
  if (!activeTabExists && tabs.length > 0) {
    issues.push(`Active tab ID "${activeTabId}" not found in tabs`);
  }

  // Validate individual tabs
  tabs.forEach((tab, index) => {
    if (!tab.id || typeof tab.id !== 'string') {
      issues.push(`Tab at index ${index} has invalid ID`);
    }
    if (!tab.name || typeof tab.name !== 'string') {
      issues.push(`Tab at index ${index} has invalid name`);
    }
    if (typeof tab.query !== 'string') {
      issues.push(`Tab at index ${index} has invalid query`);
    }
    if (typeof tab.isDirty !== 'boolean') {
      issues.push(`Tab at index ${index} has invalid isDirty flag`);
    }
    if (!(tab.createdAt instanceof Date)) {
      issues.push(`Tab at index ${index} has invalid createdAt`);
    }
  });

  return {
    isValid: issues.length === 0,
    issues,
  };
}

/**
 * Create initial tab state with one empty tab
 * @returns Initial tab state
 */
export function createInitialTabState(): { tabs: QueryTab[]; activeTabId: string } {
  const initialTab = createNewTab();
  return {
    tabs: [initialTab],
    activeTabId: initialTab.id,
  };
}