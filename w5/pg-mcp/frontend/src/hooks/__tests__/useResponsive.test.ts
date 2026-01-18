/**
 * Tests for useResponsive hook
 */

import { renderHook } from '@testing-library/react';
import { useResponsive } from '../useResponsive';

// Mock window.innerWidth and window.innerHeight
const mockWindowSize = (width: number, height: number) => {
  Object.defineProperty(window, 'innerWidth', {
    writable: true,
    configurable: true,
    value: width,
  });
  Object.defineProperty(window, 'innerHeight', {
    writable: true,
    configurable: true,
    value: height,
  });
};

describe('useResponsive', () => {
  beforeEach(() => {
    // Reset to default desktop size
    mockWindowSize(1024, 768);
  });

  it('should detect desktop layout for wide screens', () => {
    mockWindowSize(1200, 800);
    const { result } = renderHook(() => useResponsive());
    
    expect(result.current.isDesktop).toBe(true);
    expect(result.current.isMobile).toBe(false);
    expect(result.current.layoutMode).toBe('desktop');
    expect(result.current.screenWidth).toBe(1200);
  });

  it('should detect mobile layout for narrow screens', () => {
    mockWindowSize(600, 800);
    const { result } = renderHook(() => useResponsive());
    
    expect(result.current.isMobile).toBe(true);
    expect(result.current.isDesktop).toBe(false);
    expect(result.current.layoutMode).toBe('mobile');
    expect(result.current.screenWidth).toBe(600);
  });

  it('should detect constrained layout for screens too narrow for split layout', () => {
    mockWindowSize(550, 800); // Below 600px needed for split layout (200 + 400 minimum)
    const { result } = renderHook(() => useResponsive());
    
    expect(result.current.layoutMode).toBe('mobile'); // Should be mobile since 550 < 768
    expect(result.current.screenWidth).toBe(550);
  });

  it('should detect constrained layout for tablet screens that cannot fit split layout', () => {
    mockWindowSize(580, 800); // Above mobile but below 600px needed for split layout
    const { result } = renderHook(() => useResponsive());
    
    expect(result.current.layoutMode).toBe('mobile'); // Still mobile since 580 < 768
    expect(result.current.screenWidth).toBe(580);
  });

  it('should detect tablet layout for medium screens', () => {
    mockWindowSize(800, 600);
    const { result } = renderHook(() => useResponsive());
    
    expect(result.current.isTablet).toBe(true);
    expect(result.current.isMobile).toBe(false);
    expect(result.current.isDesktop).toBe(false);
    expect(result.current.layoutMode).toBe('desktop'); // 800px can accommodate split layout
  });
});