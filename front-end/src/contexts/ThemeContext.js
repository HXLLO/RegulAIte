"use client"

import { createContext, useContext, useEffect, useState } from 'react';
import { applyThemeVariables } from '../theme';

const ThemeContext = createContext();

export function ThemeProvider({ children, defaultTheme = 'system', enableSystem = true }) {
  const [theme, setTheme] = useState(defaultTheme);
  
  // Update theme when component mounts
  useEffect(() => {
    // On mount, read the theme from localStorage or use system default
    const savedTheme = localStorage.getItem('theme') || defaultTheme;
    setTheme(savedTheme);
    applyTheme(savedTheme);

    // Listen for system preference changes
    if (enableSystem) {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      const handleChange = () => {
        if (theme === 'system') {
          applyTheme('system');
        }
      };
      
      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
    }
  }, [enableSystem, defaultTheme, theme]);

  // Apply theme to document
  const applyTheme = (newTheme) => {
    const root = document.documentElement;
    const isDark = 
      newTheme === 'dark' || 
      (newTheme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches);
    
    // Remove previous theme classes
    root.classList.remove('light', 'dark');
    
    // Add new theme class
    root.classList.add(isDark ? 'dark' : 'light');
    
    // Apply CSS variables for the theme
    applyThemeVariables(isDark);
    
    // Store the theme preference
    if (newTheme !== 'system') {
      localStorage.setItem('theme', newTheme);
    }
  };

  const setThemeValue = (newTheme) => {
    setTheme(newTheme);
    applyTheme(newTheme);
  };

  return (
    <ThemeContext.Provider value={{ theme, setTheme: setThemeValue }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
} 