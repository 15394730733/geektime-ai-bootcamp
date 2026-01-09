/**
 * Property tests for layout persistence utilities
 * 
 * Tests the correctness properties for layout management and localStorage persistence.
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import * as fc from 'fast-check';
import { 
  saveLayoutPreferences, 
  loadLayoutPreferences, 
  calculateDefaultLeftPanelWidth,
  pixelsToPercentage,
  percentageToPixels,
  LAYOUT_STORAGE_KEY 
} from '../layout';
import { LayoutPreferences, DEFAULT_LAYOUT_PREFERENCES } from '../../types/layout';

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};

// Mock window.innerWidth
Object.defineProperty(window, 'innerWidth', {
  writable: true,
  configurable: true,
  value: 1920,
});

beforeEach(() => {
  vi.clearAllMocks();
  Object.defineProperty(global, 'localStorage', {
    value: localStorageMock,
    writable: true,
  });
  window.innerWidth = 1920;
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe('Layout Property Tests', () => {
  /**
   * Property 1: Layout Persistence Round-Trip
   * **Validates: Requirements 1.5, 5.3**
   */
  it('property: layout persistence round-trip', () => {
    fc.assert(fc.property(
      fc.record({
        horizontalSplitSize: fc.float({ min: 10, max: 50 }).filter(n => !isNaN(n)),
        verticalSplitSize: fc.float({ min: 20, max: 80 }).filter(n => !isNaN(n)),
        metadataPanelCollapsed: fc.boolean(),
      }),
      (layoutPrefs: LayoutPreferences) => {
        // Save preferences to localStorage
        saveLayoutPreferences(layoutPrefs);
        
        // Verify setItem was called with correct data
        expect(localStorageMock.setItem).toHaveBeenCalledWith(
          LAYOUT_STORAGE_KEY,
          JSON.stringify(layoutPrefs)
        );
        
        // Mock the getItem to return the saved data
        localStorageMock.getItem.mockReturnValue(JSON.stringify(layoutPrefs));
        
        // Load preferences from localStorage
        const loadedPrefs = loadLayoutPreferences();
        
        // Verify round-trip consistency
        expect(loadedPrefs.horizontalSplitSize).toBeCloseTo(layoutPrefs.horizontalSplitSize, 5);
        expect(loadedPrefs.verticalSplitSize).toBeCloseTo(layoutPrefs.verticalSplitSize, 5);
        expect(loadedPrefs.metadataPanelCollapsed).toBe(layoutPrefs.metadataPanelCollapsed);
      }
    ), { numRuns: 100 });
  });

  /**
   * Property 2: Panel Resize Constraints
   * **Validates: Requirements 1.4, 6.3**
   */
  it('property: panel resize constraints are enforced', () => {
    fc.assert(fc.property(
      fc.record({
        horizontalSplitSize: fc.float({ min: -100, max: 200 }), // Include invalid values
        verticalSplitSize: fc.float({ min: -100, max: 200 }),   // Include invalid values
        metadataPanelCollapsed: fc.boolean(),
      }),
      (invalidLayoutPrefs) => {
        // Mock localStorage to return invalid data
        localStorageMock.getItem.mockReturnValue(JSON.stringify(invalidLayoutPrefs));
        
        // Load preferences - should be constrained to valid ranges
        const loadedPrefs = loadLayoutPreferences();
        
        // Verify horizontal split size constraints (10-50%)
        expect(loadedPrefs.horizontalSplitSize).toBeGreaterThanOrEqual(10);
        expect(loadedPrefs.horizontalSplitSize).toBeLessThanOrEqual(50);
        
        // Verify vertical split size constraints (20-80%)
        expect(loadedPrefs.verticalSplitSize).toBeGreaterThanOrEqual(20);
        expect(loadedPrefs.verticalSplitSize).toBeLessThanOrEqual(80);
        
        // Boolean should be preserved
        expect(typeof loadedPrefs.metadataPanelCollapsed).toBe('boolean');
      }
    ), { numRuns: 100 });
  });

  /**
   * Property 3: Default values when localStorage fails
   * **Validates: Requirements 1.5**
   */
  it('property: defaults used when localStorage is unavailable', () => {
    fc.assert(fc.property(
      fc.oneof(
        fc.constant(null),
        fc.constant(undefined),
        fc.constant('invalid json'),
        fc.constant('{}'),
        fc.constant('{"invalid": "data"}')
      ),
      (invalidStorageValue) => {
        // Mock localStorage to return invalid data
        localStorageMock.getItem.mockReturnValue(invalidStorageValue);
        
        // Load preferences - should return defaults
        const loadedPrefs = loadLayoutPreferences();
        
        // Verify defaults are used
        expect(loadedPrefs.horizontalSplitSize).toBe(DEFAULT_LAYOUT_PREFERENCES.horizontalSplitSize);
        expect(loadedPrefs.verticalSplitSize).toBe(DEFAULT_LAYOUT_PREFERENCES.verticalSplitSize);
        expect(loadedPrefs.metadataPanelCollapsed).toBe(DEFAULT_LAYOUT_PREFERENCES.metadataPanelCollapsed);
      }
    ), { numRuns: 50 });
  });

  /**
   * Property 4: Pixel/Percentage conversion consistency
   * **Validates: Requirements 1.4**
   */
  it('property: pixel-percentage conversion round-trip', () => {
    fc.assert(fc.property(
      fc.tuple(
        fc.integer({ min: 800, max: 3840 }), // viewport width
        fc.integer({ min: 100, max: 1000 })  // pixel value
      ),
      ([viewportWidth, pixels]) => {
        // Set viewport width
        window.innerWidth = viewportWidth;
        
        // Convert pixels to percentage and back
        const percentage = pixelsToPercentage(pixels);
        const backToPixels = percentageToPixels(percentage);
        
        // Verify percentage is in valid range
        expect(percentage).toBeGreaterThanOrEqual(0);
        expect(percentage).toBeLessThanOrEqual(100);
        
        // Verify round-trip consistency (allow small floating point errors)
        // Only check round-trip if percentage wasn't clamped to 100%
        if (pixels <= viewportWidth) {
          expect(backToPixels).toBeCloseTo(pixels, 1);
        } else {
          // If pixels > viewportWidth, percentage should be clamped to 100%
          expect(percentage).toBe(100);
          expect(backToPixels).toBe(viewportWidth);
        }
      }
    ), { numRuns: 100 });
  });

  /**
   * Property 5: Default panel width calculation
   * **Validates: Requirements 1.2, 1.4**
   */
  it('property: default panel width respects viewport constraints', () => {
    fc.assert(fc.property(
      fc.integer({ min: 600, max: 4000 }), // viewport width
      (viewportWidth) => {
        // Set viewport width
        window.innerWidth = viewportWidth;
        
        // Calculate default left panel width
        const defaultWidth = calculateDefaultLeftPanelWidth();
        
        // Verify constraints
        expect(defaultWidth).toBeGreaterThan(0);
        expect(defaultWidth).toBeLessThanOrEqual(viewportWidth * 0.5); // Max 50% of viewport
        expect(defaultWidth).toBeLessThanOrEqual(280); // Target width or less
        
        // For large viewports, should be exactly 280px
        if (viewportWidth >= 560) { // 280 * 2
          expect(defaultWidth).toBe(280);
        }
      }
    ), { numRuns: 100 });
  });

  /**
   * Property 6: Save operation handles errors gracefully
   * **Validates: Requirements 1.5**
   */
  it('property: save operation is resilient to localStorage errors', () => {
    fc.assert(fc.property(
      fc.record({
        horizontalSplitSize: fc.float({ min: 10, max: 50 }),
        verticalSplitSize: fc.float({ min: 20, max: 80 }),
        metadataPanelCollapsed: fc.boolean(),
      }),
      (layoutPrefs: LayoutPreferences) => {
        // Mock localStorage.setItem to throw an error
        localStorageMock.setItem.mockImplementation(() => {
          throw new Error('localStorage not available');
        });
        
        // Save operation should not throw
        expect(() => saveLayoutPreferences(layoutPrefs)).not.toThrow();
        
        // Verify setItem was attempted
        expect(localStorageMock.setItem).toHaveBeenCalled();
      }
    ), { numRuns: 50 });
  });
});

describe('Layout Unit Tests', () => {
  it('loads default preferences when localStorage is empty', () => {
    localStorageMock.getItem.mockReturnValue(null);
    
    const prefs = loadLayoutPreferences();
    
    expect(prefs).toEqual(DEFAULT_LAYOUT_PREFERENCES);
  });

  it('saves preferences to localStorage with correct key', () => {
    const testPrefs: LayoutPreferences = {
      horizontalSplitSize: 25,
      verticalSplitSize: 60,
      metadataPanelCollapsed: true,
    };
    
    saveLayoutPreferences(testPrefs);
    
    expect(localStorageMock.setItem).toHaveBeenCalledWith(
      LAYOUT_STORAGE_KEY,
      JSON.stringify(testPrefs)
    );
  });

  it('calculates 280px default width for large viewports', () => {
    window.innerWidth = 1920;
    
    const width = calculateDefaultLeftPanelWidth();
    
    expect(width).toBe(280);
  });

  it('constrains default width to 50% of small viewports', () => {
    window.innerWidth = 400;
    
    const width = calculateDefaultLeftPanelWidth();
    
    expect(width).toBe(200); // 50% of 400px
  });
});