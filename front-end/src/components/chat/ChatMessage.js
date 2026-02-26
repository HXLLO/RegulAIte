import React, { useState, useEffect } from 'react';
import { User, Bot, FileText, ChevronDown, ChevronUp } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Box, Flex, Text, Badge, Spinner, useColorModeValue, Icon, Button, Collapse, VStack, Table, Thead, Tbody, Tr, Th, Td } from '@chakra-ui/react';
import ProcessingStatus from './ProcessingStatus';

/**
 * Renders a single chat message with clean, professional styling
 */
const ChatMessage = ({ message, isLoading = false, agentInfo = null, previousMessage = null }) => {
  const [showSources, setShowSources] = useState(false);
  const [showAllSources, setShowAllSources] = useState(false);
  
  const isUser = message.role === 'user';
  
  // Check if message has sources
  const hasSources = !isUser && message.metadata && message.metadata.sources && message.metadata.sources.length > 0;
  const hasInternalThoughts = !isUser && message.metadata && message.metadata.internal_thoughts;
  const isProcessing = isLoading && !isUser && message.processingState;
  
  // Theme colors - simplified and cleaner
  const accentColor = '#4415b6';
  const userBg = useColorModeValue('blue.50', 'blue.900');
  const assistantBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const textColor = useColorModeValue('gray.800', 'gray.100');
  const mutedTextColor = useColorModeValue('gray.600', 'gray.400');
  const iconBg = useColorModeValue('gray.100', 'gray.700');
  const codeBg = useColorModeValue('gray.100', 'gray.700');
  const sourceBg = useColorModeValue('gray.50', 'gray.700');
  
  // Clean message content - remove any leaked internal thoughts but preserve markdown structure
  const cleanMessageContent = () => {
    if (!message.content) return '';
    
    let cleanedContent = message.content;
    
    // Remove any internal thoughts tags that might have leaked through
    cleanedContent = cleanedContent.replace(/<internal_thoughts>[\s\S]*?<\/internal_thoughts>/g, '');
    cleanedContent = cleanedContent.replace(/<internal[^>]*thoughts[^>]*>/g, '');
    cleanedContent = cleanedContent.replace(/<\/internal[^>]*thoughts[^>]*>/g, '');
    cleanedContent = cleanedContent.replace(/internal_thoughts/g, '');
    
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
        bg={sourceBg}
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

  return (
    <Box 
      display="flex"
      width="full"
      alignItems="flex-start"
      gap={3}
      p={4}
      mb={4}
      bg={isUser ? userBg : assistantBg}
      borderWidth={1}
      borderColor={borderColor}
      borderRadius="lg"
      boxShadow="sm"
    >
      {/* Avatar */}
      <Flex
        h="32px"
        w="32px"
        alignItems="center"
        justifyContent="center"
        rounded="full"
        bg={iconBg}
        color={isUser ? 'blue.600' : accentColor}
        flexShrink={0}
      >
        <Icon as={isUser ? User : Bot} boxSize={4} />
      </Flex>
      
      <Box flex="1" minW={0}>
        {/* Header */}
        <Flex alignItems="center" gap={2} mb={2} className={isUser ? '' : 'assistant-message'}>
          <Text fontSize="sm" fontWeight="medium" color={isUser ? 'blue.600' : accentColor}>
            {isUser ? 'You' : 'RegulAIte'}
          </Text>
          
          {!isUser && agentInfo && agentInfo.agent_used && (
            <Badge 
              bg={accentColor} 
              color="white" 
              size="sm"
              borderRadius="full"
            >
              AI Agent
            </Badge>
          )}
          
          {/* Processing Status - Simplified */}
          {isProcessing && (
            <ProcessingStatus
              processingState={message.processingState}
              isProcessing={isProcessing}
              startTime={message.metadata?.startTime}
            />
          )}
        </Flex>
        
        {/* Message Content */}
        <Box 
          color={textColor}
          fontSize="sm"
          lineHeight="1.6"
          sx={{
            '& p': { mb: 2 },
            '& p:last-child': { mb: 0 },
            '& ul, & ol': { pl: 4, mb: 2 },
            '& li': { mb: 1 },
            '& h1, & h2, & h3': { fontWeight: 'semibold', mb: 2, mt: 3 },
            '& h1:first-child, & h2:first-child, & h3:first-child': { mt: 0 },
            '& code': { 
              bg: codeBg, 
              px: 1, 
              py: 0.5, 
              borderRadius: 'sm',
              fontSize: 'xs'
            },
            '& pre': { 
              bg: codeBg, 
              p: 3, 
              borderRadius: 'md',
              overflow: 'auto',
              fontSize: 'xs'
            }
          }}
        >
          <ReactMarkdown 
            components={markdownComponents}
            remarkPlugins={[remarkGfm]}
          >
            {cleanMessageContent()}
          </ReactMarkdown>
        </Box>
        
        
        {/* Sources - Simplified */}
        {hasSources && (
          <Box mt={3} pt={3} borderTop="1px solid" borderColor={borderColor}>
            <Button
              size="sm"
              variant="ghost"
              leftIcon={<Icon as={FileText} />}
              rightIcon={<Icon as={showSources ? ChevronUp : ChevronDown} />}
              onClick={() => setShowSources(!showSources)}
              color={accentColor}
              fontSize="xs"
            >
              {message.metadata.sources.length} source{message.metadata.sources.length !== 1 ? 's' : ''}
            </Button>
            
            <Collapse in={showSources}>
              <VStack align="stretch" spacing={2} mt={2}>
                {(showAllSources ? message.metadata.sources : message.metadata.sources.slice(0, 3)).map((source, idx) => (
                  <Box 
                    key={idx}
                    p={2}
                    bg={sourceBg}
                    borderRadius="md"
                    fontSize="xs"
                  >
                    <Text fontWeight="medium" mb={1} color={textColor}>
                      {source.title || 'Document'}
                    </Text>
                    {source.content && (
                      <Text 
                        color={mutedTextColor} 
                        noOfLines={2}
                        fontSize="xs"
                      >
                        {source.content}
                      </Text>
                    )}
                  </Box>
                ))}
                {message.metadata.sources.length > 3 && !showAllSources && (
                  <Button
                    size="xs"
                    variant="ghost"
                    color={accentColor}
                    fontSize="xs"
                    onClick={() => setShowAllSources(true)}
                    _hover={{ bg: 'transparent', textDecoration: 'underline' }}
                  >
                    +{message.metadata.sources.length - 3} more sources
                  </Button>
                )}
                {showAllSources && message.metadata.sources.length > 3 && (
                  <Button
                    size="xs"
                    variant="ghost"
                    color={accentColor}
                    fontSize="xs"
                    onClick={() => setShowAllSources(false)}
                    _hover={{ bg: 'transparent', textDecoration: 'underline' }}
                  >
                    Show fewer sources
                  </Button>
                )}
              </VStack>
            </Collapse>
          </Box>
        )}
      </Box>
    </Box>
  );
};

export default ChatMessage; 