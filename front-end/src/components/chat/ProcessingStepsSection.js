import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Text, 
  Button, 
  Collapse, 
  HStack, 
  VStack,
  IconButton,
  useColorModeValue 
} from '@chakra-ui/react';
import { ChevronDown, ChevronUp, Square, Cog } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

/**
 * ProcessingStepsSection - Collapsible section showing AI processing steps
 * Features: Processing steps display, auto-collapse after completion
 */
const ProcessingStepsSection = ({ 
  message, 
  isStreaming = false, 
  onStop = null 
}) => {
  const [isExpanded, setIsExpanded] = useState(true);
  const [shouldAutoCollapse, setShouldAutoCollapse] = useState(false);

  // Theme colors with accent color - moved to top level to fix hooks rule
  const accentColor = '#4415b6';
  const stepsBg = useColorModeValue('purple.50', 'purple.900');
  const stepsBorderColor = useColorModeValue('purple.200', 'purple.700');
  const stepsTextColor = useColorModeValue('purple.900', 'purple.100');
  const stepsHoverBg = useColorModeValue('purple.100', 'purple.800');

  // Auto-collapse after completion with animation
  useEffect(() => {
    if (!isStreaming && shouldAutoCollapse) {
      const timer = setTimeout(() => {
        setIsExpanded(false);
      }, 2000); // Wait 2 seconds after completion before collapsing

      return () => clearTimeout(timer);
    }
  }, [isStreaming, shouldAutoCollapse]);

  // Set auto-collapse flag when streaming completes
  useEffect(() => {
    if (!isStreaming && message.metadata?.completed) {
      setShouldAutoCollapse(true);
    }
  }, [isStreaming, message.metadata?.completed]);

  // Keep expanded during streaming
  useEffect(() => {
    if (isStreaming) {
      setIsExpanded(true);
      setShouldAutoCollapse(false);
    }
  }, [isStreaming]);

  const hasProcessingSteps = message.metadata?.processingSteps && message.metadata.processingSteps.length > 0;
  const hasProcessingState = message.processingState;

  // Don't render if no processing steps or state
  if (!hasProcessingSteps && !hasProcessingState) {
    return null;
  }

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded);
    setShouldAutoCollapse(false); // Disable auto-collapse if user manually toggles
  };

  return (
    <Box mb={4}>
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <Box
          bg={stepsBg}
          borderWidth="1px"
          borderColor={stepsBorderColor}
          borderRadius="lg"
          overflow="hidden"
          boxShadow="sm"
        >
          {/* Header with toggle */}
          <HStack
            p={3}
            justify="space-between"
            align="center"
            borderBottomWidth={isExpanded ? "1px" : "0"}
            borderBottomColor={stepsBorderColor}
            cursor="pointer"
            onClick={toggleExpanded}
            _hover={{ bg: stepsHoverBg }}
            transition="background-color 0.2s"
          >
            <HStack spacing={2}>
              <Cog size={16} color={accentColor} />
              <Text
                fontSize="sm"
                fontWeight="medium"
                color={stepsTextColor}
              >
                Processing Steps
              </Text>
              {isStreaming && (
                <Box
                  w={2}
                  h={2}
                  bg={accentColor}
                  borderRadius="full"
                  animation="pulse 1.5s infinite"
                />
              )}
            </HStack>

            <HStack spacing={2}>
              {/* Expand/collapse button */}
              <IconButton
                size="xs"
                variant="ghost"
                icon={isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                aria-label={isExpanded ? "Collapse steps" : "Expand steps"}
                color={stepsTextColor}
              />
            </HStack>
          </HStack>

          {/* Collapsible content */}
          <Collapse in={isExpanded} animateOpacity>
            <Box p={3}>
              {/* Processing steps */}
              {hasProcessingSteps && (
                <VStack align="stretch" spacing={2} mb={hasProcessingState ? 3 : 0}>
                  {message.metadata.processingSteps.map((step, index) => (
                    <motion.div
                      key={step.step || index}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.3, delay: index * 0.1 }}
                    >
                      <HStack spacing={2} align="flex-start">
                        <Box
                          w={2}
                          h={2}
                          borderRadius="full"
                          bg={
                            step.status === 'completed' ? 'green.500' :
                            step.status === 'in_progress' ? accentColor :
                            step.status === 'failed' ? 'red.500' :
                            'gray.300'
                          }
                          mt={1}
                          flexShrink={0}
                          className={step.status === 'in_progress' ? 'animate-pulse' : ''}
                        />
                        <VStack align="stretch" spacing={1} flex={1}>
                          <Text fontSize="xs" color={stepsTextColor}>
                            {step.message || step.step}
                          </Text>
                          {step.details && (
                            <Text fontSize="xs" color={stepsTextColor} opacity={0.7}>
                              {step.details}
                            </Text>
                          )}
                        </VStack>
                      </HStack>
                    </motion.div>
                  ))}
                </VStack>
              )}

              {/* Current processing state */}
              {hasProcessingState && (
                <Box>
                  <Text fontSize="xs" color={stepsTextColor} fontStyle="italic">
                    {message.processingState}
                  </Text>
                </Box>
              )}
            </Box>
          </Collapse>
        </Box>
      </motion.div>
    </Box>
  );
};

export default ProcessingStepsSection; 