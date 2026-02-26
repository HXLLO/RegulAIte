import React from 'react';
import { Box, Text, useColorModeValue } from '@chakra-ui/react';
import { motion } from 'framer-motion';

/**
 * UserMessage - Renders user messages with proper styling
 * Features: Border, colored background, right-aligned, auto-sizing with max width
 */
const UserMessage = ({ message, index }) => {
  // Theme colors - moved to top level to fix hooks rule
  const userBg = useColorModeValue('blue.50', 'blue.900');
  const userBorderColor = useColorModeValue('blue.200', 'blue.700');
  const userTextColor = useColorModeValue('blue.900', 'blue.100');
  const timestampColor = useColorModeValue('blue.600', 'blue.300');

  return (
    <Box display="flex" justifyContent="flex-end" w="full">
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.3 }}
        style={{ maxWidth: '70%' }}
      >
        <Box
          bg={userBg}
          borderWidth="1px"
          borderColor={userBorderColor}
          borderRadius="lg"
          p={4}
          boxShadow="sm"
          position="relative"
          _before={{
            content: '""',
            position: 'absolute',
            top: '50%',
            right: '-8px',
            transform: 'translateY(-50%)',
            width: 0,
            height: 0,
            borderLeft: '8px solid',
            borderLeftColor: userBorderColor,
            borderTop: '8px solid transparent',
            borderBottom: '8px solid transparent',
          }}
          _after={{
            content: '""',
            position: 'absolute',
            top: '50%',
            right: '-7px',
            transform: 'translateY(-50%)',
            width: 0,
            height: 0,
            borderLeft: '7px solid',
            borderLeftColor: userBg,
            borderTop: '7px solid transparent',
            borderBottom: '7px solid transparent',
          }}
        >
          <Text
            color={userTextColor}
            fontSize="sm"
            lineHeight="1.6"
            whiteSpace="pre-wrap"
            wordBreak="break-word"
          >
            {message.content}
          </Text>
          
          {/* Timestamp */}
          {message.timestamp && (
            <Text
              fontSize="xs"
              color={timestampColor}
              mt={2}
              textAlign="right"
              opacity={0.7}
            >
              {new Date(message.timestamp).toLocaleTimeString([], { 
                hour: '2-digit', 
                minute: '2-digit' 
              })}
            </Text>
          )}
        </Box>
      </motion.div>
    </Box>
  );
};

export default UserMessage; 