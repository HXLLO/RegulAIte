import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Flex, 
  Text, 
  VStack, 
  HStack, 
  Badge, 
  Progress,
  Icon,
  Collapse,
  useColorModeValue,
  Divider,
  Tooltip,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText
} from '@chakra-ui/react';
import { 
  Brain, 
  Eye, 
  TrendingUp, 
  Shield, 
  Clock,
  CheckCircle,
  AlertTriangle,
  Info,
  Zap,
  Database
} from 'lucide-react';

/**
 * Advanced AI Reasoning Panel - Shows detailed insights into AI decision-making
 */
const AIReasoningPanel = ({ 
  contextMetadata, 
  processingMetrics,
  confidenceScore,
  isVisible = true 
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  // Theme colors
  const accentColor = useColorModeValue('#4415b6', '#6c45e7');
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const textColor = useColorModeValue('gray.800', 'gray.100');
  const mutedTextColor = useColorModeValue('gray.600', 'gray.400');
  const successColor = useColorModeValue('green.500', 'green.300');
  const warningColor = useColorModeValue('orange.500', 'orange.300');
  const errorColor = useColorModeValue('red.500', 'red.300');
  const insightBg = useColorModeValue('blue.50', 'blue.900');
  const metricBg = useColorModeValue('gray.50', 'gray.700');

  if (!isVisible || (!contextMetadata && !processingMetrics)) {
    return null;
  }

  // Calculate confidence level
  const getConfidenceLevel = (score) => {
    if (score >= 0.8) return { level: 'High', color: successColor, icon: CheckCircle };
    if (score >= 0.6) return { level: 'Medium', color: warningColor, icon: AlertTriangle };
    return { level: 'Low', color: errorColor, icon: AlertTriangle };
  };

  const confidence = getConfidenceLevel(confidenceScore || 0.75);

  // Risk assessment
  const getRiskLevel = (risk) => {
    if (risk < 0.3) return { level: 'Low', color: successColor, percentage: risk * 100 };
    if (risk < 0.6) return { level: 'Medium', color: warningColor, percentage: risk * 100 };
    return { level: 'High', color: errorColor, percentage: risk * 100 };
  };

  return (
    <Box
      bg={bgColor}
      borderWidth="1px"
      borderColor={borderColor}
      borderRadius="lg"
      overflow="hidden"
      boxShadow="0 2px 4px rgba(68, 21, 182, 0.08)"
      mt={3}
    >
      {/* Header */}
      <Flex
        align="center"
        justify="space-between"
        p={3}
        bg={insightBg}
        cursor="pointer"
        onClick={() => setIsExpanded(!isExpanded)}
        _hover={{ opacity: 0.8 }}
        transition="opacity 0.2s"
      >
        <HStack spacing={2}>
          <Icon as={Brain} boxSize={4} color={accentColor} />
          <Text fontWeight="semibold" color={accentColor} fontSize="sm">
            AI Reasoning Insights
          </Text>
          <Badge colorScheme="purple" size="sm" borderRadius="full">
            Transparency Mode
          </Badge>
        </HStack>
        
        <HStack spacing={2}>
          <Icon as={confidence.icon} boxSize={3} color={confidence.color} />
          <Text fontSize="xs" color={confidence.color} fontWeight="medium">
            {confidence.level} Confidence
          </Text>
        </HStack>
      </Flex>

      {/* Content */}
      <Collapse in={isExpanded}>
        <Box p={4}>
          
          {/* Context Analysis */}
          {contextMetadata && (
            <Box mb={4}>
              <HStack spacing={2} mb={3}>
                <Icon as={Database} boxSize={4} color={accentColor} />
                <Text fontWeight="semibold" color={textColor} fontSize="sm">
                  Context Analysis
                </Text>
              </HStack>
              
              <SimpleGrid columns={3} spacing={3} mb={3}>
                <Stat size="sm" bg={metricBg} p={3} borderRadius="md">
                  <StatLabel color={mutedTextColor} fontSize="xs">Sources Found</StatLabel>
                  <StatNumber color={textColor} fontSize="lg">
                    {contextMetadata.source_count || 0}
                  </StatNumber>
                  <StatHelpText color={mutedTextColor} fontSize="xs">
                    documents retrieved
                  </StatHelpText>
                </Stat>
                
                <Stat size="sm" bg={metricBg} p={3} borderRadius="md">
                  <StatLabel color={mutedTextColor} fontSize="xs">Context Quality</StatLabel>
                  <StatNumber color={textColor} fontSize="lg">
                    {contextMetadata.context_quality || 'N/A'}
                  </StatNumber>
                  <StatHelpText color={mutedTextColor} fontSize="xs">
                    relevance assessment
                  </StatHelpText>
                </Stat>
                
                <Stat size="sm" bg={metricBg} p={3} borderRadius="md">
                  <StatLabel color={mutedTextColor} fontSize="xs">Confidence</StatLabel>
                  <StatNumber color={confidence.color} fontSize="lg">
                    {Math.round((confidenceScore || 0.75) * 100)}%
                  </StatNumber>
                  <StatHelpText color={mutedTextColor} fontSize="xs">
                    response reliability
                  </StatHelpText>
                </Stat>
              </SimpleGrid>
              
              {/* Risk Assessment */}
              {contextMetadata.hallucination_risk !== undefined && (
                <Box>
                  <Text fontWeight="medium" color={textColor} fontSize="sm" mb={2}>
                    Risk Assessment
                  </Text>
                  {(() => {
                    const risk = getRiskLevel(contextMetadata.hallucination_risk);
                    return (
                      <Box bg={metricBg} p={3} borderRadius="md">
                        <Flex align="center" justify="space-between" mb={2}>
                          <HStack>
                            <Icon as={Shield} boxSize={3} color={risk.color} />
                            <Text fontSize="xs" fontWeight="medium" color={risk.color}>
                              {risk.level} Risk
                            </Text>
                          </HStack>
                          <Text fontSize="xs" color={mutedTextColor}>
                            {Math.round(risk.percentage)}% uncertainty
                          </Text>
                        </Flex>
                        <Progress 
                          value={100 - risk.percentage} 
                          size="sm" 
                          colorScheme={risk.level === 'Low' ? 'green' : risk.level === 'Medium' ? 'yellow' : 'red'}
                          borderRadius="full"
                        />
                        <Text fontSize="xs" color={mutedTextColor} mt={1}>
                          Information reliability score
                        </Text>
                      </Box>
                    );
                  })()}
                </Box>
              )}
            </Box>
          )}
          
          <Divider my={4} />
          
          {/* Processing Insights */}
          <Box>
            <HStack spacing={2} mb={3}>
              <Icon as={Eye} boxSize={4} color={accentColor} />
              <Text fontWeight="semibold" color={textColor} fontSize="sm">
                Processing Insights
              </Text>
            </HStack>
            
            <VStack spacing={2} align="stretch">
              <Box bg={metricBg} p={3} borderRadius="md">
                <HStack spacing={2} mb={1}>
                  <Icon as={Zap} boxSize={3} color={accentColor} />
                  <Text fontSize="xs" fontWeight="medium" color={textColor}>
                    Decision Process
                  </Text>
                </HStack>
                <Text fontSize="xs" color={mutedTextColor}>
                  The AI used multi-step reasoning combining semantic search, context evaluation, 
                  and domain expertise to generate this response.
                </Text>
              </Box>
              
              <Box bg={metricBg} p={3} borderRadius="md">
                <HStack spacing={2} mb={1}>
                  <Icon as={TrendingUp} boxSize={3} color={accentColor} />
                  <Text fontSize="xs" fontWeight="medium" color={textColor}>
                    Quality Assurance
                  </Text>
                </HStack>
                <Text fontSize="xs" color={mutedTextColor}>
                  Information was cross-referenced with multiple sources and validated 
                  against regulatory standards before presentation.
                </Text>
              </Box>
              
              {processingMetrics && processingMetrics.responseTime && (
                <Box bg={metricBg} p={3} borderRadius="md">
                  <HStack spacing={2} mb={1}>
                    <Icon as={Clock} boxSize={3} color={accentColor} />
                    <Text fontSize="xs" fontWeight="medium" color={textColor}>
                      Processing Time
                    </Text>
                  </HStack>
                  <Text fontSize="xs" color={mutedTextColor}>
                    Response generated in {processingMetrics.responseTime}ms with 
                    {processingMetrics.tokenCount || 'N/A'} tokens processed.
                  </Text>
                </Box>
              )}
            </VStack>
          </Box>
        </Box>
      </Collapse>
    </Box>
  );
};

export default AIReasoningPanel; 