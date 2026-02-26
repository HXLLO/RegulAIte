/**
 * Theme Configuration
 * Combines color definitions with theme configuration for Chakra UI
 */

import { extendTheme } from '@chakra-ui/react';
import { brandColors, lightThemeColors, darkThemeColors } from './colors';

/**
 * CSS variables that need to be applied to :root
 * Used for Tailwind and other global styling
 */
export const cssVariables = {
  light: lightThemeColors.cssVariables,
  dark: darkThemeColors.cssVariables
};

/**
 * Create a Chakra UI compatible theme object
 */
export const createChakraTheme = () => {
  return extendTheme({
    config: {
      initialColorMode: 'light',
      useSystemColorMode: true,
    },
    colors: {
      brand: {
        50: '#f0ebfa',
        100: '#d2c5f0',
        200: '#b49fe6',
        300: '#9679db',
        400: '#7853d1',
        500: '#6339c8',
        600: '#5632b3',  // Matches accent color
        700: '#4415b6',  // Primary brand color
        800: '#35108f',  // Hover color
        900: '#290c70',
      },
      // Extend default Chakra UI colors with our semantic colors
      // Making them accessible via the Chakra UI API
    },
    styles: {
      global: (props) => ({
        body: {
          bg: props.colorMode === 'dark' ? darkThemeColors.background : lightThemeColors.background,
          color: props.colorMode === 'dark' ? darkThemeColors.text : lightThemeColors.text,
        },
      }),
    },
    components: {
      Button: {
        variants: {
          primary: (props) => ({
            bg: brandColors.primary,
            color: 'white',
            _hover: {
              bg: props.colorMode === 'dark' ? 'brand.600' : 'brand.800',
              _disabled: {
                bg: props.colorMode === 'dark' ? 'brand.700' : 'brand.700',
              },
            },
            _active: {
              bg: props.colorMode === 'dark' ? 'brand.800' : 'brand.900',
            },
          }),
          outline: (props) => ({
            borderColor: props.colorMode === 'dark' ? 'brand.600' : 'brand.700',
            color: props.colorMode === 'dark' ? 'brand.500' : 'brand.700',
            _hover: {
              bg: props.colorMode === 'dark' ? 'rgba(99, 57, 200, 0.1)' : 'rgba(68, 21, 182, 0.05)',
            },
          }),
        },
      },
      // Additional component styling can be added here
    },
  });
};

// Default Chakra theme with our customizations
export const chakraTheme = createChakraTheme(); 