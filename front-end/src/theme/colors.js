/**
 * RegulAIte Theme Colors
 * This file contains all color definitions used throughout the application
 */

// App accent color (brand color) and variants
export const brandColors = {
  primary: '#4415b6', // Main accent color
  primaryHover: '#3a1296',
  primaryLight: '#4415b615',
  primaryLighter: '#4415b608',
  primaryMedium: '#4415b630',
  primaryDark: '#35108f'
};

// Light theme colors
export const lightThemeColors = {
  // Backgrounds
  background: 'white',
  backgroundAlt: 'gray.50',
  sidebar: 'white',
  card: 'white',
  headerBg: 'white',
  
  // Text
  text: 'gray.800',
  textSecondary: 'gray.500',
  textTertiary: 'gray.400',
  
  // UI elements
  border: 'gray.200',
  input: 'gray.200',
  inputBg: 'white',
  
  // Interactive elements
  buttonHoverBg: 'purple.50',
  buttonHoverBorder: 'purple.300',
  
  // State colors
  error: 'red.800',
  errorBg: 'red.100',
  errorBorder: 'red.200',
  
  // CSS variables for TailwindCSS
  cssVariables: {
    '--background': '0 0% 100%',
    '--foreground': '240 10% 3.9%',
    '--card': '0 0% 100%',
    '--card-foreground': '240 10% 3.9%',
    '--popover': '0 0% 100%',
    '--popover-foreground': '240 10% 3.9%',
    '--primary': '262 80% 40%',
    '--primary-foreground': '0 0% 98%',
    '--secondary': '240 4.8% 95.9%',
    '--secondary-foreground': '240 5.9% 10%',
    '--muted': '240 4.8% 95.9%',
    '--muted-foreground': '240 3.8% 46.1%',
    '--accent': '262 80% 40%',
    '--accent-foreground': '0 0% 98%',
    '--destructive': '0 84.2% 60.2%',
    '--destructive-foreground': '0 0% 98%',
    '--border': '240 5.9% 90%',
    '--input': '240 5.9% 90%',
    '--ring': '262 80% 40%',
    '--radius': '0.5rem'
  }
};

// Dark theme colors
export const darkThemeColors = {
  // Backgrounds
  background: 'gray.800',
  backgroundAlt: 'gray.900',
  sidebar: 'gray.800',
  card: 'gray.700',
  headerBg: 'gray.800',
  
  // Text
  text: 'gray.200',
  textSecondary: 'gray.400',
  textTertiary: 'gray.500',
  
  // UI elements
  border: 'gray.700',
  input: 'gray.700',
  inputBg: 'gray.700',
  
  // Interactive elements
  buttonHoverBg: 'purple.900',
  buttonHoverBorder: 'purple.600',
  
  // State colors
  error: 'red.200',
  errorBg: 'red.900',
  errorBorder: 'red.700',
  
  // CSS variables for TailwindCSS
  cssVariables: {
    '--background': '240 10% 3.9%',
    '--foreground': '0 0% 98%',
    '--card': '240 10% 3.9%',
    '--card-foreground': '0 0% 98%',
    '--popover': '240 10% 3.9%',
    '--popover-foreground': '0 0% 98%',
    '--primary': '262 80% 50%',
    '--primary-foreground': '0 0% 98%',
    '--secondary': '240 3.7% 15.9%',
    '--secondary-foreground': '0 0% 98%',
    '--muted': '240 3.7% 15.9%',
    '--muted-foreground': '240 5% 64.9%',
    '--accent': '262 80% 50%',
    '--accent-foreground': '0 0% 98%',
    '--destructive': '0 62.8% 30.6%',
    '--destructive-foreground': '0 0% 98%',
    '--border': '240 3.7% 15.9%',
    '--input': '240 3.7% 15.9%',
    '--ring': '262 80% 50%',
    '--radius': '0.5rem'
  }
};

// Chart colors for data visualization
export const chartColors = {
  light: {
    chart1: 'hsl(12, 76%, 61%)',
    chart2: 'hsl(173, 58%, 39%)',
    chart3: 'hsl(197, 37%, 24%)',
    chart4: 'hsl(43, 74%, 66%)',
    chart5: 'hsl(27, 87%, 67%)'
  },
  dark: {
    chart1: 'hsl(220, 70%, 50%)',
    chart2: 'hsl(160, 60%, 45%)',
    chart3: 'hsl(30, 80%, 55%)',
    chart4: 'hsl(280, 65%, 60%)',
    chart5: 'hsl(340, 75%, 55%)'
  }
};

// Semantic colors for specific UI components
export const semanticColors = {
  success: {
    light: 'green.500',
    dark: 'green.300'
  },
  warning: {
    light: 'orange.500',
    dark: 'orange.300'
  },
  info: {
    light: 'blue.500',
    dark: 'blue.300'
  }
}; 