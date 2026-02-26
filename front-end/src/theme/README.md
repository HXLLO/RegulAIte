# RegulAIte Theme System

This directory contains the centralized theme system for RegulAIte, designed to provide consistent styling across the application.

## Directory Structure

- `colors.js` - All color definitions used throughout the application
- `themeConfig.js` - Theme configuration for Chakra UI and CSS variables
- `useThemeColors.js` - Custom hooks for accessing theme colors
- `index.js` - Central exports for all theme-related utilities

## Usage

### Importing the Theme

```jsx
// Import the theme
import { useThemeColors, useBrandColors, useChartColors } from '../theme';
```

### Using Theme Colors in Components

```jsx
const MyComponent = () => {
  // Get all theme colors
  const colors = useThemeColors();
  
  // Or just get brand/accent colors
  const brandColors = useBrandColors();
  
  // Or just get chart colors
  const chartColors = useChartColors();
  
  return (
    <Box bg={colors.background} color={colors.text}>
      <Heading color={colors.primary}>Title</Heading>
      <Text color={colors.textSecondary}>Secondary text</Text>
      <Button bg={brandColors.primary} color="white">Button</Button>
    </Box>
  );
};
```

### Theme Variables

The theme system provides a variety of color variables including:

#### Brand Colors
- `primary` - Main accent color (#4415b6)
- `primaryHover` - Hover state for primary color
- `primaryLight` - Light version of primary color
- `primaryLighter` - Very light version of primary color
- `primaryMedium` - Medium intensity version of primary color

#### UI Colors
- `background` - Main background color
- `backgroundAlt` - Alternative background color
- `text` - Main text color
- `textSecondary` - Secondary text color
- `textTertiary` - Tertiary text color
- `border` - Border color
- `card` - Card background color
- `headerBg` - Header background color

#### Interactive Elements
- `buttonHoverBg` - Button hover background
- `buttonHoverBorder` - Button hover border

#### State Colors
- `error` - Error text color
- `errorBg` - Error background color
- `errorBorder` - Error border color

## Customizing the Theme

To customize the theme, modify the color definitions in `colors.js`. All parts of the application that use the theme hooks will automatically update. 