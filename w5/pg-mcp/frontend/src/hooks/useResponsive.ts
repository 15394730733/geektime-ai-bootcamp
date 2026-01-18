/**
 * Custom hook for responsive design utilities
 */

import { useState, useEffect } from 'react';
import { LAYOUT_CONSTRAINTS } from '../types/layout';
import { getLayoutMode } from '../utils/layout';

export interface ResponsiveState {
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  screenWidth: number;
  screenHeight: number;
  layoutMode: 'mobile' | 'desktop' | 'constrained';
}

/**
 * Hook to track responsive breakpoints and screen dimensions
 */
export const useResponsive = (): ResponsiveState => {
  const [state, setState] = useState<ResponsiveState>(() => {
    const width = typeof window !== 'undefined' ? window.innerWidth : 1024;
    const height = typeof window !== 'undefined' ? window.innerHeight : 768;
    
    return {
      isMobile: width < LAYOUT_CONSTRAINTS.MOBILE_BREAKPOINT,
      isTablet: width >= LAYOUT_CONSTRAINTS.MOBILE_BREAKPOINT && width < 1024,
      isDesktop: width >= 1024,
      screenWidth: width,
      screenHeight: height,
      layoutMode: getLayoutMode(),
    };
  });

  useEffect(() => {
    const handleResize = () => {
      const width = window.innerWidth;
      const height = window.innerHeight;
      
      setState({
        isMobile: width < LAYOUT_CONSTRAINTS.MOBILE_BREAKPOINT,
        isTablet: width >= LAYOUT_CONSTRAINTS.MOBILE_BREAKPOINT && width < 1024,
        isDesktop: width >= 1024,
        screenWidth: width,
        screenHeight: height,
        layoutMode: getLayoutMode(),
      });
    };

    window.addEventListener('resize', handleResize);
    
    // Call once to set initial state
    handleResize();
    
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return state;
};

/**
 * Hook to detect if screen is mobile size
 */
export const useIsMobile = (): boolean => {
  const { isMobile } = useResponsive();
  return isMobile;
};