import React from 'react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { 
  Box, 
  Flex, 
  HStack, 
  Text, 
  Button,
  Link
} from '@chakra-ui/react';
import { useAuth } from '../../contexts/AuthContext';
import ThemeToggle from '../ui/ThemeToggle';
import { useTheme } from '../../contexts/ThemeContext';
import { useThemeColors } from '../../theme';

const Navbar = () => {
  const { currentUser, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const { theme } = useTheme();
  const colors = useThemeColors();
  
  // Use theme colors from our centralized system
  const bg = colors.background;
  const borderColor = colors.border;
  const textColor = colors.text;
  const accentColor = colors.primary; // Using the primary brand color

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <Box as="nav" bg={bg} borderBottom="1px" borderColor={borderColor}>
      <Flex maxW="7xl" mx="auto" px={4} h={16} alignItems="center" justifyContent="space-between">
        <Flex>
          <Flex alignItems="center">
            <Link as={RouterLink} to="/" _hover={{ textDecoration: 'none' }}>
              <Text fontSize="xl" fontWeight="bold" color={accentColor}>
                RegulAIte
              </Text>
            </Link>
          </Flex>
          {isAuthenticated() && (
            <HStack spacing={4} ml={10}>
              <Link
                as={RouterLink}
                to="/dashboard"
                color={textColor}
                fontSize="sm"
                fontWeight="medium"
                _hover={{ color: accentColor }}
              >
                Dashboard
              </Link>
              <Link
                as={RouterLink}
                to="/chat"
                color={textColor}
                fontSize="sm"
                fontWeight="medium"
                _hover={{ color: accentColor }}
              >
                Chat
              </Link>
              <Link
                as={RouterLink}
                to="/documents"
                color={textColor}
                fontSize="sm"
                fontWeight="medium"
                _hover={{ color: accentColor }}
              >
                Documents
              </Link>
              <Link
                as={RouterLink}
                to="/organization"
                color={textColor}
                fontSize="sm"
                fontWeight="medium"
                _hover={{ color: accentColor }}
              >
                Organization
              </Link>
            </HStack>
          )}
        </Flex>
        <Flex alignItems="center" gap={4}>
          <ThemeToggle />
          {isAuthenticated() ? (
            <Flex alignItems="center" gap={4}>
              <Text fontSize="sm" color={textColor} opacity={0.7}>
                {currentUser?.full_name || 'User'}
              </Text>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={handleLogout}
              >
                Sign Out
              </Button>
            </Flex>
          ) : (
            <Flex alignItems="center" gap={4}>
              <Button 
                as={RouterLink} 
                to="/login" 
                variant="ghost" 
                size="sm"
              >
                Log in
              </Button>
              <Button 
                as={RouterLink} 
                to="/register" 
                size="sm" 
                bg={accentColor}
                color="white"
                _hover={{ bg: '#3a1296' }}
              >
                Sign up
              </Button>
            </Flex>
          )}
        </Flex>
      </Flex>
    </Box>
  );
};

export default Navbar; 