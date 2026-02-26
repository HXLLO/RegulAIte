import React, { useState } from 'react';
import { 
  Box, 
  Text, 
  Button, 
  Collapse, 
  VStack, 
  HStack,
  Badge,
  Divider,
  useColorModeValue,
  Flex,
  Icon,
  Tooltip,
  Code,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon
} from '@chakra-ui/react';
import { FileText, ChevronDown, ChevronUp, ExternalLink, Info, Eye, Hash, Clock, Database, Target } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

/**
 * Enhanced SourcesSection - Displays detailed RAG sources with comprehensive information
 * Features: Document chunks, relevance scores, metadata, agent iteration tracking
 */
const SourcesSection = ({ 
  sources = [], 
  isStreaming = false 
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [showAllSources, setShowAllSources] = useState(false);
  const [expandedChunks, setExpandedChunks] = useState(new Set());

  // Theme colors
  const accentColor = '#4415b6';
  const sourcesBg = useColorModeValue('gray.50', 'gray.800');
  const sourcesBorderColor = useColorModeValue('gray.200', 'gray.600');
  const sourcesTextColor = useColorModeValue('gray.800', 'gray.200');
  const sourcesSecondaryColor = useColorModeValue('gray.600', 'gray.400');
  const sourceItemBg = useColorModeValue('white', 'gray.700');
  const sourceItemBorderColor = useColorModeValue('gray.100', 'gray.600');
  const sourcesHoverBg = useColorModeValue('gray.100', 'gray.700');
  const chunkTextBg = useColorModeValue('gray.50', 'gray.800');
  const metadataBg = useColorModeValue('blue.50', 'blue.900');
  const chunkBorderColor = useColorModeValue('gray.200', 'gray.600');

  // Don't render if no sources or still streaming
  if (!sources || sources.length === 0 || isStreaming) {
    return null;
  }

  const displayedSources = showAllSources ? sources : sources.slice(0, 3);
  const hasMoreSources = sources.length > 3;

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded);
  };

  const toggleShowAll = () => {
    setShowAllSources(!showAllSources);
  };

  const toggleChunkExpanded = (index) => {
    const newExpanded = new Set(expandedChunks);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedChunks(newExpanded);
  };

  // Calculate relevance color based on score
  const getRelevanceColor = (score) => {
    if (score >= 0.8) return 'green';
    if (score >= 0.6) return 'yellow';
    if (score >= 0.4) return 'orange';
    return 'red';
  };

  // Format relevance score
  const formatRelevance = (score) => {
    if (typeof score === 'number') {
      return `${Math.round(score * 100)}%`;
    }
    return 'N/A';
  };

  // Get document type icon
  const getDocumentIcon = (fileType) => {
    if (!fileType) return '📄';
    const type = fileType.toLowerCase();
    if (type.includes('pdf')) return '📕';
    if (type.includes('doc') || type.includes('word')) return '📘';
    if (type.includes('xls') || type.includes('excel')) return '📊';
    if (type.includes('ppt') || type.includes('powerpoint')) return '📑';
    if (type.includes('txt') || type.includes('text')) return '📝';
    return '📄';
  };

  // Format file size
  const formatFileSize = (size) => {
    if (!size || size === 0) return '';
    if (size < 1024) return `${size} B`;
    if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
    return `${(size / (1024 * 1024)).toFixed(1)} MB`;
  };

  // Get match method badge
  const getMatchMethod = (source) => {
    if (source.matched_via === 'question') return { label: 'Via Question', color: 'purple' };
    if (source.matched_via === 'chunk') return { label: 'Direct Match', color: 'blue' };
    if (source.is_question) return { label: 'Question', color: 'purple' };
    return { label: 'Semantic', color: 'green' };
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.4 }}
    >
      <Box
        bg={sourcesBg}
        borderWidth="1px"
        borderColor={sourcesBorderColor}
        borderRadius="lg"
        overflow="hidden"
        boxShadow="sm"
      >
        {/* Enhanced Header */}
        <HStack
          p={4}
          justify="space-between"
          align="center"
          cursor="pointer"
          onClick={toggleExpanded}
          _hover={{ bg: sourcesHoverBg }}
          transition="background-color 0.2s"
        >
          <HStack spacing={3}>
            <Icon as={Database} size={18} color={accentColor} />
            <Text
              fontSize="sm"
              fontWeight="semibold"
              color={sourcesTextColor}
            >
              Sources consultées par l'agent RAG
            </Text>
            <Badge
              colorScheme="purple"
              size="sm"
              borderRadius="full"
              variant="solid"
            >
              {sources.length} documents
            </Badge>
            {/* Show high relevance count */}
            {sources.filter(s => (s.relevance_score || s.match_percentage / 100 || 0) >= 0.7).length > 0 && (
              <Badge
                colorScheme="green"
                size="sm"
                borderRadius="full"
                variant="outline"
              >
                {sources.filter(s => (s.relevance_score || s.match_percentage / 100 || 0) >= 0.7).length} haute pertinence
              </Badge>
            )}
          </HStack>

          <HStack spacing={2}>
            <Text fontSize="xs" color={sourcesSecondaryColor}>
              {isExpanded ? 'Masquer' : 'Voir'} les détails
            </Text>
            {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </HStack>
        </HStack>

        {/* Enhanced Collapsible content */}
        <Collapse in={isExpanded} animateOpacity>
          <Box p={4} pt={0}>
            <VStack spacing={4} align="stretch">
              {displayedSources.map((source, index) => {
                const isChunkExpanded = expandedChunks.has(index);
                const matchMethod = getMatchMethod(source);
                const relevanceScore = source.relevance_score || source.match_percentage / 100 || 0;
                
                return (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: index * 0.1 }}
                  >
                    <Box
                      bg={sourceItemBg}
                      borderWidth="1px"
                      borderColor={sourceItemBorderColor}
                      borderRadius="lg"
                      overflow="hidden"
                      boxShadow="xs"
                    >
                      {/* Source header with detailed metadata */}
                      <Box p={4} borderBottom="1px" borderColor={sourceItemBorderColor}>
                        <Flex justify="space-between" align="flex-start" mb={3}>
                          <HStack spacing={2} flex={1}>
                            <VStack align="flex-start" spacing={1}>
                              <Text
                                fontSize="sm"
                                fontWeight="semibold"
                                color={sourcesTextColor}
                                noOfLines={1}
                              >
                                {source.filename || source.original_filename || source.title || `Document ${index + 1}`}
                              </Text>
                              <HStack spacing={2} flexWrap="wrap">
                                {/* Document ID */}
                                {source.doc_id && (
                                  <Tooltip label="Document ID">
                                    <HStack spacing={1}>
                                      <Icon as={Hash} size={10} color={sourcesSecondaryColor} />
                                      <Code fontSize="xs" color={sourcesSecondaryColor}>
                                        {source.doc_id.slice(0, 8)}...
                                      </Code>
                                    </HStack>
                                  </Tooltip>
                                )}
                                
                                {/* Chunk information */}
                                {(source.chunk_index !== undefined || source.chunk_id) && (
                                  <Tooltip label="Chunk Index">
                                    <Badge size="xs" colorScheme="gray" variant="outline">
                                      Chunk {source.chunk_index || source.chunk_id || 'N/A'}
                                    </Badge>
                                  </Tooltip>
                                )}
                                
                                {/* Match method */}
                                <Badge 
                                  size="xs" 
                                  colorScheme={matchMethod.color}
                                  variant="subtle"
                                >
                                  {matchMethod.label}
                                </Badge>
                                
                                {/* File size */}
                                {source.size && (
                                  <Text fontSize="xs" color={sourcesSecondaryColor}>
                                    {formatFileSize(source.size)}
                                  </Text>
                                )}
                              </HStack>
                            </VStack>
                          </HStack>

                          {/* Relevance score */}
                          <VStack align="flex-end" spacing={1}>
                            {relevanceScore > 0 && (
                              <Tooltip label="Score de pertinence basé sur la similarité sémantique">
                                <Badge
                                  colorScheme={getRelevanceColor(relevanceScore)}
                                  size="md"
                                  borderRadius="full"
                                  variant="solid"
                                  px={2}
                                >
                                  <HStack spacing={1}>
                                    <Icon as={Target} size={10} />
                                    <Text>
                                      {source.match_percentage !== undefined 
                                        ? `${source.match_percentage}%` 
                                        : formatRelevance(relevanceScore)
                                      }
                                    </Text>
                                  </HStack>
                                </Badge>
                              </Tooltip>
                            )}
                          </VStack>
                        </Flex>

                        {/* Additional metadata row */}
                        {(source.category || source.language || source.created_at) && (
                          <HStack spacing={3} mt={2} flexWrap="wrap">
                            {source.category && (
                              <Badge size="xs" colorScheme="blue" variant="outline">
                                {source.category}
                              </Badge>
                            )}
                            {source.created_at && (
                              <HStack spacing={1}>
                                <Icon as={Clock} size={10} color={sourcesSecondaryColor} />
                                <Text fontSize="xs" color={sourcesSecondaryColor}>
                                  {new Date(source.created_at).toLocaleDateString('fr-FR')}
                                </Text>
                              </HStack>
                            )}
                          </HStack>
                        )}
                      </Box>

                      {/* Chunk content section */}
                      {(source.chunk_text || source.content || source.text) && (
                        <Box>
                          <HStack
                            px={4}
                            py={2}
                            cursor="pointer"
                            onClick={() => toggleChunkExpanded(index)}
                            _hover={{ bg: sourcesHoverBg }}
                            transition="background-color 0.2s"
                            borderBottom={isChunkExpanded ? "1px" : "none"}
                            borderColor={chunkBorderColor}
                          >
                            <Icon as={Eye} size={14} color={accentColor} />
                            <Text fontSize="xs" fontWeight="medium" color={sourcesTextColor}>
                              Contenu du chunk ({(source.chunk_text || source.content || source.text || '').length} caractères)
                            </Text>
                            <Flex flex={1} />
                            {isChunkExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                          </HStack>
                          
                          <Collapse in={isChunkExpanded} animateOpacity>
                            <Box
                              bg={chunkTextBg}
                              borderRadius="none"
                              p={4}
                              borderTop="1px"
                              borderColor={chunkBorderColor}
                            >
                              <Text
                                fontSize="sm"
                                color={sourcesTextColor}
                                lineHeight="1.6"
                                fontFamily="system-ui"
                                whiteSpace="pre-wrap"
                              >
                                {source.chunk_text || source.content || source.text}
                              </Text>
                            </Box>
                          </Collapse>
                        </Box>
                      )}

                      {/* Technical metadata (collapsible) */}
                      {(source.node_id || source.document_id || source.metadata) && (
                        <Accordion allowToggle size="sm">
                          <AccordionItem border="none">
                            <AccordionButton
                              px={4}
                              py={2}
                              _hover={{ bg: sourcesHoverBg }}
                            >
                              <HStack flex={1} spacing={2}>
                                <Icon as={Info} size={12} color={sourcesSecondaryColor} />
                                <Text fontSize="xs" color={sourcesSecondaryColor}>
                                  Métadonnées techniques
                                </Text>
                              </HStack>
                              <AccordionIcon />
                            </AccordionButton>
                            <AccordionPanel pb={3} px={4}>
                              <Box bg={metadataBg} borderRadius="md" p={3}>
                                <VStack align="stretch" spacing={2} fontSize="xs">
                                  {source.node_id && (
                                    <HStack justify="space-between">
                                      <Text color={sourcesSecondaryColor}>Node ID:</Text>
                                      <Code fontSize="xs">{source.node_id}</Code>
                                    </HStack>
                                  )}
                                  {source.document_id && (
                                    <HStack justify="space-between">
                                      <Text color={sourcesSecondaryColor}>Document ID:</Text>
                                      <Code fontSize="xs">{source.document_id}</Code>
                                    </HStack>
                                  )}
                                  {source.text_content_type && (
                                    <HStack justify="space-between">
                                      <Text color={sourcesSecondaryColor}>Content Type:</Text>
                                      <Badge size="xs" colorScheme="gray">{source.text_content_type}</Badge>
                                    </HStack>
                                  )}
                                  {source.file_type && (
                                    <HStack justify="space-between">
                                      <Text color={sourcesSecondaryColor}>Type de fichier:</Text>
                                      <Badge size="xs" colorScheme="blue">{source.file_type}</Badge>
                                    </HStack>
                                  )}
                                </VStack>
                              </Box>
                            </AccordionPanel>
                          </AccordionItem>
                        </Accordion>
                      )}

                      {/* External link if available */}
                      {source.url && (
                        <Box px={4} pb={3}>
                          <Button
                            size="xs"
                            variant="ghost"
                            leftIcon={<ExternalLink size={12} />}
                            color={accentColor}
                            onClick={() => window.open(source.url, '_blank')}
                          >
                            Voir la source externe
                          </Button>
                        </Box>
                      )}
                    </Box>
                  </motion.div>
                );
              })}

              {/* Show more/less button */}
              {hasMoreSources && (
                <Box textAlign="center" pt={2}>
                  <Button
                    size="sm"
                    variant="ghost"
                    color={accentColor}
                    onClick={toggleShowAll}
                    fontSize="xs"
                  >
                    {showAllSources 
                      ? `Afficher moins` 
                      : `Afficher ${sources.length - 3} sources supplémentaires`
                    }
                  </Button>
                </Box>
              )}

              {/* Summary footer */}
              <Box
                bg={metadataBg}
                borderRadius="md"
                p={3}
                mt={2}
              >
                <Text fontSize="xs" color={sourcesSecondaryColor} textAlign="center">
                  <strong>{sources.length}</strong> documents analysés • 
                  <strong> {sources.filter(s => (s.relevance_score || s.match_percentage / 100 || 0) >= 0.7).length}</strong> très pertinents • 
                  <strong> {sources.filter(s => s.matched_via === 'question').length}</strong> trouvés via questions •
                  <strong> {sources.filter(s => s.matched_via === 'chunk').length}</strong> correspondances directes
                </Text>
              </Box>
            </VStack>
          </Box>
        </Collapse>
      </Box>
    </motion.div>
  );
};

export default SourcesSection; 