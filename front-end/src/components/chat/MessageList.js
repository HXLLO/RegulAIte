import React, { useRef, useEffect } from 'react';
import { VStack, Box } from '@chakra-ui/react';
import { motion, AnimatePresence } from 'framer-motion';
import UserMessage from './UserMessage';
import LLMMessage from './LLMMessage';

/**
 * MessageList - Renders and manages the list of chat messages
 * Handles message type routing and scroll behavior
 */
const MessageList = ({ 
  messages = [], 
  isLoading = false,
  onRetry = null,
  onStop = null 
}) => {
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const renderMessage = (message, index) => {
    const isUser = message.role === 'user';
    const isStreaming = message.isGenerating || false;

    if (isUser) {
      return (
        <UserMessage
          key={message.id || index}
          message={message}
          index={index}
        />
      );
    } else {
      return (
        <LLMMessage
          key={message.id || index}
          message={message}
          index={index}
          isStreaming={isStreaming}
          onRetry={() => onRetry && onRetry(index)}
          onStop={isStreaming ? onStop : null}
        />
      );
    }
  };

  return (
    <VStack 
      spacing={4} 
      flex="1" 
      overflowY="auto" 
      p={6} 
      align="stretch"
      pb="120px"
    >
      <AnimatePresence>
        {messages.map((message, index) => (
          <motion.div
            key={message.id || index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            {renderMessage(message, index)}
          </motion.div>
        ))}
      </AnimatePresence>
      
      {/* Invisible element to scroll to */}
      <Box ref={messagesEndRef} />
    </VStack>
  );
};

export default MessageList; 