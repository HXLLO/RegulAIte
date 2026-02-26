import React from 'react';
import {
  Box,
  Flex,
  Text,
  Avatar,
  Stack,
  Badge,
  useColorModeValue
} from '@chakra-ui/react';
import { useAuth } from '../../contexts/AuthContext';

const UserProfile = () => {
  const { currentUser } = useAuth();
  const accentColor = '#4415b6';
  const emptyStateBg = useColorModeValue('gray.100', 'gray.700');
  
  if (!currentUser) {
    return (
      <Box p={4} borderRadius="md" bg={emptyStateBg}>
        <Text>No user information available</Text>
      </Box>
    );
  }

  // Extract user info with fallbacks
  const userName = currentUser.full_name || currentUser.name || currentUser.email || 'User';
  const userEmail = currentUser.email || 'No email provided';
  const userRole = currentUser.role || 'User';
  const userCompany = currentUser.company || 'Not specified';
  
  // Generate initials for avatar
  const initials = userName.split(' ')
    .map(name => name[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();

  return (
    <Stack spacing={4}>
      <Flex align="center">
        <Avatar 
          name={userName} 
          size="lg" 
          bg={accentColor} 
          color="white"
          mr={4}
        >
          {initials}
        </Avatar>
        <Box>
          <Text fontWeight="bold" fontSize="lg">{userName}</Text>
          <Text color="gray.500" fontSize="sm">{userEmail}</Text>
          <Badge colorScheme="purple" fontSize="xs" mt={1}>{userRole}</Badge>
        </Box>
      </Flex>
      
      <Box>
        <Text fontSize="sm" fontWeight="bold" mb={1}>Company</Text>
        <Text fontSize="sm">{userCompany}</Text>
      </Box>
    </Stack>
  );
};

export default UserProfile; 