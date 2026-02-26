import React, { useState } from 'react';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  InputGroup,
  InputRightElement,
  Stack,
  Heading,
  Text,
  Link,
  Flex,
  Card,
  CardBody,
  CardHeader,
  CardFooter,
  useColorMode
} from '@chakra-ui/react';
import { ViewIcon, ViewOffIcon } from '@chakra-ui/icons';
import { useAuth } from '../../contexts/AuthContext';

const LoginForm = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  
  const { login } = useAuth();
  const navigate = useNavigate();
  const { colorMode } = useColorMode();
  
  // Chakra UI colors
  const cardBg = colorMode === 'light' ? 'white' : 'gray.700';
  const accentColor = '#4415b6';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    
    try {
      await login(email, password);
      navigate('/'); // Redirect to dashboard after successful login
    } catch (err) {
      setError(err.detail || 'Failed to login. Please check your credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card bg={cardBg} boxShadow="lg" w="100%" maxW="md" borderRadius="lg">
      <CardHeader pb={0}>
        <Heading size="lg">Login</Heading>
        <Text mt={1} color="gray.500">Enter your credentials to access your account</Text>
      </CardHeader>

      <CardBody>
        {error && (
          <Box mb={4} p={3} bg="red.50" color="red.600" borderRadius="md">
            {error}
          </Box>
        )}

        <form onSubmit={handleSubmit}>
          <Stack spacing={4}>
            <FormControl id="email" isRequired>
              <FormLabel>Email</FormLabel>
              <Input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
              />
            </FormControl>

            <FormControl id="password" isRequired>
              <Flex align="center" justify="space-between">
                <FormLabel m={0}>Password</FormLabel>
                <Link as={RouterLink} to="/forgot-password" fontSize="sm" color={accentColor}>
                  Forgot Password?
                </Link>
              </Flex>
              <InputGroup>
                <Input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                />
                <InputRightElement width="3rem">
                  <Button 
                    h="1.5rem" 
                    size="sm" 
                    onClick={() => setShowPassword(!showPassword)}
                    variant="ghost"
                  >
                    {showPassword ? <ViewOffIcon /> : <ViewIcon />}
                  </Button>
                </InputRightElement>
              </InputGroup>
            </FormControl>

            <Button
              mt={6}
              isLoading={isLoading}
              type="submit"
              colorScheme="purple"
              bg={accentColor}
              _hover={{ bg: '#3a1296' }}
              size="lg"
              w="full"
            >
              Login
            </Button>
          </Stack>
        </form>
      </CardBody>

      <CardFooter pt={0}>
        <Text align="center" w="full">
          Don't have an account?{' '}
          <Link as={RouterLink} to="/register" color={accentColor} fontWeight="semibold">
            Sign up
          </Link>
        </Text>
      </CardFooter>
    </Card>
  );
};

export default LoginForm; 