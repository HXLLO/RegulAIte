import React from 'react';
import { IconButton, useColorMode, useColorModeValue } from '@chakra-ui/react';
import { FaMoon, FaSun } from 'react-icons/fa';
import { useTheme } from '../../contexts/ThemeContext';

const ThemeToggle = () => {
  const { colorMode, toggleColorMode } = useColorMode();
  const { theme, setTheme } = useTheme();
  const SwitchIcon = useColorModeValue(FaMoon, FaSun);
  
  // Handle theme toggle
  const handleToggle = () => {
    // Toggle Chakra color mode
    toggleColorMode();
    
    // Also update our custom theme
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
  };

  return (
    <IconButton
      aria-label={`Toggle ${colorMode === 'light' ? 'Dark' : 'Light'} Mode`}
      icon={<SwitchIcon />}
      variant="ghost"
      color="current"
      onClick={handleToggle}
      size="md"
    />
  );
};

export default ThemeToggle; 