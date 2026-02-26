import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  FormErrorMessage,
  FormHelperText,
  Input,
  Select,
  Stack,
  Heading,
  Text,
  Card,
  CardBody,
  CardHeader,
  Grid,
  GridItem,
  Badge,
  VStack,
  HStack,
  Textarea,
  Checkbox,
  CheckboxGroup,
  useToast,
  useColorModeValue,
  Progress,
  Flex,
  Icon,
  Tooltip,
  Divider,
  Container,
  Spinner,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  IconButton,
  SimpleGrid,
  NumberInput,
  NumberInputField
} from '@chakra-ui/react';
import { 
  FiBriefcase, 
  FiUsers, 
  FiGlobe, 
  FiShield, 
  FiSettings,
  FiInfo,
  FiCheck,
  FiArrowRight,
  FiArrowLeft
} from 'react-icons/fi';
import { createOrganizationProfile, validateOrganizationConfig, getOrganizationTemplates, updateOrganizationProfile } from '../services/organizationService';
import { useNavigate, useLocation } from 'react-router-dom';

const ACCENT_COLOR = '#4415b6';

const OrganizationSetupPage = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [templates, setTemplates] = useState(null);
  const [errors, setErrors] = useState({});
  const [isEditMode, setIsEditMode] = useState(false);
  
  const navigate = useNavigate();
  const location = useLocation();
  const toast = useToast();
  const cardBg = useColorModeValue('white', 'gray.700');
  const stepperBg = useColorModeValue('gray.100', 'gray.600');

  // Check if we're in edit mode and get existing data
  useEffect(() => {
    if (location.state && location.state.editMode && location.state.organizationData) {
      setIsEditMode(true);
      setOrganizationData(location.state.organizationData);
      console.log('Edit mode activated with data:', location.state.organizationData);
    }
  }, [location.state]);

  const [organizationData, setOrganizationData] = useState({
    // Basic Information
    organization_id: '',
    name: '',
    organization_type: 'technology',
    sector: 'technology',
    size: 'medium',
    employee_count: 250,
    annual_revenue: '10M-100M',
    
    // Operational Context
    geographical_presence: [],
    business_model: 'digital',
    digital_maturity: 'intermediate',
    transformation_stage: 'evolving',
    
    // Risk & Governance
    risk_appetite: 'moderate',
    risk_tolerance: {
      cyber: 'medium',
      operational: 'medium',
      financial: 'medium',
      regulatory: 'low'
    },
    governance_maturity: {
      strategic: 'developing',
      risk: 'developing',
      compliance: 'developing'
    },
    
    // Compliance Preferences
    preferred_methodologies: [],
    analysis_preferences: {
      report_format: 'executive_summary',
      detail_level: 'high',
      focus_areas: []
    }
  });

  console.log('OrganizationSetupPage mounted, current step:', currentStep);
  console.log('Organization data:', organizationData);
  console.log('Templates loaded:', templates);
  console.log('Edit mode:', isEditMode);

  // Configuration options
  const organizationTypes = [
    { value: 'startup', label: 'Startup', description: 'Early-stage companies' },
    { value: 'sme', label: 'Small/Medium Enterprise', description: 'Growing businesses' },
    { value: 'large_corp', label: 'Large Corporation', description: 'Established enterprises' },
    { value: 'public_sector', label: 'Public Sector', description: 'Government entities' },
    { value: 'healthcare', label: 'Healthcare', description: 'Healthcare organizations' },
    { value: 'financial', label: 'Financial', description: 'Financial institutions' },
    { value: 'technology', label: 'Technology', description: 'Tech companies' },
    { value: 'manufacturing', label: 'Manufacturing', description: 'Manufacturing companies' },
    { value: 'energy', label: 'Energy', description: 'Energy sector' },
    { value: 'telecom', label: 'Telecommunications', description: 'Telecom companies' }
  ];

  const regulatorySectors = [
    { value: 'banking', label: 'Banking' },
    { value: 'insurance', label: 'Insurance' },
    { value: 'healthcare', label: 'Healthcare' },
    { value: 'energy', label: 'Energy' },
    { value: 'telecom', label: 'Telecommunications' },
    { value: 'technology', label: 'Technology' },
    { value: 'public', label: 'Public Sector' },
    { value: 'general', label: 'General' }
  ];

  const sizeCategories = [
    { value: 'startup', label: 'Startup', description: 'Limited resources, high agility', employees: '< 50' },
    { value: 'small', label: 'Small', description: 'Developing governance, moderate resources', employees: '50-250' },
    { value: 'medium', label: 'Medium', description: 'Defined processes, adequate budget', employees: '250-1000' },
    { value: 'large', label: 'Large', description: 'Managed governance, substantial resources', employees: '1000+' }
  ];

  const complianceFrameworks = [
    { value: 'iso27001', label: 'ISO 27001', description: 'Information Security Management' },
    { value: 'rgpd', label: 'RGPD/GDPR', description: 'Data Protection Regulation' },
    { value: 'dora', label: 'DORA', description: 'Digital Operational Resilience Act' },
    { value: 'nist', label: 'NIST', description: 'Cybersecurity Framework' },
    { value: 'sox', label: 'SOX', description: 'Sarbanes-Oxley Act' },
    { value: 'pci_dss', label: 'PCI DSS', description: 'Payment Card Industry Standard' },
    { value: 'hipaa', label: 'HIPAA', description: 'Health Insurance Portability' },
    { value: 'anssi', label: 'ANSSI', description: 'French Cybersecurity Agency' }
  ];

  const geographicalRegions = [
    'France', 'Europe', 'North America', 'Asia Pacific', 
    'Latin America', 'Middle East', 'Africa', 'Global'
  ];

  const focusAreas = [
    'cybersecurity', 'data_protection', 'cloud_security', 
    'risk_management', 'compliance_monitoring', 'governance',
    'business_continuity', 'incident_response', 'vendor_management'
  ];

  const steps = [
    { id: 1, title: 'Basic Information', icon: FiBriefcase },
    { id: 2, title: 'Operational Context', icon: FiGlobe },
    { id: 3, title: 'Risk & Governance', icon: FiShield },
    { id: 4, title: 'Compliance & Preferences', icon: FiSettings }
  ];

  // Use fallback data if templates are not loaded
  const getTemplateData = () => ({
    organization_types: templates?.organization_types || organizationTypes,
    regulatory_sectors: templates?.regulatory_sectors || regulatorySectors,
    size_categories: templates?.size_categories || sizeCategories,
    compliance_frameworks: templates?.compliance_frameworks || complianceFrameworks
  });

  const templateData = getTemplateData();

  const handleInputChange = (field, value) => {
    setOrganizationData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleNestedInputChange = (parent, field, value) => {
    setOrganizationData(prev => ({
      ...prev,
      [parent]: {
        ...prev[parent],
        [field]: value
      }
    }));
  };

  const handleArrayChange = (field, value, checked) => {
    setOrganizationData(prev => ({
      ...prev,
      [field]: checked 
        ? [...prev[field], value]
        : prev[field].filter(item => item !== value)
    }));
  };

  const nextStep = () => {
    if (currentStep < steps.length) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSubmit = async () => {
    console.log('handleSubmit called');
    console.log('Organization data being submitted:', organizationData);
    console.log('Edit mode:', isEditMode);
    
    setIsLoading(true);
    
    try {
      // Generate organization ID if not provided (for new orgs only)
      if (!organizationData.organization_id && !isEditMode) {
        const id = organizationData.name.toLowerCase().replace(/\s+/g, '-') + '-' + Date.now();
        organizationData.organization_id = id;
        console.log('Generated organization ID:', id);
      }

      // Prepare data with custom settings
      const submitData = {
        ...organizationData,
        custom_settings: {
          preferred_methodologies: organizationData.preferred_methodologies,
          analysis_preferences: organizationData.analysis_preferences,
          risk_appetite: organizationData.risk_appetite
        }
      };

      console.log('Final submit data:', submitData);

      // For testing purposes, simulate API call if backend is not available
      const isTestMode = process.env.NODE_ENV === 'development';
      
      if (isTestMode) {
        console.log('Running in test mode');
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        console.log(`Organization profile ${isEditMode ? 'updated' : 'created'} (test mode):`, submitData);
        
        toast({
          title: `Organization ${isEditMode ? 'updated' : 'configured'} successfully! (Test Mode)`,
          description: `Your organization profile has been ${isEditMode ? 'updated' : 'created'} locally for testing.`,
          status: 'success',
          duration: 5000,
          isClosable: true,
        });
        
        // Store in localStorage for testing
        localStorage.setItem('organization_profile', JSON.stringify(submitData));
        console.log('Saved to localStorage');
        
      } else {
        console.log(`Trying API call: ${isEditMode ? 'update' : 'create'}`);
        // Try actual API call
        try {
          const result = isEditMode 
            ? await updateOrganizationProfile(organizationData.organization_id, submitData)
            : await createOrganizationProfile(submitData);
          console.log('API call successful:', result);
          
          toast({
            title: `Organization ${isEditMode ? 'updated' : 'configured'} successfully!`,
            description: `Your organization profile has been ${isEditMode ? 'updated' : 'created'} and is ready for analysis.`,
            status: 'success',
            duration: 5000,
            isClosable: true,
          });
        } catch (apiError) {
          // Fallback to test mode if API fails
          console.log('API failed, falling back to test mode:', apiError);
          console.log(`Organization profile ${isEditMode ? 'updated' : 'created'} (fallback):`, submitData);
          localStorage.setItem('organization_profile', JSON.stringify(submitData));
          
          toast({
            title: `Organization ${isEditMode ? 'updated' : 'configured'} locally!`,
            description: `Backend not available. Configuration saved locally for testing.`,
            status: 'warning',
            duration: 5000,
            isClosable: true,
          });
        }
      }
      
      // Redirect to organization page after success
      console.log('Redirecting to organization page in 2 seconds...');
      setTimeout(() => {
        navigate('/organization');
      }, 2000);
        
    } catch (error) {
      console.error('Organization setup error:', error);
      toast({
        title: 'Configuration failed',
        description: error.message || `There was an error ${isEditMode ? 'updating' : 'setting up'} your organization. Please try again.`,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const renderStepIndicator = () => (
    <Box mb={8}>
      <Progress 
        value={(currentStep / steps.length) * 100} 
        bg="gray.100"
        sx={{
          '& > div': {
            bg: ACCENT_COLOR
          }
        }}
        mb={4} 
      />
      <HStack spacing={4} justify="center">
        {steps.map((step) => (
          <VStack key={step.id} spacing={2}>
            <Box
              w={12}
              h={12}
              rounded="full"
              bg={currentStep >= step.id ? ACCENT_COLOR : stepperBg}
              color={currentStep >= step.id ? 'white' : 'gray.500'}
              display="flex"
              alignItems="center"
              justifyContent="center"
            >
              <Icon as={currentStep > step.id ? FiCheck : step.icon} />
            </Box>
            <Text fontSize="sm" fontWeight={currentStep === step.id ? 'bold' : 'normal'}>
              {step.title}
            </Text>
          </VStack>
        ))}
      </HStack>
    </Box>
  );

  const renderBasicInformation = () => (
    <VStack spacing={6} align="stretch">
      <HStack>
        <Box as={FiBriefcase} color={ACCENT_COLOR} size="24px" />
        <Heading size="lg" color={ACCENT_COLOR}>Basic Organization Information</Heading>
      </HStack>
      
      <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
        <FormControl isRequired isInvalid={errors.name}>
          <FormLabel>Organization Name</FormLabel>
          <Input
            value={organizationData.name}
            onChange={(e) => handleInputChange('name', e.target.value)}
            placeholder="Enter organization name"
            focusBorderColor={ACCENT_COLOR}
          />
          <FormErrorMessage>{errors.name}</FormErrorMessage>
        </FormControl>

        <FormControl>
          <FormLabel>Organization Type</FormLabel>
          <Select
            value={organizationData.organization_type}
            onChange={(e) => handleInputChange('organization_type', e.target.value)}
            focusBorderColor={ACCENT_COLOR}
          >
            {templateData.organization_types.map(type => (
              <option key={type.value} value={type.value}>{type.label}</option>
            ))}
          </Select>
        </FormControl>

        <FormControl>
          <FormLabel>Regulatory Sector</FormLabel>
          <Select
            value={organizationData.sector}
            onChange={(e) => handleInputChange('sector', e.target.value)}
            focusBorderColor={ACCENT_COLOR}
          >
            {templateData.regulatory_sectors.map(sector => (
              <option key={sector.value} value={sector.value}>{sector.label}</option>
            ))}
          </Select>
        </FormControl>

        <FormControl>
          <FormLabel>Organization Size</FormLabel>
          <Select
            value={organizationData.size}
            onChange={(e) => handleInputChange('size', e.target.value)}
            focusBorderColor={ACCENT_COLOR}
          >
            {templateData.size_categories.map(size => (
              <option key={size.value} value={size.value}>{size.label}</option>
            ))}
          </Select>
        </FormControl>

        <FormControl isInvalid={errors.employee_count}>
          <FormLabel>Employee Count</FormLabel>
          <NumberInput
            value={organizationData.employee_count}
            onChange={(value) => handleInputChange('employee_count', parseInt(value) || 1)}
            min={1}
            focusBorderColor={ACCENT_COLOR}
          >
            <NumberInputField />
          </NumberInput>
          <FormErrorMessage>{errors.employee_count}</FormErrorMessage>
        </FormControl>

        <FormControl>
          <FormLabel>Annual Revenue</FormLabel>
          <Select
            value={organizationData.annual_revenue}
            onChange={(e) => handleInputChange('annual_revenue', e.target.value)}
            focusBorderColor={ACCENT_COLOR}
          >
            <option value="<1M">Less than $1M</option>
            <option value="1M-10M">$1M - $10M</option>
            <option value="10M-100M">$10M - $100M</option>
            <option value="100M-1B">$100M - $1B</option>
            <option value=">1B">Over $1B</option>
          </Select>
        </FormControl>
      </SimpleGrid>
    </VStack>
  );

  const renderOperationalContext = () => (
    <VStack spacing={6} align="stretch">
      <HStack>
        <Box as={FiGlobe} color={ACCENT_COLOR} size="24px" />
        <Heading size="lg" color={ACCENT_COLOR}>Operational Context</Heading>
      </HStack>
      
      <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
        <FormControl isInvalid={errors.business_model}>
          <FormLabel>Business Model</FormLabel>
          <Select
            value={organizationData.business_model}
            onChange={(e) => handleInputChange('business_model', e.target.value)}
            focusBorderColor={ACCENT_COLOR}
          >
            <option value="digital">Digital/Technology</option>
            <option value="traditional">Traditional</option>
            <option value="hybrid">Hybrid</option>
            <option value="platform">Platform Business</option>
            <option value="service">Service-Based</option>
          </Select>
          <FormErrorMessage>{errors.business_model}</FormErrorMessage>
        </FormControl>

        <FormControl>
          <FormLabel>Digital Maturity</FormLabel>
          <Select
            value={organizationData.digital_maturity}
            onChange={(e) => handleInputChange('digital_maturity', e.target.value)}
            focusBorderColor={ACCENT_COLOR}
          >
            <option value="basic">Basic</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
            <option value="leader">Digital Leader</option>
          </Select>
        </FormControl>

        <FormControl>
          <FormLabel>Transformation Stage</FormLabel>
          <Select
            value={organizationData.transformation_stage}
            onChange={(e) => handleInputChange('transformation_stage', e.target.value)}
            focusBorderColor={ACCENT_COLOR}
          >
            <option value="planning">Planning</option>
            <option value="pilot">Pilot</option>
            <option value="evolving">Evolving</option>
            <option value="scaling">Scaling</option>
            <option value="optimized">Optimized</option>
          </Select>
        </FormControl>
      </SimpleGrid>

      <FormControl>
        <FormLabel>Geographical Presence</FormLabel>
        <CheckboxGroup 
          value={organizationData.geographical_presence} 
          onChange={(values) => handleInputChange('geographical_presence', values)}
        >
          <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4}>
            <Checkbox 
              value="europe" 
              sx={{
                '& .chakra-checkbox__control[data-checked]': {
                  bg: ACCENT_COLOR,
                  borderColor: ACCENT_COLOR,
                }
              }}
            >
              Europe
            </Checkbox>
            <Checkbox 
              value="north_america"
              sx={{
                '& .chakra-checkbox__control[data-checked]': {
                  bg: ACCENT_COLOR,
                  borderColor: ACCENT_COLOR,
                }
              }}
            >
              North America
            </Checkbox>
            <Checkbox 
              value="asia_pacific"
              sx={{
                '& .chakra-checkbox__control[data-checked]': {
                  bg: ACCENT_COLOR,
                  borderColor: ACCENT_COLOR,
                }
              }}
            >
              Asia Pacific
            </Checkbox>
            <Checkbox 
              value="latin_america"
              sx={{
                '& .chakra-checkbox__control[data-checked]': {
                  bg: ACCENT_COLOR,
                  borderColor: ACCENT_COLOR,
                }
              }}
            >
              Latin America
            </Checkbox>
            <Checkbox 
              value="africa"
              sx={{
                '& .chakra-checkbox__control[data-checked]': {
                  bg: ACCENT_COLOR,
                  borderColor: ACCENT_COLOR,
                }
              }}
            >
              Africa
            </Checkbox>
            <Checkbox 
              value="middle_east"
              sx={{
                '& .chakra-checkbox__control[data-checked]': {
                  bg: ACCENT_COLOR,
                  borderColor: ACCENT_COLOR,
                }
              }}
            >
              Middle East
            </Checkbox>
          </SimpleGrid>
        </CheckboxGroup>
      </FormControl>
    </VStack>
  );

  const renderRiskGovernance = () => (
    <VStack spacing={6} align="stretch">
      <HStack>
        <Box as={FiShield} color={ACCENT_COLOR} size="24px" />
        <Heading size="lg" color={ACCENT_COLOR}>Risk & Governance</Heading>
      </HStack>
      
      <FormControl isInvalid={errors.risk_appetite}>
        <FormLabel>Risk Appetite</FormLabel>
        <Select
          value={organizationData.risk_appetite}
          onChange={(e) => handleInputChange('risk_appetite', e.target.value)}
          focusBorderColor={ACCENT_COLOR}
        >
          <option value="conservative">Conservative</option>
          <option value="moderate">Moderate</option>
          <option value="aggressive">Aggressive</option>
        </Select>
        <FormErrorMessage>{errors.risk_appetite}</FormErrorMessage>
      </FormControl>

      <FormControl>
        <FormLabel>Risk Tolerance by Category</FormLabel>
        <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
          {Object.entries(organizationData.risk_tolerance).map(([category, level]) => (
            <FormControl key={category}>
              <FormLabel fontSize="sm" textTransform="capitalize">
                {category.replace('_', ' ')} Risk
              </FormLabel>
              <Select
                value={level}
                onChange={(e) => handleNestedInputChange('risk_tolerance', category, e.target.value)}
                size="sm"
                focusBorderColor={ACCENT_COLOR}
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </Select>
            </FormControl>
          ))}
        </SimpleGrid>
      </FormControl>

      <FormControl>
        <FormLabel>Governance Maturity</FormLabel>
        <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4}>
          {Object.entries(organizationData.governance_maturity).map(([area, level]) => (
            <FormControl key={area}>
              <FormLabel fontSize="sm" textTransform="capitalize">
                {area.replace('_', ' ')}
              </FormLabel>
              <Select
                value={level}
                onChange={(e) => handleNestedInputChange('governance_maturity', area, e.target.value)}
                size="sm"
                focusBorderColor={ACCENT_COLOR}
              >
                <option value="initial">Initial</option>
                <option value="developing">Developing</option>
                <option value="defined">Defined</option>
                <option value="managed">Managed</option>
                <option value="optimized">Optimized</option>
              </Select>
            </FormControl>
          ))}
        </SimpleGrid>
      </FormControl>
    </VStack>
  );

  const renderCompliancePreferences = () => (
    <VStack spacing={6} align="stretch">
      <HStack>
        <Box as={FiSettings} color={ACCENT_COLOR} size="24px" />
        <Heading size="lg" color={ACCENT_COLOR}>Compliance & Analysis Preferences</Heading>
      </HStack>
      
      <FormControl isInvalid={errors.preferred_methodologies}>
        <FormLabel>Preferred Compliance Frameworks</FormLabel>
        <Text fontSize="sm" color="gray.600" mb={3}>
          Select the frameworks that apply to your organization
        </Text>
        <CheckboxGroup
          value={organizationData.preferred_methodologies}
          onChange={(values) => handleInputChange('preferred_methodologies', values)}
        >
          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={3}>
            {templateData.compliance_frameworks.map((framework) => (
              <Checkbox 
                key={framework.value} 
                value={framework.value}
                sx={{
                  '& .chakra-checkbox__control[data-checked]': {
                    bg: ACCENT_COLOR,
                    borderColor: ACCENT_COLOR,
                  }
                }}
              >
                <VStack align="start" spacing={1}>
                  <Text fontWeight="medium">{framework.label}</Text>
                  <Text fontSize="sm" color="gray.600">{framework.description}</Text>
                </VStack>
              </Checkbox>
            ))}
          </SimpleGrid>
        </CheckboxGroup>
        <FormErrorMessage>{errors.preferred_methodologies}</FormErrorMessage>
      </FormControl>

      <FormControl>
        <FormLabel>Analysis Preferences</FormLabel>
        <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4}>
          <FormControl>
            <FormLabel fontSize="sm">Detail Level</FormLabel>
            <Select
              value={organizationData.analysis_preferences.detail_level}
              onChange={(e) => handleNestedInputChange('analysis_preferences', 'detail_level', e.target.value)}
              size="sm"
              focusBorderColor={ACCENT_COLOR}
            >
              <option value="summary">Summary</option>
              <option value="detailed">Detailed</option>
              <option value="comprehensive">Comprehensive</option>
            </Select>
          </FormControl>

          <FormControl>
            <FormLabel fontSize="sm">Reporting Frequency</FormLabel>
            <Select
              value={organizationData.analysis_preferences.reporting_frequency}
              onChange={(e) => handleNestedInputChange('analysis_preferences', 'reporting_frequency', e.target.value)}
              size="sm"
              focusBorderColor={ACCENT_COLOR}
            >
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
              <option value="quarterly">Quarterly</option>
              <option value="annually">Annually</option>
            </Select>
          </FormControl>

          <FormControl>
            <FormLabel fontSize="sm">Focus Areas</FormLabel>
            <CheckboxGroup 
              value={organizationData.analysis_preferences.focus_areas || []} 
              onChange={(values) => handleInputChange('analysis_preferences', { ...organizationData.analysis_preferences, focus_areas: values })}
            >
              <HStack spacing={6} wrap="wrap">
                <Checkbox 
                  value="security" 
                  size="sm"
                  sx={{
                    '& .chakra-checkbox__control[data-checked]': {
                      bg: ACCENT_COLOR,
                      borderColor: ACCENT_COLOR,
                    }
                  }}
                >
                  Security
                </Checkbox>
                <Checkbox 
                  value="compliance" 
                  size="sm"
                  sx={{
                    '& .chakra-checkbox__control[data-checked]': {
                      bg: ACCENT_COLOR,
                      borderColor: ACCENT_COLOR,
                    }
                  }}
                >
                  Compliance
                </Checkbox>
                <Checkbox 
                  value="risk" 
                  size="sm"
                  sx={{
                    '& .chakra-checkbox__control[data-checked]': {
                      bg: ACCENT_COLOR,
                      borderColor: ACCENT_COLOR,
                    }
                  }}
                >
                  Risk Management
                </Checkbox>
                <Checkbox 
                  value="governance" 
                  size="sm"
                  sx={{
                    '& .chakra-checkbox__control[data-checked]': {
                      bg: ACCENT_COLOR,
                      borderColor: ACCENT_COLOR,
                    }
                  }}
                >
                  Governance
                </Checkbox>
              </HStack>
            </CheckboxGroup>
          </FormControl>
        </SimpleGrid>
      </FormControl>

      <Alert status="info" borderLeft="4px" borderLeftColor={ACCENT_COLOR}>
        <AlertIcon color={ACCENT_COLOR} />
        <Box>
          <AlertTitle>Ready to Complete!</AlertTitle>
          <AlertDescription>
            Your organization profile will be created with the selected configurations. 
            You can modify these settings later in the organization management section.
          </AlertDescription>
        </Box>
      </Alert>
    </VStack>
  );

  const renderCurrentStep = () => {
    switch (currentStep) {
      case 1:
        return renderBasicInformation();
      case 2:
        return renderOperationalContext();
      case 3:
        return renderRiskGovernance();
      case 4:
        return renderCompliancePreferences();
      default:
        return renderBasicInformation();
    }
  };

  // Load templates on component mount
  useEffect(() => {
    console.log('useEffect triggered - loading templates');
    
    const loadTemplates = async () => {
      try {
        console.log('Fetching organization templates...');
        const templatesData = await getOrganizationTemplates();
        console.log('Templates loaded successfully:', templatesData);
        setTemplates(templatesData);
      } catch (error) {
        console.error('Error loading templates:', error);
        toast({
          title: 'Error',
          description: 'Failed to load organization templates',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      }
    };

    loadTemplates();
  }, [toast]);

  return (
    <Box p={8} maxW="6xl" mx="auto">
      <VStack spacing={8} align="stretch">
        <Box textAlign="center">
          <Heading size="xl" mb={2}>
            {isEditMode ? 'Edit Organization Configuration' : 'Organization Configuration'}
          </Heading>
          <Text color="gray.600" fontSize="lg">
            {isEditMode 
              ? 'Update your organization profile and preferences'
              : 'Set up your organization profile for personalized GRC analysis'
            }
          </Text>
        </Box>

        <Card bg={cardBg} shadow="lg">
          <CardHeader>
            {renderStepIndicator()}
          </CardHeader>
          
          <CardBody>
            <Box minH="500px">
              {renderCurrentStep()}
            </Box>
            
            <Divider my={6} />
            
            <HStack justify="space-between">
              <Button
                leftIcon={<FiArrowLeft />}
                onClick={prevStep}
                isDisabled={currentStep === 1}
                variant="outline"
                borderColor={ACCENT_COLOR}
                color={ACCENT_COLOR}
                _hover={{ bg: ACCENT_COLOR, color: 'white' }}
              >
                Previous
              </Button>

              {currentStep < 4 ? (
                <Button
                  rightIcon={<FiArrowRight />}
                  onClick={nextStep}
                  bg={ACCENT_COLOR}
                  color="white"
                  _hover={{ bg: '#3311a0' }}
                >
                  Next
                </Button>
              ) : (
                <Button
                  rightIcon={<FiCheck />}
                  onClick={handleSubmit}
                  bg={ACCENT_COLOR}
                  color="white"
                  _hover={{ bg: '#3311a0' }}
                  isLoading={isLoading}
                  loadingText={isEditMode ? "Updating..." : "Setting up..."}
                >
                  {isEditMode ? "Update Profile" : "Complete Setup"}
                </Button>
              )}
            </HStack>
          </CardBody>
        </Card>
      </VStack>
    </Box>
  );
};

export default OrganizationSetupPage; 