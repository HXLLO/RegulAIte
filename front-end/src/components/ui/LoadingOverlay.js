import React from 'react';
import {
  Box,
  Flex,
  Spinner,
  Text,
  VStack,
  useColorModeValue
} from '@chakra-ui/react';

/**
 * Loading overlay component to prevent interactions during critical operations
 */
const LoadingOverlay = ({
  isVisible = false,
  subMessage = null,
  zIndex = 1000
}) => {
  const bgColor = useColorModeValue('rgba(255, 255, 255, 0.9)', 'rgba(0, 0, 0, 0.9)');
  const textColor = useColorModeValue('gray.800', 'gray.200');
  const subTextColor = useColorModeValue('gray.600', 'gray.400');
  const accentColor = '#4415b6';

  if (!isVisible) return null;

  return (
    <Box
      position="fixed"
      top="0"
      left="0"
      right="0"
      bottom="0"
      bg={bgColor}
      backdropFilter="blur(2px)"
      zIndex={zIndex}
      display="flex"
      alignItems="center"
      justifyContent="center"
    >
      <VStack spacing={4} textAlign="center" p={8}>
        <Spinner
          size="xl"
          color={accentColor}
          thickness="3px"
          speed="0.8s"
        />
        
        {subMessage && (
          <Text
            fontSize="sm"
            color={subTextColor}
            maxW="400px"
          >
            {subMessage}
          </Text>
        )}
      </VStack>
    </Box>
  );
};

export default LoadingOverlay; 