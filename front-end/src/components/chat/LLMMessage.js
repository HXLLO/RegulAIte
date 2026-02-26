import React from 'react';
import { Box, useColorModeValue } from '@chakra-ui/react';
import { motion } from 'framer-motion';
import ProcessingStepsSection from './ProcessingStepsSection';
import ResponseSection from './ResponseSection';
import SourcesSection from './SourcesSection';

/**
 * LLMMessage - Main container for AI assistant messages
 * Features: No background, no border, left-aligned, contains processing steps, response, and sources
 */
const LLMMessage = ({ 
  message, 
  index, 
  isStreaming = false, 
  onRetry = null, 
  onStop = null 
}) => {
  const textColor = useColorModeValue('gray.800', 'gray.200');

  // Check if we have processing steps or state
  const hasProcessingSteps = message.metadata?.processingSteps || message.processingState;

  // Check if we have sources
  const hasSources = message.metadata?.sources && message.metadata.sources.length > 0;

  return (
    <Box display="flex" justifyContent="flex-start" w="full">
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.3 }}
        style={{ maxWidth: '85%', width: '100%' }}
      >
        <Box
          color={textColor}
          // No background, no border as per requirements
        >
          {/* Processing Steps Section */}
          {hasProcessingSteps && (
            <ProcessingStepsSection
              message={message}
              isStreaming={isStreaming}
              onStop={onStop}
            />
          )}

          {/* Response Section */}
          <ResponseSection
            message={message}
            isStreaming={isStreaming}
            onRetry={onRetry}
            onStop={onStop}
            hasProcessingSteps={hasProcessingSteps}
          />

          {/* Sources Section */}
          {hasSources && (
            <Box mt={4}>
              <SourcesSection
                sources={message.metadata.sources}
                isStreaming={isStreaming}
              />
            </Box>
          )}
        </Box>
      </motion.div>
    </Box>
  );
};

export default LLMMessage; 