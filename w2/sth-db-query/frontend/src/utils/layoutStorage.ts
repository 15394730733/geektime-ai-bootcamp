/**
 * localStorage utility functions for layout persistence
 */

import { LayoutPreferences, DEFAULT_LAYOUT_PREFERENCES } from '../types/layout';

const LAYOUT_STORAGE_KEY = 'db-query-layout-preferences';

/**
 * Save layout preferences to localStorage
 * @param preferences - Layout preferences to save
 * @returns true if saved successfully, false otherwise
 */
export function saveLayoutPreferences(preferences: LayoutPreferences): boolean {
  try {
    const json = JSON.stringify(preferences);
    localStorage.setItem(LAYOUT_STORAGE_KEY, json);
    return true;
  } catch (error) {
    console.error('Failed to save layout preferences:', error);
    return false;
  }
}

/**
 * Load layout preferences from localStorage
 * @returns Layout preferences or default values if not found or invalid
 */
export function loadLayoutPreferences(): LayoutPreferences {
  try {
    const json = localStorage.getItem(LAYOUT_STORAGE_KEY);
    if (!json) {
      return DEFAULT_LAYOUT_PREFERENCES;
    }

    const preferences = JSON.parse(json) as LayoutPreferences;

    // Validate the loaded preferences
    if (!isValidLayoutPreferences(preferences)) {
      console.warn('Invalid layout preferences found, using defaults');
      return DEFAULT_LAYOUT_PREFERENCES;
    }

    return preferences;
  } catch (error) {
    console.error('Failed to load layout preferences:', error);
    return DEFAULT_LAYOUT_PREFERENCES;
  }
}

/**
 * Clear layout preferences from localStorage
 * @returns true if cleared successfully, false otherwise
 */
export function clearLayoutPreferences(): boolean {
  try {
    localStorage.removeItem(LAYOUT_STORAGE_KEY);
    return true;
  } catch (error) {
    console.error('Failed to clear layout preferences:', error);
    return false;
  }
}

/**
 * Validate layout preferences object
 * @param preferences - Preferences to validate
 * @returns true if valid, false otherwise
 */
function isValidLayoutPreferences(preferences: any): preferences is LayoutPreferences {
  if (!preferences || typeof preferences !== 'object') {
    return false;
  }

  const { horizontalSplitSize, verticalSplitSize, metadataPanelCollapsed } = preferences;

  // Check types
  if (typeof horizontalSplitSize !== 'number' || typeof verticalSplitSize !== 'number') {
    return false;
  }

  if (typeof metadataPanelCollapsed !== 'boolean') {
    return false;
  }

  // Check ranges (0-100 for percentages)
  if (horizontalSplitSize < 0 || horizontalSplitSize > 100) {
    return false;
  }

  if (verticalSplitSize < 0 || verticalSplitSize > 100) {
    return false;
  }

  return true;
}

/**
 * Constrain a split size value to valid range
 * @param size - Size value to constrain
 * @returns Constrained size value (0-100)
 */
export function constrainSplitSize(size: number): number {
  return Math.max(0, Math.min(100, size));
}

/**
 * Save horizontal split size
 * @param size - Size percentage (0-100)
 */
export function saveHorizontalSplitSize(size: number): void {
  const preferences = loadLayoutPreferences();
  preferences.horizontalSplitSize = constrainSplitSize(size);
  saveLayoutPreferences(preferences);
}

/**
 * Save vertical split size
 * @param size - Size percentage (0-100)
 */
export function saveVerticalSplitSize(size: number): void {
  const preferences = loadLayoutPreferences();
  preferences.verticalSplitSize = constrainSplitSize(size);
  saveLayoutPreferences(preferences);
}

/**
 * Save metadata panel collapsed state
 * @param collapsed - Whether the metadata panel is collapsed
 */
export function saveMetadataPanelCollapsed(collapsed: boolean): void {
  const preferences = loadLayoutPreferences();
  preferences.metadataPanelCollapsed = collapsed;
  saveLayoutPreferences(preferences);
}
