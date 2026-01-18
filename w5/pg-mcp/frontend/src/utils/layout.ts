/**
 * Layout utilities for managing panel sizes and localStorage persistence
 */

import { LayoutPreferences, DEFAULT_LAYOUT_PREFERENCES, LAYOUT_CONSTRAINTS } from '../types/layout';

export const LAYOUT_STORAGE_KEY = 'db-query-layout-preferences';

/**
 * Save layout preferences to localStorage
 */
export const saveLayoutPreferences = (preferences: LayoutPreferences): void => {
  try {
    localStorage.setItem(LAYOUT_STORAGE_KEY, JSON.stringify(preferences));
  } catch (error) {
    console.warn('Failed to save layout preferences:', error);
  }
};

/**
 * Load layout preferences from localStorage
 */
export const loadLayoutPreferences = (): LayoutPreferences => {
  try {
    const stored = localStorage.getItem(LAYOUT_STORAGE_KEY);
    if (stored) {
      const parsed = JSON.parse(stored);
      // Validate and merge with defaults
      return {
        horizontalSplitSize: typeof parsed.horizontalSplitSize === 'number' && !isNaN(parsed.horizontalSplitSize)
          ? Math.max(10, Math.min(50, parsed.horizontalSplitSize))
          : DEFAULT_LAYOUT_PREFERENCES.horizontalSplitSize,
        verticalSplitSize: typeof parsed.verticalSplitSize === 'number' && !isNaN(parsed.verticalSplitSize)
          ? Math.max(20, Math.min(80, parsed.verticalSplitSize))
          : DEFAULT_LAYOUT_PREFERENCES.verticalSplitSize,
        metadataPanelCollapsed: typeof parsed.metadataPanelCollapsed === 'boolean'
          ? parsed.metadataPanelCollapsed
          : DEFAULT_LAYOUT_PREFERENCES.metadataPanelCollapsed,
      };
    }
  } catch (error) {
    console.warn('Failed to load layout preferences:', error);
  }
  
  return DEFAULT_LAYOUT_PREFERENCES;
};

/**
 * Calculate default left panel width in pixels based on viewport
 */
export const calculateDefaultLeftPanelWidth = (): number => {
  const viewportWidth = window.innerWidth;
  const targetWidth = 280; // Default 280px as specified in requirements
  
  // Ensure it doesn't exceed 50% of viewport
  const maxWidth = viewportWidth * 0.5;
  return Math.min(targetWidth, maxWidth);
};

/**
 * Convert pixel width to percentage of viewport
 */
export const pixelsToPercentage = (pixels: number): number => {
  const percentage = (pixels / window.innerWidth) * 100;
  // Ensure percentage doesn't exceed 100%
  return Math.min(100, Math.max(0, percentage));
};

/**
 * Convert percentage to pixel width
 */
export const percentageToPixels = (percentage: number): number => {
  return (percentage / 100) * window.innerWidth;
};

/**
 * Check if current viewport meets minimum panel width constraints
 */
export const validatePanelConstraints = (leftPanelPercentage: number): boolean => {
  const viewportWidth = window.innerWidth;
  const leftPanelWidth = (leftPanelPercentage / 100) * viewportWidth;
  const rightPanelWidth = viewportWidth - leftPanelWidth;
  
  return (
    leftPanelWidth >= LAYOUT_CONSTRAINTS.MIN_LEFT_PANEL_WIDTH &&
    rightPanelWidth >= LAYOUT_CONSTRAINTS.MIN_RIGHT_PANEL_WIDTH
  );
};

/**
 * Calculate safe panel sizes that respect minimum width constraints
 */
export const calculateSafePanelSizes = (requestedLeftPercentage: number): {
  leftPercentage: number;
  rightPercentage: number;
} => {
  const viewportWidth = window.innerWidth;
  const minLeftPixels = LAYOUT_CONSTRAINTS.MIN_LEFT_PANEL_WIDTH;
  const minRightPixels = LAYOUT_CONSTRAINTS.MIN_RIGHT_PANEL_WIDTH;
  
  // Calculate minimum percentages
  const minLeftPercentage = (minLeftPixels / viewportWidth) * 100;
  const maxLeftPercentage = ((viewportWidth - minRightPixels) / viewportWidth) * 100;
  
  // Clamp the requested percentage to safe bounds
  const safeLeftPercentage = Math.max(minLeftPercentage, Math.min(maxLeftPercentage, requestedLeftPercentage));
  const safeRightPercentage = 100 - safeLeftPercentage;
  
  return {
    leftPercentage: safeLeftPercentage,
    rightPercentage: safeRightPercentage,
  };
};

/**
 * Check if viewport is mobile size
 */
export const isMobileViewport = (): boolean => {
  return window.innerWidth < LAYOUT_CONSTRAINTS.MOBILE_BREAKPOINT;
};

/**
 * Check if viewport can accommodate split layout with minimum constraints
 */
export const canAccommodateSplitLayout = (): boolean => {
  const viewportWidth = window.innerWidth;
  const minTotalWidth = LAYOUT_CONSTRAINTS.MIN_LEFT_PANEL_WIDTH + LAYOUT_CONSTRAINTS.MIN_RIGHT_PANEL_WIDTH;
  return viewportWidth >= minTotalWidth;
};

/**
 * Get responsive layout mode based on screen size and constraints
 */
export const getLayoutMode = (): 'mobile' | 'desktop' | 'constrained' => {
  const viewportWidth = window.innerWidth;
  
  // First check if we can accommodate split layout
  if (!canAccommodateSplitLayout()) {
    // If we can't accommodate split layout but are above mobile breakpoint, it's constrained
    if (viewportWidth >= LAYOUT_CONSTRAINTS.MOBILE_BREAKPOINT) {
      return 'constrained';
    }
    // Otherwise it's mobile
    return 'mobile';
  }
  
  // If we can accommodate split layout, check if it's mobile size
  if (viewportWidth < LAYOUT_CONSTRAINTS.MOBILE_BREAKPOINT) {
    return 'mobile';
  }
  
  return 'desktop';
};