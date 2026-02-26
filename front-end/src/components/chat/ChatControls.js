import React from 'react';
import { Box, HStack, Text, VStack, useColorModeValue } from '@chakra-ui/react';
import ChatInput from './ChatInput';

/**
 * Chat controls component with input
 */
const ChatControls = ({ 
  onSendMessage, 
  disabled = false,
  reasoningNodeId = null
}) => {
  // Theme colors
  const accentColor = '#4415b6'; 
  const accentLight = '#4415b615';
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const textColor = useColorModeValue('purple.700', 'purple.200');
  const bgColor = useColorModeValue('purple.50', 'purple.900');
  const bgBase = useColorModeValue('white', 'gray.800');
  
  // Shows the tree reasoning node info if it's active
  const showReasoningInfo = reasoningNodeId;

  return (
    <Box position="relative" bg={bgBase}>
      <Box borderTop="1px solid" borderTopColor={borderColor} bg={bgBase} p={3}>
        <VStack spacing={3} maxW="100%" mx="auto">
          <Box w="100%">
            <ChatInput onSendMessage={onSendMessage} disabled={disabled} />
          </Box>
          
          {/* Tree reasoning info */}
          {showReasoningInfo && (
            <HStack 
              w="100%" 
              px={3} 
              py={2} 
              bg={bgColor} 
              borderRadius="md" 
              fontSize="xs" 
              color={textColor}
              borderWidth="1px"
              borderColor="purple.200"
            >
              <Text fontWeight="medium">Current Reasoning:</Text>
              <Text>{reasoningNodeId}</Text>
            </HStack>
          )}
        </VStack>
      </Box>
    </Box>
  );
};

export default ChatControls; 