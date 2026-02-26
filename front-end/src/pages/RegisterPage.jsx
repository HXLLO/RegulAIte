import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Center, Container, useColorModeValue } from '@chakra-ui/react';
import RegisterForm from '../components/auth/RegisterForm';
import { useAuth } from '../contexts/AuthContext';

const RegisterPage = () => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const bg = useColorModeValue('gray.50', 'gray.900');
  
  // Redirect if already logged in
  useEffect(() => {
    if (isAuthenticated()) {
      navigate('/');
    }
  }, [isAuthenticated, navigate]);

  return (
    <Box minH="100vh" bg={bg}>
      <Container maxW="lg" py={{ base: '12', md: '24' }} px={{ base: '0', sm: '8' }}>
        <Center>
          <RegisterForm />
        </Center>
      </Container>
    </Box>
  );
};

export default RegisterPage; 