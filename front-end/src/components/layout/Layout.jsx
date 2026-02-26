import React from 'react';
import { Navigate } from 'react-router-dom';
import { Box, Flex, Text, useColorModeValue } from '@chakra-ui/react';
import Navbar from './Navbar';
import { useTheme } from '../../contexts/ThemeContext';
import { useAuth } from '../../contexts/AuthContext';

const Layout = ({ children }) => {
  const { theme } = useTheme();
  const { isAuthenticated, loading } = useAuth();
  
  // Use CSS variables through Chakra's color mode
  const bg = useColorModeValue('var(--chakra-colors-white)', 'var(--chakra-colors-gray-800)');
  const textColor = useColorModeValue('var(--chakra-colors-gray-800)', 'var(--chakra-colors-whiteAlpha-900)');
  const borderColor = useColorModeValue('var(--chakra-colors-gray-200)', 'var(--chakra-colors-gray-700)');

  // Handle authentication check
  if (loading) {
    return (
      <Flex justify="center" align="center" minH="100vh" bg={bg}>
        <Text fontSize="lg">Loading...</Text>
      </Flex>
    );
  }
  
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }

  return (
    <Flex direction="column" minH="100vh" bg={bg} color={textColor}>
      <Navbar />
      <Box as="main" flex="1">
        {children}
      </Box>
    </Flex>
  );
};

export default Layout; 