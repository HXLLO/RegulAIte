import React, { useEffect, useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { 
  Box, 
  Flex, 
  Heading, 
  Text, 
  Button, 
  Grid, 
  Card, 
  CardHeader, 
  CardBody, 
  CardFooter,
  Spinner,
  Stat,
  StatNumber,
  StatHelpText,
  useColorModeValue
} from '@chakra-ui/react';
import { useAuth } from '../contexts/AuthContext';
import UserProfile from '../components/auth/UserProfile';
import { getDocumentStats } from '../services/documentService';

const DashboardPage = () => {
  const { currentUser } = useAuth();
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState(null);
  const [error, setError] = useState(null);
  
  // Chakra UI colors
  const accentColor = '#4415b6';
  const cardBg = useColorModeValue('white', 'gray.700');

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Get real document statistics from API
        const docStats = await getDocumentStats();
        
        setDashboardData({
          documentCount: docStats.total_documents,
          totalChunks: docStats.total_chunks,
          documentsByType: docStats.documents_by_type,
          documentsByLanguage: docStats.documents_by_language,
          recentUploads: docStats.recent_uploads,
          totalStorageMb: docStats.total_storage_mb
        });
        setLoading(false);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        setError('Failed to load dashboard data. Please try again later.');
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <Flex justify="center" align="center" height="100vh">
        <Spinner size="xl" color={accentColor} />
        <Text ml={4}>Loading dashboard...</Text>
      </Flex>
    );
  }

  if (error) {
    return (
      <Flex justify="center" align="center" height="100vh" direction="column">
        <Text color="red.500" fontSize="lg" mb={4}>{error}</Text>
        <Button onClick={() => window.location.reload()} colorScheme="purple">
          Retry
        </Button>
      </Flex>
    );
  }

  return (
    <Box p={6} minH="100vh">
      <Box maxW="7xl" mx="auto">
        <Flex 
          direction={{ base: 'column', md: 'row' }} 
          justify="space-between" 
          align={{ base: 'flex-start', md: 'center' }}
          mb={8}
          gap={4}
        >
          <Box>
            <Heading as="h1" size="xl" mb={2}>Dashboard</Heading>
            <Text color="gray.500">
              Welcome back, {currentUser?.full_name || 'User'}!
            </Text>
          </Box>
          <Flex gap={3}>
            <Button as={RouterLink} to="/chat" variant="outline">
              Start Chat
            </Button>
            <Button 
              as={RouterLink} 
              to="/documents" 
              bg={accentColor}
              color="white"
              _hover={{ bg: '#3a1296' }}
            >
              View Documents
            </Button>
          </Flex>
        </Flex>

        {/* Main dashboard cards */}
        <Grid 
          templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)', lg: 'repeat(3, 1fr)' }}
          gap={6}
        >
          <Card bg={cardBg} boxShadow="md" borderRadius="lg">
            <CardHeader>
              <Heading size="md">Documents</Heading>
              <Text fontSize="sm" color="gray.500">Your regulatory document library</Text>
            </CardHeader>
            <CardBody>
              <Stat>
                <StatNumber fontSize="3xl" color={accentColor}>
                  {dashboardData?.documentCount || 0}
                </StatNumber>
                <StatHelpText>Total documents</StatHelpText>
              </Stat>
              {dashboardData?.totalStorageMb > 0 && (
                <Stat mt={3}>
                  <StatNumber fontSize="lg">
                    {dashboardData.totalStorageMb.toFixed(1)} MB
                  </StatNumber>
                  <StatHelpText>Storage used</StatHelpText>
                </Stat>
              )}
            </CardBody>
            <CardFooter>
              <Button 
                as={RouterLink} 
                to="/documents"
                variant="outline"
                width="full"
              >
                Browse Documents
              </Button>
            </CardFooter>
          </Card>

          <Card bg={cardBg} boxShadow="md" borderRadius="lg">
            <CardHeader>
              <Heading size="md">AI Assistant</Heading>
              <Text fontSize="sm" color="gray.500">Get instant answers to compliance questions</Text>
            </CardHeader>
            <CardBody>
              <Text fontSize="sm" color="gray.600">
                Ask questions about your documents and get AI-powered insights on governance, 
                risk, and compliance topics.
              </Text>
            </CardBody>
            <CardFooter>
              <Button 
                as={RouterLink} 
                to="/chat"
                bg={accentColor}
                color="white"
                width="full"
                _hover={{ bg: '#3a1296' }}
              >
                Start Chatting
              </Button>
            </CardFooter>
          </Card>

          <Card bg={cardBg} boxShadow="md" borderRadius="lg">
            <CardHeader>
              <Heading size="md">Account</Heading>
              <Text fontSize="sm" color="gray.500">Your profile and settings</Text>
            </CardHeader>
            <CardBody>
              <UserProfile />
            </CardBody>
          </Card>
        </Grid>
      </Box>
    </Box>
  );
};

export default DashboardPage; 