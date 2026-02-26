import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Flex, 
  Text, 
  Spinner, 
  Progress,
  useColorModeValue
} from '@chakra-ui/react';

/**
 * Simple, clean processing status component
 */
const ProcessingStatus = ({ 
  processingState, 
  isProcessing = true,
  startTime = null
}) => {
  const [processingTime, setProcessingTime] = useState(0);

  // Track processing time
  useEffect(() => {
    let interval = null;
    if (isProcessing && startTime) {
      interval = setInterval(() => {
        setProcessingTime(Math.floor((Date.now() - startTime) / 1000));
      }, 1000);
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isProcessing, startTime]);

  // Theme colors
  const bgColor = useColorModeValue('blue.50', 'blue.900');
  const textColor = useColorModeValue('blue.700', 'blue.200');
  const accentColor = '#4415b6';

  if (!isProcessing) return null;

  const formatTime = (seconds) => {
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  const getStatusText = () => {
    if (processingState?.current_step) {
      return processingState.current_step.replace(/_/g, ' ');
    }
    return 'Processing your request...';
  };

  return (
    <Box 
      mt={3}
      p={3}
      bg={bgColor}
      borderRadius="md"
      borderLeft="3px solid"
      borderLeftColor={accentColor}
    >
      <Flex alignItems="center" gap={2} mb={2}>
        <Spinner size="sm" color={accentColor} />
        <Text fontSize="sm" fontWeight="medium" color={textColor}>
          {getStatusText()}
        </Text>
      </Flex>
      
      {processingTime > 0 && (
        <Text fontSize="xs" color={textColor} opacity={0.8}>
          Processing time: {formatTime(processingTime)}
        </Text>
      )}
      
      {processingState?.progress !== undefined && (
        <Progress 
          value={processingState.progress * 100} 
          size="sm" 
          colorScheme="blue"
          mt={2}
          borderRadius="full"
        />
      )}
    </Box>
  );
};

export default ProcessingStatus; 