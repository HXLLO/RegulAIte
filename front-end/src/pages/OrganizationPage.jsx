import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Heading,
  Text,
  Card,
  CardBody,
  CardHeader,
  VStack,
  HStack,
  SimpleGrid,
  Badge,
  Spinner,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  useToast,
  useColorModeValue,
  Icon,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Flex,
  Divider,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  TableContainer,
  Avatar,
  AvatarGroup
} from '@chakra-ui/react';
import { 
  FiBriefcase, 
  FiUsers, 
  FiGlobe, 
  FiShield, 
  FiSettings,
  FiEdit,
  FiPlus,
  FiCheckCircle,
  FiAlertTriangle,
  FiInfo
} from 'react-icons/fi';
import { useNavigate } from 'react-router-dom';
import { getOrganizationProfile, getAllOrganizations } from '../services/organizationService';

const ACCENT_COLOR = '#4415b6';

const OrganizationPage = () => {
  const [organization, setOrganization] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const toast = useToast();
  const navigate = useNavigate();
  const cardBg = useColorModeValue('white', 'gray.700');
  const bgColor = useColorModeValue('gray.50', 'gray.900');

  useEffect(() => {
    loadOrganization();
  }, []);

  const loadOrganization = async () => {
    setIsLoading(true);
    try {
      // First try to get from localStorage (for test mode)
      const localOrg = localStorage.getItem('organization_profile');
      if (localOrg) {
        const orgData = JSON.parse(localOrg);
        console.log('Loaded organization from localStorage:', orgData);
        setOrganization(orgData);
        setIsLoading(false);
        return;
      }

      // Try to get from API
      try {
        const organizations = await getAllOrganizations();
        if (organizations && organizations.length > 0) {
          setOrganization(organizations[0]); // Use first organization for now
        } else {
          setOrganization(null);
        }
      } catch (apiError) {
        console.log('No organizations found via API:', apiError);
        setOrganization(null);
      }
    } catch (error) {
      console.error('Error loading organization:', error);
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSetupOrganization = () => {
    navigate('/organization/setup');
  };

  const handleEditOrganization = () => {
    navigate('/organization/setup', { state: { editMode: true, organizationData: organization } });
  };

  const formatValue = (value) => {
    if (Array.isArray(value)) {
      return value.length > 0 ? value.join(', ') : 'Not specified';
    }
    if (typeof value === 'object' && value !== null) {
      return Object.entries(value).map(([k, v]) => `${k}: ${v}`).join(', ');
    }
    return value || 'Not specified';
  };

  const getComplianceStatus = (frameworks) => {
    if (!frameworks || frameworks.length === 0) {
      return { color: 'orange', text: 'Needs Configuration', icon: FiAlertTriangle };
    }
    return { color: 'green', text: 'Configured', icon: FiCheckCircle };
  };

  const getRiskLevel = (riskAppetite) => {
    const riskColors = {
      conservative: 'green',
      moderate: 'yellow',
      aggressive: 'red',
      low: 'green',
      medium: 'yellow',
      high: 'red'
    };
    return riskColors[riskAppetite] || 'gray';
  };

  if (isLoading) {
    return (
      <Box p={8} maxW="6xl" mx="auto">
        <VStack spacing={8} align="center" justify="center" minH="400px">
          <Spinner size="xl" color={ACCENT_COLOR} />
          <Text>Loading organization information...</Text>
        </VStack>
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={8} maxW="6xl" mx="auto">
        <Alert status="error">
          <AlertIcon />
          <AlertTitle>Error loading organization!</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </Box>
    );
  }

  if (!organization) {
    return (
      <Box p={8} maxW="6xl" mx="auto">
        <VStack spacing={8} align="stretch">
          <Box textAlign="center">
            <Heading size="xl" mb={2}>Organization Configuration</Heading>
            <Text color="gray.600" fontSize="lg">
              Welcome to RegulAIte! Let's set up your organization profile.
            </Text>
          </Box>

          <Card bg={cardBg} shadow="lg" maxW="2xl" mx="auto">
            <CardBody textAlign="center" p={8}>
              <VStack spacing={6}>
                <Box as={FiBriefcase} size="64px" color={ACCENT_COLOR} />
                <Heading size="lg">No Organization Configured</Heading>
                <Text color="gray.600">
                  You haven't set up your organization yet. Create your organization profile 
                  to get personalized GRC analysis and recommendations.
                </Text>
                
                <VStack spacing={4} align="stretch" w="full">
                  <Text fontSize="sm" fontWeight="bold" color="gray.700">
                    What you'll configure:
                  </Text>
                  <SimpleGrid columns={2} spacing={4} fontSize="sm">
                    <HStack>
                      <Icon as={FiBriefcase} color={ACCENT_COLOR} />
                      <Text>Basic Information</Text>
                    </HStack>
                    <HStack>
                      <Icon as={FiGlobe} color={ACCENT_COLOR} />
                      <Text>Operations</Text>
                    </HStack>
                    <HStack>
                      <Icon as={FiShield} color={ACCENT_COLOR} />
                      <Text>Risk & Governance</Text>
                    </HStack>
                    <HStack>
                      <Icon as={FiSettings} color={ACCENT_COLOR} />
                      <Text>Compliance</Text>
                    </HStack>
                  </SimpleGrid>
                </VStack>

                <Button
                  leftIcon={<FiPlus />}
                  onClick={handleSetupOrganization}
                  bg={ACCENT_COLOR}
                  color="white"
                  size="lg"
                  _hover={{ bg: '#3311a0' }}
                  w="full"
                >
                  Set Up Organization
                </Button>
              </VStack>
            </CardBody>
          </Card>
        </VStack>
      </Box>
    );
  }

  const complianceStatus = getComplianceStatus(organization.preferred_methodologies);

  return (
    <Box p={8} maxW="6xl" mx="auto" bg={bgColor} minH="100vh">
      <VStack spacing={8} align="stretch">
        {/* Header */}
        <Flex justify="space-between" align="center">
          <VStack align="start" spacing={1}>
            <Heading size="xl">{organization.name}</Heading>
            <HStack>
              <Badge colorScheme="blue" variant="subtle">
                {organization.organization_type?.replace('_', ' ').toUpperCase()}
              </Badge>
              <Badge colorScheme="green" variant="subtle">
                {organization.sector?.toUpperCase()}
              </Badge>
              <Badge colorScheme="purple" variant="subtle">
                {organization.size?.toUpperCase()}
              </Badge>
            </HStack>
          </VStack>
          
          <Button
            leftIcon={<FiEdit />}
            onClick={handleEditOrganization}
            bg={ACCENT_COLOR}
            color="white"
            _hover={{ bg: '#3311a0' }}
          >
            Edit Configuration
          </Button>
        </Flex>

        {/* Overview Stats */}
        <SimpleGrid columns={{ base: 2, md: 4 }} spacing={6}>
          <Card bg={cardBg}>
            <CardBody>
              <Stat>
                <StatLabel>Employees</StatLabel>
                <StatNumber>{organization.employee_count?.toLocaleString()}</StatNumber>
                <StatHelpText>Current workforce</StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card bg={cardBg}>
            <CardBody>
              <Stat>
                <StatLabel>Revenue</StatLabel>
                <StatNumber>{organization.annual_revenue}</StatNumber>
                <StatHelpText>Annual revenue</StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card bg={cardBg}>
            <CardBody>
              <Stat>
                <StatLabel>Risk Appetite</StatLabel>
                <StatNumber>
                  <Badge colorScheme={getRiskLevel(organization.risk_appetite)} size="lg">
                    {organization.risk_appetite?.toUpperCase()}
                  </Badge>
                </StatNumber>
                <StatHelpText>Current level</StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card bg={cardBg}>
            <CardBody>
              <Stat>
                <StatLabel>Compliance</StatLabel>
                <StatNumber>
                  <HStack>
                    <Icon as={complianceStatus.icon} color={`${complianceStatus.color}.500`} />
                    <Text fontSize="sm">{complianceStatus.text}</Text>
                  </HStack>
                </StatNumber>
                <StatHelpText>
                  {organization.preferred_methodologies?.length || 0} frameworks
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>
        </SimpleGrid>

        {/* Detailed Information */}
        <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6}>
          {/* Basic Information */}
          <Card bg={cardBg}>
            <CardHeader>
              <HStack>
                <Icon as={FiBriefcase} color={ACCENT_COLOR} />
                <Heading size="md">Basic Information</Heading>
              </HStack>
            </CardHeader>
            <CardBody>
              <VStack align="stretch" spacing={4}>
                <HStack justify="space-between">
                  <Text fontWeight="bold">Organization ID:</Text>
                  <Text>{organization.organization_id}</Text>
                </HStack>
                <HStack justify="space-between">
                  <Text fontWeight="bold">Type:</Text>
                  <Text textTransform="capitalize">{organization.organization_type?.replace('_', ' ')}</Text>
                </HStack>
                <HStack justify="space-between">
                  <Text fontWeight="bold">Sector:</Text>
                  <Text textTransform="capitalize">{organization.sector}</Text>
                </HStack>
                <HStack justify="space-between">
                  <Text fontWeight="bold">Size:</Text>
                  <Text textTransform="capitalize">{organization.size}</Text>
                </HStack>
              </VStack>
            </CardBody>
          </Card>

          {/* Operational Context */}
          <Card bg={cardBg}>
            <CardHeader>
              <HStack>
                <Icon as={FiGlobe} color={ACCENT_COLOR} />
                <Heading size="md">Operational Context</Heading>
              </HStack>
            </CardHeader>
            <CardBody>
              <VStack align="stretch" spacing={4}>
                <Box>
                  <Text fontWeight="bold" mb={1}>Business Model:</Text>
                  <Text textTransform="capitalize">{organization.business_model}</Text>
                </Box>
                <Box>
                  <Text fontWeight="bold" mb={1}>Digital Maturity:</Text>
                  <Text textTransform="capitalize">{organization.digital_maturity}</Text>
                </Box>
                <Box>
                  <Text fontWeight="bold" mb={1}>Geographic Presence:</Text>
                  <Text textTransform="capitalize">{formatValue(organization.geographical_presence)}</Text>
                </Box>
              </VStack>
            </CardBody>
          </Card>

          {/* Risk & Governance */}
          <Card bg={cardBg}>
            <CardHeader>
              <HStack>
                <Icon as={FiShield} color={ACCENT_COLOR} />
                <Heading size="md">Risk & Governance</Heading>
              </HStack>
            </CardHeader>
            <CardBody>
              <VStack align="stretch" spacing={4}>
                <Box>
                  <Text fontWeight="bold" mb={2}>Risk Tolerance:</Text>
                  <SimpleGrid columns={2} spacing={2} fontSize="sm">
                    {organization.risk_tolerance && Object.entries(organization.risk_tolerance).map(([key, value]) => (
                      <HStack key={key} justify="space-between">
                        <Text textTransform="capitalize">{key}:</Text>
                        <Badge size="sm" colorScheme={getRiskLevel(value)} textTransform="uppercase">{value}</Badge>
                      </HStack>
                    ))}
                  </SimpleGrid>
                </Box>
                <Box>
                  <Text fontWeight="bold" mb={2}>Governance Maturity:</Text>
                  <SimpleGrid columns={1} spacing={2} fontSize="sm">
                    {organization.governance_maturity && Object.entries(organization.governance_maturity).map(([key, value]) => (
                      <HStack key={key} justify="space-between">
                        <Text textTransform="capitalize">{key}:</Text>
                        <Badge size="sm" variant="outline" textTransform="capitalize">{value}</Badge>
                      </HStack>
                    ))}
                  </SimpleGrid>
                </Box>
              </VStack>
            </CardBody>
          </Card>

          {/* Compliance */}
          <Card bg={cardBg}>
            <CardHeader>
              <HStack>
                <Icon as={FiSettings} color={ACCENT_COLOR} />
                <Heading size="md">Compliance & Preferences</Heading>
              </HStack>
            </CardHeader>
            <CardBody>
              <VStack align="stretch" spacing={4}>
                <Box>
                  <Text fontWeight="bold" mb={2}>Active Frameworks:</Text>
                  {organization.preferred_methodologies && organization.preferred_methodologies.length > 0 ? (
                    <SimpleGrid columns={2} spacing={2}>
                      {organization.preferred_methodologies.map((framework) => (
                        <Badge key={framework} colorScheme="green" variant="subtle">
                          {framework.toUpperCase()}
                        </Badge>
                      ))}
                    </SimpleGrid>
                  ) : (
                    <Text fontSize="sm" color="gray.500">No frameworks configured</Text>
                  )}
                </Box>
                <Box>
                  <Text fontWeight="bold" mb={2}>Analysis Preferences:</Text>
                  <VStack align="stretch" spacing={1} fontSize="sm">
                    <HStack justify="space-between">
                      <Text>Detail Level:</Text>
                      <Text textTransform="capitalize">{organization.analysis_preferences?.detail_level}</Text>
                    </HStack>
                    <HStack justify="space-between">
                      <Text>Report Format:</Text>
                      <Text textTransform="capitalize">{organization.analysis_preferences?.report_format?.replace('_', ' ')}</Text>
                    </HStack>
                  </VStack>
                </Box>
              </VStack>
            </CardBody>
          </Card>
        </SimpleGrid>

        </VStack>
    </Box>
  );
};

export default OrganizationPage; 