/**
 * Theme Hooks
 * Custom hooks for working with the theme system
 */

import { useColorModeValue } from '@chakra-ui/react';
import { brandColors, lightThemeColors, darkThemeColors, chartColors, semanticColors } from './colors';

/**
 * Hook to access brand/accent colors
 */
export const useBrandColors = () => {
  return {
    ...brandColors,
    accent: brandColors.primary
  };
};

/**
 * Hook to access semantic colors (success, error, warning)
 */
export const useSemanticColors = () => {
  const success = useColorModeValue(semanticColors.success.light, semanticColors.success.dark);
  const warning = useColorModeValue(semanticColors.warning.light, semanticColors.warning.dark);
  const info = useColorModeValue(semanticColors.info.light, semanticColors.info.dark);
  
  return {
    success,
    warning,
    info
  };
};

/**
 * Hook to access chart colors for data visualization
 */
export const useChartColors = () => {
  const chart1 = useColorModeValue(chartColors.light.chart1, chartColors.dark.chart1);
  const chart2 = useColorModeValue(chartColors.light.chart2, chartColors.dark.chart2);
  const chart3 = useColorModeValue(chartColors.light.chart3, chartColors.dark.chart3);
  const chart4 = useColorModeValue(chartColors.light.chart4, chartColors.dark.chart4);
  const chart5 = useColorModeValue(chartColors.light.chart5, chartColors.dark.chart5);
  
  return {
    chart1,
    chart2,
    chart3,
    chart4,
    chart5,
    chartArray: [chart1, chart2, chart3, chart4, chart5]
  };
};

/**
 * Hook for common UI color needs
 * Provides color values based on current color mode
 */
export const useThemeColors = () => {
  // UI Background colors
  const background = useColorModeValue(lightThemeColors.background, darkThemeColors.background);
  const backgroundAlt = useColorModeValue(lightThemeColors.backgroundAlt, darkThemeColors.backgroundAlt);
  const sidebar = useColorModeValue(lightThemeColors.sidebar, darkThemeColors.sidebar);
  const card = useColorModeValue(lightThemeColors.card, darkThemeColors.card);
  const headerBg = useColorModeValue(lightThemeColors.headerBg, darkThemeColors.headerBg);
  
  // Text colors
  const text = useColorModeValue(lightThemeColors.text, darkThemeColors.text);
  const textSecondary = useColorModeValue(lightThemeColors.textSecondary, darkThemeColors.textSecondary);
  const textTertiary = useColorModeValue(lightThemeColors.textTertiary, darkThemeColors.textTertiary);
  
  // UI element colors
  const border = useColorModeValue(lightThemeColors.border, darkThemeColors.border);
  const input = useColorModeValue(lightThemeColors.input, darkThemeColors.input);
  const inputBg = useColorModeValue(lightThemeColors.inputBg, darkThemeColors.inputBg);
  
  // Interactive element colors
  const buttonHoverBg = useColorModeValue(lightThemeColors.buttonHoverBg, darkThemeColors.buttonHoverBg);
  const buttonHoverBorder = useColorModeValue(lightThemeColors.buttonHoverBorder, darkThemeColors.buttonHoverBorder);
  
  // State colors
  const error = useColorModeValue(lightThemeColors.error, darkThemeColors.error);
  const errorBg = useColorModeValue(lightThemeColors.errorBg, darkThemeColors.errorBg);
  const errorBorder = useColorModeValue(lightThemeColors.errorBorder, darkThemeColors.errorBorder);
  
  // Brand colors (also including the useBrandColors hook)
  const brand = useBrandColors();
  
  return {
    // Background colors
    background,
    backgroundAlt,
    sidebar,
    card,
    headerBg,
    
    // Text colors
    text,
    textSecondary,
    textTertiary,
    
    // UI Element colors
    border,
    input,
    inputBg,
    
    // Interactive element colors
    buttonHoverBg,
    buttonHoverBorder,
    
    // State colors
    error,
    errorBg,
    errorBorder,
    
    // Brand colors
    ...brand
  };
}; 