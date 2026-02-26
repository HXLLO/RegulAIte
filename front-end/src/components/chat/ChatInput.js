import React, { useState } from 'react';
import { 
  Box, 
  Flex,
  Textarea, 
  IconButton, 
  useColorModeValue
} from '@chakra-ui/react';
import { AttachmentIcon, ArrowRightIcon } from '@chakra-ui/icons';

/**
 * Chat input component for sending messages
 * @param {Object} props
 * @param {Function} props.onSendMessage - Function to call when sending a message
 * @param {boolean} props.disabled - Whether the input is disabled
 */
const ChatInput = ({ onSendMessage, disabled = false }) => {
  const [input, setInput] = useState('');
  
  // Theme colors
  const accentColor = '#4415b6';
  const accentHoverColor = '#3a1296';
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const bgColor = useColorModeValue('white', 'gray.700');
  const textColor = useColorModeValue('gray.700', 'gray.200');
  const placeholderColor = useColorModeValue('gray.400', 'gray.500');
  const iconColor = useColorModeValue('gray.400', 'gray.500');
  const disabledBgColor = useColorModeValue('gray.100', 'gray.600');
  const disabledTextColor = useColorModeValue('gray.400', 'gray.500');
  const inputShadow = "0 2px 6px rgba(68, 21, 182, 0.07)";
  const inputHoverShadow = "0 3px 8px rgba(68, 21, 182, 0.1)";

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSendMessage(input);
      setInput('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <Box as="form" onSubmit={handleSubmit} position="relative" w="full">
      <Flex 
        align="center" 
        gap={2} 
        rounded="lg" 
        border="1px" 
        borderColor={borderColor}
        bg={bgColor} 
        px={4} 
        py={3} 
        w="full"
        boxShadow={inputShadow}
        transition="all 0.2s ease"
        _hover={{
          boxShadow: inputHoverShadow,
          borderColor: useColorModeValue('gray.300', 'gray.500')
        }}
        _focusWithin={{
          borderColor: accentColor,
          boxShadow: `0 0 0 1px ${accentColor}`
        }}
      >
        <IconButton
          aria-label="Attach file"
          icon={<AttachmentIcon />}
          size="sm"
          variant="ghost"
          color={iconColor}
          _hover={{ color: accentColor }}
          borderRadius="full"
        />
        <Textarea
          placeholder="Ask a question about governance, risk, or compliance..."
          minH="8"
          resize="none"
          flex="1"
          border="0"
          p="0"
          _focus={{ outline: 'none' }}
          color={textColor}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={1}
          isDisabled={disabled}
          _placeholder={{ color: placeholderColor }}
          fontSize="md"
        />
        <IconButton
          type="submit"
          aria-label="Send message"
          icon={<ArrowRightIcon />}
          isDisabled={input.trim() === '' || disabled}
          borderRadius="full"
          size="md"
          bg={input.trim() === '' || disabled ? disabledBgColor : accentColor}
          color={input.trim() === '' || disabled ? disabledTextColor : 'white'}
          _hover={{
            bg: input.trim() === '' || disabled ? disabledBgColor : accentHoverColor,
            transform: input.trim() === '' || disabled ? 'none' : 'translateY(-1px)'
          }}
          transition="all 0.2s ease"
          boxShadow={input.trim() === '' || disabled ? 'none' : '0 2px 4px rgba(68, 21, 182, 0.3)'}
          _active={{
            transform: 'translateY(1px)',
            boxShadow: 'none'
          }}
        />
      </Flex>
    </Box>
  );
};

export default ChatInput; 