import React, { useState } from 'react';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  FormErrorMessage,
  FormHelperText,
  Input,
  InputGroup,
  InputRightElement,
  Stack,
  Heading,
  Text,
  Link,
  Card,
  CardBody,
  CardHeader,
  CardFooter,
  useColorModeValue
} from '@chakra-ui/react';
import { ViewIcon, ViewOffIcon } from '@chakra-ui/icons';
import { useAuth } from '../../contexts/AuthContext';

const RegisterForm = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    full_name: '',
    company: ''
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  
  const { register } = useAuth();
  const navigate = useNavigate();
  
  // Chakra UI colors
  const cardBg = useColorModeValue('white', 'gray.700');
  const accentColor = '#4415b6';

  const validatePassword = (password) => {
    const hasMinLength = password.length >= 8;
    const hasUppercase = /[A-Z]/.test(password);
    const hasSpecialChar = /[!@#$%^&*()_+{}\[\]:;<>,.?~\\/-]/.test(password);
    
    return {
      isValid: hasMinLength && hasUppercase && hasSpecialChar,
      messages: [
        !hasMinLength && 'Password must be at least 8 characters long',
        !hasUppercase && 'Password must contain at least one uppercase letter',
        !hasSpecialChar && 'Password must contain at least one special character'
      ].filter(Boolean)
    };
  };

  const handleChange = (e) => {
    const { id, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [id]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    // Validate form
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    
    const passwordValidation = validatePassword(formData.password);
    if (!passwordValidation.isValid) {
      setError(passwordValidation.messages.join('. '));
      return;
    }
    
    setIsLoading(true);
    
    try {
      // Create user object without confirmPassword
      const userData = {
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name,
        company: formData.company || undefined // Only include if not empty
      };
      
      console.log('Attempting to register with userData:', { ...userData, password: '[REDACTED]' });
      await register(userData);
      console.log('Registration successful, navigating to login page');
      navigate('/login?registered=true'); // Redirect to login with success param
    } catch (err) {
      console.error('Registration error:', err);
      
      // Make sure we extract a string error message
      let errorMessage = 'Registration failed. Please try again.';
      
      if (typeof err === 'string') {
        errorMessage = err;
      } else if (err && typeof err === 'object') {
        // Handle direct detail string
        if (typeof err.detail === 'string') {
          errorMessage = err.detail;
        }
        // Handle Pydantic validation errors (array format)
        else if (Array.isArray(err.detail)) {
          const validationErrors = err.detail.map(error => {
            if (error.msg) {
              return error.msg;
            } else if (error.message) {
              return error.message;
            }
            return 'Invalid field';
          });
          errorMessage = validationErrors.join('. ');
        }
        // Handle other object formats
        else if (err.message) {
          errorMessage = err.message;
        }
        // Handle Axios response structure
        else if (err.response && err.response.data) {
          const responseData = err.response.data;
          if (typeof responseData === 'string') {
            errorMessage = responseData;
          } else if (typeof responseData.detail === 'string') {
            errorMessage = responseData.detail;
          } else if (Array.isArray(responseData.detail)) {
            const validationErrors = responseData.detail.map(error => error.msg || error.message || 'Invalid field');
            errorMessage = validationErrors.join('. ');
          } else if (responseData.message) {
            errorMessage = responseData.message;
          }
        }
      }
      
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card bg={cardBg} boxShadow="lg" w="100%" maxW="md" borderRadius="lg">
      <CardHeader pb={0}>
        <Heading size="lg">Create an Account</Heading>
        <Text mt={1} color="gray.500">Enter your information to create your account</Text>
      </CardHeader>

      <CardBody>
        {error && (
          <Box mb={4} p={3} bg="red.50" color="red.600" borderRadius="md">
            {error}
          </Box>
        )}

        <form onSubmit={handleSubmit}>
          <Stack spacing={4}>
            <FormControl id="full_name" isRequired>
              <FormLabel>Full Name</FormLabel>
              <Input
                type="text"
                value={formData.full_name}
                onChange={handleChange}
                placeholder="John Doe"
              />
            </FormControl>

            <FormControl id="email" isRequired>
              <FormLabel>Email</FormLabel>
              <Input
                type="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="you@example.com"
              />
            </FormControl>

            <FormControl id="company">
              <FormLabel>Company (Optional)</FormLabel>
              <Input
                type="text"
                value={formData.company}
                onChange={handleChange}
                placeholder="Your company name"
              />
            </FormControl>

            <FormControl id="password" isRequired>
              <FormLabel>Password</FormLabel>
              <InputGroup>
                <Input
                  type={showPassword ? 'text' : 'password'}
                  value={formData.password}
                  onChange={handleChange}
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
              <FormHelperText>
                Password must be at least 8 characters long, contain at least one uppercase letter and one special character
              </FormHelperText>
            </FormControl>

            <FormControl id="confirmPassword" isRequired>
              <FormLabel>Confirm Password</FormLabel>
              <InputGroup>
                <Input
                  type={showPassword ? 'text' : 'password'}
                  value={formData.confirmPassword}
                  onChange={handleChange}
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
              Create Account
            </Button>
          </Stack>
        </form>
      </CardBody>

      <CardFooter pt={0}>
        <Text align="center" w="full">
          Already have an account?{' '}
          <Link as={RouterLink} to="/login" color={accentColor} fontWeight="semibold">
            Sign in
          </Link>
        </Text>
      </CardFooter>
    </Card>
  );
};

export default RegisterForm; 