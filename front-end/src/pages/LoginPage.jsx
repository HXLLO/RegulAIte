import React, { useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Box, Container, Center, Alert, AlertIcon, useColorModeValue } from '@chakra-ui/react';
import LoginForm from '../components/auth/LoginForm';
import { useAuth } from '../contexts/AuthContext';

const LoginPage = () => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const bg = useColorModeValue('gray.50', 'gray.900');
  
  // Check for 'registered=true' query param to show success message
  const registrationSuccess = new URLSearchParams(location.search).get('registered') === 'true';
  
  // Redirect if already logged in
  useEffect(() => {
    if (isAuthenticated()) {
      navigate('/');
    }
  }, [isAuthenticated, navigate]);

  return (
    <Box minH="100vh" bg={bg}>
      {registrationSuccess && (
        <Alert status="success" position="fixed" top="4" left="0" right="0" width="auto" maxW="md" mx="auto" zIndex="50">
          <AlertIcon />
          Registration successful! Please log in with your credentials.
        </Alert>
      )}
      <Container maxW="lg" py={{ base: '12', md: '24' }} px={{ base: '0', sm: '8' }}>
        <Center>
          <LoginForm />
        </Center>
      </Container>
    </Box>
  );
};

export default LoginPage; 