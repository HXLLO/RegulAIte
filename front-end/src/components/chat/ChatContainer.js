import React from 'react';
import { Box } from '@chakra-ui/react';
import MessageList from './MessageList';

/**
 * ChatContainer - Top-level container for the chat interface
 * Manages the overall layout and message flow
 */
const ChatContainer = ({ 
  messages = [], 
  isLoading = false,
  onRetry = null,
  onStop = null,
  className = ''
}) => {
  return (
    <Box 
      className={`chat-container ${className}`}
      h="full"
      display="flex"
      flexDirection="column"
      overflow="hidden"
    >
      <MessageList
        messages={messages}
        isLoading={isLoading}
        onRetry={onRetry}
        onStop={onStop}
      />
    </Box>
  );
};

export default ChatContainer; 