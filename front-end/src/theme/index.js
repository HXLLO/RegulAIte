/**
 * Theme Module Index
 * Export all theme-related utilities for easier imports
 */

// Import needed for applyThemeVariables
import { cssVariables } from './themeConfig'; 

// Color definitions
export * from './colors';

// Theme configurations
export * from './themeConfig';

// Theme hooks
export * from './useThemeColors';

// Export default chakra theme
export { chakraTheme } from './themeConfig';

// Export ThemeContext utilities
export { useTheme } from '../contexts/ThemeContext';

// Utility function to apply CSS variables
export const applyThemeVariables = (isDark = false) => {
  const root = document.documentElement;
  const variables = isDark ? cssVariables.dark : cssVariables.light;
  
  // Apply CSS variables to :root element
  Object.entries(variables).forEach(([key, value]) => {
    root.style.setProperty(key, value);
  });
};

