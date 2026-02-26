import React, { useState, useEffect, useRef } from 'react';
import { 
  Box, 
  Text, 
  Button, 
  HStack,
  useColorModeValue,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td
} from '@chakra-ui/react';
import { RefreshCw, Square } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

/**
 * ResponseSection - Displays the AI response with streaming support
 * Features: Markdown rendering, streaming cursor, error handling, retry functionality
 */
const ResponseSection = ({ 
  message, 
  isStreaming = false, 
  onRetry = null, 
  onStop = null,
  hasProcessingSteps = false 
}) => {
  const [displayContent, setDisplayContent] = useState('');
  const [showCursor, setShowCursor] = useState(false);
  const contentRef = useRef(null);

  // Theme colors
  const textColor = useColorModeValue('gray.800', 'gray.200');
  const codeBg = useColorModeValue('gray.100', 'gray.700');
  const errorBg = useColorModeValue('red.50', 'red.900');
  const errorColor = useColorModeValue('red.800', 'red.200');
  const errorBorderColor = useColorModeValue('red.200', 'red.700');
  const blockquoteBg = useColorModeValue('gray.50', 'gray.700');

  // Update display content
  useEffect(() => {
    setDisplayContent(message.content || '');
  }, [message.content]);

  // Manage cursor blinking during streaming
  useEffect(() => {
    if (isStreaming && displayContent) {
      setShowCursor(true);
      const interval = setInterval(() => {
        setShowCursor(prev => !prev);
      }, 500);

      return () => clearInterval(interval);
    } else {
      setShowCursor(false);
    }
  }, [isStreaming, displayContent]);

  // Auto-scroll during streaming
  useEffect(() => {
    if (contentRef.current && isStreaming) {
      contentRef.current.scrollTop = contentRef.current.scrollHeight;
    }
  }, [displayContent, isStreaming]);

  // Clean message content - remove any leaked internal thoughts but preserve markdown structure
  const cleanMessageContent = () => {
    if (!displayContent) return '';
    
    let cleanedContent = displayContent;
    
    // Remove any internal thoughts tags that might have leaked through
    cleanedContent = cleanedContent.replace(/<internal_thoughts>[\s\S]*?<\/internal_thoughts>/g, '');
    cleanedContent = cleanedContent.replace(/<internal[^>]*thoughts[^>]*>/g, '');
    cleanedContent = cleanedContent.replace(/<\/internal[^>]*thoughts[^>]*>/g, '');
    cleanedContent = cleanedContent.replace(/internal_thoughts/g, '');
    
    // Fix markdown structure issues but preserve line breaks
    cleanedContent = fixMarkdownStructure(cleanedContent);
    
    // Preserve double line breaks (paragraph breaks) but clean up excessive spaces
    cleanedContent = cleanedContent.replace(/\n\n\n+/g, '\n\n'); // Max 2 consecutive newlines
    cleanedContent = cleanedContent.replace(/ {3,}/g, ' '); // Replace 3+ spaces with single space
    cleanedContent = cleanedContent.replace(/\t+/g, ' '); // Replace tabs with spaces
    
    // Remove multiple consecutive punctuation marks
    cleanedContent = cleanedContent.replace(/([.!?])\1{2,}/g, '$1');
    
    // Fix obvious character repetition
    cleanedContent = cleanedContent.replace(/(\w)\1{3,}/g, '$1');
    
    return cleanedContent.trim();
  };

  // Fix markdown structure to ensure proper rendering
  const fixMarkdownStructure = (content) => {
    if (!content) return '';
    
    let lines = content.split('\n');
    let fixedLines = [];
    
    for (let i = 0; i < lines.length; i++) {
      let line = lines[i];
      
      // Check if line starts with text that should be a header
      // Look for patterns like "Résumé Le Règlement..." or "Summary The regulation..."
      if (i === 0 && !line.startsWith('#') && line.length > 0) {
        // Check if it looks like a title/summary line
        const words = line.trim().split(' ');
        const firstWord = words[0];
        
        // Common title/summary words in multiple languages
        const titleWords = ['résumé', 'summary', 'analyse', 'analysis', 'introduction', 'overview', 'conclusion'];
        
        if (titleWords.some(word => firstWord.toLowerCase().includes(word.toLowerCase()))) {
          // Split the line at the first sentence or after the title word
          const titleMatch = line.match(/^([^.!?]*[.!?]?)\s*(.*)/);
          if (titleMatch) {
            const [, title, rest] = titleMatch;
            fixedLines.push(`## ${title.trim()}`);
            fixedLines.push('');
            if (rest.trim()) {
              fixedLines.push(rest.trim());
            }
          } else {
            fixedLines.push(`## ${line.trim()}`);
          }
        } else {
          // Check if the line contains multiple sentences that should be split
          const sentenceMatch = line.match(/^([^.!?]*[.!?])\s*##\s*(.*)/);
          if (sentenceMatch) {
            const [, firstPart, headerPart] = sentenceMatch;
            fixedLines.push(`## ${firstPart.trim()}`);
            fixedLines.push('');
            fixedLines.push(`## ${headerPart.trim()}`);
          } else {
            fixedLines.push(line);
          }
        }
      } else {
        // Fix spacing around headers
        if (line.startsWith('#')) {
          // Ensure proper spacing before headers (except first line)
          if (i > 0 && fixedLines.length > 0 && fixedLines[fixedLines.length - 1].trim() !== '') {
            fixedLines.push('');
          }
          fixedLines.push(line);
          // Ensure spacing after headers
          if (i < lines.length - 1 && lines[i + 1].trim() !== '' && !lines[i + 1].startsWith('#')) {
            fixedLines.push('');
          }
        } else {
          fixedLines.push(line);
        }
      }
    }
    
    return fixedLines.join('\n');
  };

  // Custom markdown components for better rendering
  const markdownComponents = {
    // Custom paragraph component to handle spacing
    p: ({ children }) => (
      <Text mb={3} lineHeight="1.7">
        {children}
      </Text>
    ),
    
    // Custom heading components
    h1: ({ children }) => (
      <Text as="h1" fontSize="2xl" fontWeight="bold" mb={4} mt={6} color={textColor}>
        {children}
      </Text>
    ),
    h2: ({ children }) => (
      <Text as="h2" fontSize="xl" fontWeight="semibold" mb={3} mt={5} color={textColor}>
        {children}
      </Text>
    ),
    h3: ({ children }) => (
      <Text as="h3" fontSize="lg" fontWeight="semibold" mb={3} mt={4} color={textColor}>
        {children}
      </Text>
    ),
    
    // Custom list components
    ul: ({ children }) => (
      <Box as="ul" pl={6} mb={3}>
        {children}
      </Box>
    ),
    ol: ({ children }) => (
      <Box as="ol" pl={6} mb={3}>
        {children}
      </Box>
    ),
    li: ({ children }) => (
      <Text as="li" mb={1} lineHeight="1.6">
        {children}
      </Text>
    ),
    
    // Custom code components
    code: ({ inline, children }) => (
      <Text
        as={inline ? 'code' : 'pre'}
        bg={codeBg}
        px={inline ? 2 : 4}
        py={inline ? 1 : 3}
        borderRadius="md"
        fontSize="sm"
        fontFamily="mono"
        display={inline ? 'inline' : 'block'}
        overflowX={inline ? 'visible' : 'auto'}
        mb={inline ? 0 : 3}
        whiteSpace={inline ? 'nowrap' : 'pre'}
      >
        {children}
      </Text>
    ),
    
    // Custom blockquote component
    blockquote: ({ children }) => (
      <Box
        borderLeft="4px solid"
        borderLeftColor="gray.300"
        pl={4}
        py={2}
        fontStyle="italic"
        mb={3}
        bg={blockquoteBg}
        borderRadius="md"
      >
        {children}
      </Box>
    ),
    
    // Custom strong/bold component
    strong: ({ children }) => (
      <Text as="strong" fontWeight="bold">
        {children}
      </Text>
    ),
    
    // Custom emphasis/italic component
    em: ({ children }) => (
      <Text as="em" fontStyle="italic">
        {children}
      </Text>
    ),
    
    // Custom break component
    br: () => <Box height="1em" />,
    
    // Custom table components
    table: ({ children }) => (
      <Box mb={4} overflowX="auto">
        <Table variant="simple" size="sm">
          {children}
        </Table>
      </Box>
    ),
    thead: ({ children }) => (
      <Thead>
        {children}
      </Thead>
    ),
    tbody: ({ children }) => (
      <Tbody>
        {children}
      </Tbody>
    ),
    tr: ({ children }) => (
      <Tr>
        {children}
      </Tr>
    ),
    th: ({ children }) => (
      <Th fontSize="xs" fontWeight="bold" color={textColor}>
        {children}
      </Th>
    ),
    td: ({ children }) => (
      <Td fontSize="sm" py={2}>
        {children}
      </Td>
    )
  };

  // Check for errors
  const hasError = message.metadata?.error;

  // Don't render if no content and not streaming
  if (!displayContent && !isStreaming && !hasError) {
    return null;
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: hasProcessingSteps ? 10 : 0 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: hasProcessingSteps ? 0.2 : 0 }}
    >
      <Box mb={4}>
        {/* Error state */}
        {hasError && (
          <Box
            bg={errorBg}
            borderWidth="1px"
            borderColor={errorBorderColor}
            borderRadius="lg"
            p={4}
            mb={4}
          >
            <HStack justify="space-between" align="flex-start">
              <Box flex={1}>
                <Text fontSize="sm" fontWeight="medium" color={errorColor} mb={1}>
                  Error occurred during processing
                </Text>
                <Text fontSize="xs" color={errorColor}>
                  {message.metadata.error.message}
                </Text>
                {message.metadata.error.error_code && (
                  <Text fontSize="xs" color={errorColor} mt={1} fontFamily="mono">
                    Code: {message.metadata.error.error_code}
                  </Text>
                )}
              </Box>
              {onRetry && (
                <Button
                  size="sm"
                  colorScheme="red"
                  variant="outline"
                  leftIcon={<RefreshCw size={14} />}
                  onClick={onRetry}
                >
                  Retry
                </Button>
              )}
            </HStack>
          </Box>
        )}

        {/* Response content */}
        {(displayContent || isStreaming) && (
          <Box
            ref={contentRef}
            color={textColor}
            fontSize="sm"
            lineHeight="1.6"
          >
            <ReactMarkdown 
              components={markdownComponents}
              remarkPlugins={[remarkGfm]}
            >
              {cleanMessageContent()}
            </ReactMarkdown>
            
            {/* Streaming cursor */}
            {isStreaming && showCursor && (
              <motion.span
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="inline-block w-0.5 h-5 bg-purple-500 ml-1"
              />
            )}
          </Box>
        )}

        {/* Streaming controls */}
        {isStreaming && onStop && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-3"
          >
            <HStack spacing={2}>
              <Button
                size="sm"
                colorScheme="red"
                variant="outline"
                leftIcon={<Square size={14} />}
                onClick={onStop}
              >
                Stop Generation
              </Button>
              <Text fontSize="xs" color="gray.500">
                Generating response...
              </Text>
            </HStack>
          </motion.div>
        )}
      </Box>
    </motion.div>
  );
};

export default ResponseSection; 