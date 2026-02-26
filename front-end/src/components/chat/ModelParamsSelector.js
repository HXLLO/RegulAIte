import React, { useState, useEffect, useRef } from 'react';
import { 
  Box, 
  FormControl, 
  FormLabel, 
  Select, 
  Slider,
  SliderTrack,
  SliderFilledTrack,
  SliderThumb,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberDecrementStepper,
  NumberIncrementStepper,
  Tooltip,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
  HStack,
  Text,
  VStack,
  useColorModeValue
} from '@chakra-ui/react';
import { InfoIcon } from '@chakra-ui/icons';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8090';

/**
 * Component for selecting and configuring LLM parameters
 */
const ModelParamsSelector = ({ onParamsChange, initialParams = {} }) => {
  // Color mode values
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const inputBgColor = useColorModeValue('white', 'gray.700');
  const labelColor = useColorModeValue('gray.700', 'gray.300');
  const textColor = useColorModeValue('gray.800', 'gray.100');
  const loadingTextColor = useColorModeValue('gray.600', 'gray.300');
  const errorBgColor = useColorModeValue('red.50', 'red.900');
  const errorTextColor = useColorModeValue('red.600', 'red.200');

  const [config, setConfig] = useState(null);
  const [params, setParams] = useState({
    model: initialParams.model || 'gpt-4',
    temperature: initialParams.temperature !== undefined ? initialParams.temperature : 0.7,
    max_tokens: initialParams.max_tokens || 2048,
    top_p: initialParams.top_p !== undefined ? initialParams.top_p : 1.0,
    frequency_penalty: initialParams.frequency_penalty !== undefined ? initialParams.frequency_penalty : 0.0,
    presence_penalty: initialParams.presence_penalty !== undefined ? initialParams.presence_penalty : 0.0
  });
  
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const isInitialLoadRef = useRef(true);

  // Fetch available models and default parameters - only runs once
  useEffect(() => {
    // Skip API call if we've already loaded the config
    if (!isInitialLoadRef.current) {
      return;
    }
    
    const controller = new AbortController();
    const fetchConfig = async () => {
      setIsLoading(true);
      try {
        const response = await axios.get(`${API_URL}/config`, {
          signal: controller.signal
        });
        setConfig(response.data);
        
        // Update with defaults from config if available
        if (response.data && response.data.llm) {
          setParams(prev => ({
            model: initialParams.model || response.data.llm.model,
            temperature: initialParams.temperature !== undefined ? initialParams.temperature : response.data.llm.temperature,
            max_tokens: initialParams.max_tokens || response.data.llm.max_tokens,
            top_p: initialParams.top_p !== undefined ? initialParams.top_p : response.data.llm.top_p,
            frequency_penalty: initialParams.frequency_penalty !== undefined ? initialParams.frequency_penalty : response.data.llm.frequency_penalty,
            presence_penalty: initialParams.presence_penalty !== undefined ? initialParams.presence_penalty : response.data.llm.presence_penalty
          }));
        }
        
        setError(null);
        isInitialLoadRef.current = false;
      } catch (err) {
        if (!axios.isCancel(err)) {
          console.error('Error fetching config:', err);
          setError('Failed to load model configuration.');
        }
      } finally {
        setIsLoading(false);
      }
    };

    fetchConfig();
    
    // Cleanup function to abort fetch on unmount
    return () => {
      controller.abort();
    };
  // We're deliberately using an empty dependency array with a ref check to ensure this only runs once
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Handle updates to initialParams without triggering API calls
  useEffect(() => {
    // Skip if it's the initial render - that's handled by the first useEffect
    if (isInitialLoadRef.current) {
      return;
    }
    
    // Update params when initialParams change
    const updatedParams = {
      model: initialParams.model || params.model,
      temperature: initialParams.temperature !== undefined ? initialParams.temperature : params.temperature,
      max_tokens: initialParams.max_tokens || params.max_tokens,
      top_p: initialParams.top_p !== undefined ? initialParams.top_p : params.top_p,
      frequency_penalty: initialParams.frequency_penalty !== undefined ? initialParams.frequency_penalty : params.frequency_penalty,
      presence_penalty: initialParams.presence_penalty !== undefined ? initialParams.presence_penalty : params.presence_penalty
    };
    
    // Only update if there are actual changes
    if (JSON.stringify(updatedParams) !== JSON.stringify(params)) {
      setParams(updatedParams);
    }
  // Remove params from the dependency array to prevent infinite loops
  }, [initialParams]);

  // Notify parent when params change
  useEffect(() => {
    onParamsChange(params);
  }, [params, onParamsChange]);

  // Handle parameter change
  const handleParamChange = (param, value) => {
    setParams(prev => ({
      ...prev,
      [param]: value
    }));
  };

  // Available models - fallback if config not available
  const availableModels = [
    { id: 'gpt-4', name: 'GPT-4' },
    { id: 'gpt-4-turbo', name: 'GPT-4 Turbo' },
    { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo' },
    { id: 'claude-3-opus', name: 'Claude 3 Opus' },
    { id: 'claude-3-sonnet', name: 'Claude 3 Sonnet' },
    { id: 'claude-3-haiku', name: 'Claude 3 Haiku' }
  ];

  if (isLoading) {
    return (
      <Box p={2} opacity={0.7}>
        <Text fontSize="sm" color={loadingTextColor}>Loading model parameters...</Text>
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={3} borderWidth="1px" borderRadius="md" borderColor="red.300" bg={errorBgColor}>
        <Text fontSize="sm" color={errorTextColor}>
          {error} Using default parameters.
        </Text>
      </Box>
    );
  }

  return (
    <Box 
      borderWidth="1px" 
      borderRadius="md" 
      p={3} 
      bg={bgColor} 
      shadow="sm"
      borderColor={borderColor}
    >
      <Accordion allowToggle defaultIndex={[0]}>
        <AccordionItem border="none">
          <AccordionButton px={0} _hover={{ bg: 'transparent' }}>
            <Box flex="1" textAlign="left">
              <Text fontWeight="medium" fontSize="sm" color={textColor}>LLM Parameters</Text>
            </Box>
            <AccordionIcon />
          </AccordionButton>
          
          <AccordionPanel pb={4} px={0}>
            <VStack spacing={4} align="stretch">
              {/* Model Selection */}
              <FormControl>
                <FormLabel htmlFor="model-select" fontSize="sm" mb={1} color={labelColor}>
                  Model
                </FormLabel>
                <Select
                  id="model-select"
                  value={params.model}
                  onChange={(e) => handleParamChange('model', e.target.value)}
                  size="sm"
                  bg={inputBgColor}
                  borderColor={borderColor}
                >
                  {availableModels.map(model => (
                    <option key={model.id} value={model.id}>
                      {model.name}
                    </option>
                  ))}
                </Select>
              </FormControl>
              
              {/* Temperature */}
              <FormControl>
                <HStack justify="space-between" mb={1}>
                  <FormLabel htmlFor="temperature-slider" fontSize="sm" mb={0} color={labelColor}>
                    Temperature
                  </FormLabel>
                  <Tooltip label="Controls randomness: lower values are more focused, higher values are more creative" placement="top">
                    <InfoIcon boxSize={3} color="gray.500" />
                  </Tooltip>
                </HStack>
                <HStack spacing={4}>
                  <Slider
                    id="temperature-slider"
                    min={0}
                    max={2}
                    step={0.1}
                    value={params.temperature}
                    onChange={(value) => handleParamChange('temperature', value)}
                    colorScheme="purple"
                    flex="1"
                  >
                    <SliderTrack>
                      <SliderFilledTrack bg="#4415b6" />
                    </SliderTrack>
                    <SliderThumb />
                  </Slider>
                  <NumberInput
                    value={params.temperature}
                    onChange={(valueString) => {
                      const value = parseFloat(valueString);
                      if (!isNaN(value)) {
                        handleParamChange('temperature', Math.max(0, Math.min(2, value)));
                      }
                    }}
                    step={0.1}
                    min={0}
                    max={2}
                    size="xs"
                    maxW="60px"
                    bg={inputBgColor}
                    borderColor={borderColor}
                  >
                    <NumberInputField />
                    <NumberInputStepper>
                      <NumberIncrementStepper />
                      <NumberDecrementStepper />
                    </NumberInputStepper>
                  </NumberInput>
                </HStack>
              </FormControl>
              
              {/* Max Tokens */}
              <FormControl>
                <HStack justify="space-between" mb={1}>
                  <FormLabel htmlFor="max-tokens-input" fontSize="sm" mb={0} color={labelColor}>
                    Max Tokens
                  </FormLabel>
                  <Tooltip label="Maximum number of tokens (words/characters) in the response" placement="top">
                    <InfoIcon boxSize={3} color="gray.500" />
                  </Tooltip>
                </HStack>
                <NumberInput
                  id="max-tokens-input"
                  value={params.max_tokens}
                  onChange={(valueString) => {
                    const value = parseInt(valueString);
                    if (!isNaN(value)) {
                      handleParamChange('max_tokens', Math.max(1, Math.min(8192, value)));
                    }
                  }}
                  min={1}
                  max={8192}
                  step={1}
                  size="sm"
                  bg={inputBgColor}
                  borderColor={borderColor}
                >
                  <NumberInputField />
                  <NumberInputStepper>
                    <NumberIncrementStepper />
                    <NumberDecrementStepper />
                  </NumberInputStepper>
                </NumberInput>
              </FormControl>
              
              {/* Top P */}
              <FormControl>
                <HStack justify="space-between" mb={1}>
                  <FormLabel htmlFor="top-p-slider" fontSize="sm" mb={0} color={labelColor}>
                    Top P
                  </FormLabel>
                  <Tooltip label="Controls diversity: 0.1 means only consider tokens with the top 10% probability" placement="top">
                    <InfoIcon boxSize={3} color="gray.500" />
                  </Tooltip>
                </HStack>
                <HStack spacing={4}>
                  <Slider
                    id="top-p-slider"
                    min={0.1}
                    max={1}
                    step={0.05}
                    value={params.top_p}
                    onChange={(value) => handleParamChange('top_p', value)}
                    colorScheme="purple"
                    flex="1"
                  >
                    <SliderTrack>
                      <SliderFilledTrack bg="#4415b6" />
                    </SliderTrack>
                    <SliderThumb />
                  </Slider>
                  <NumberInput
                    value={params.top_p}
                    onChange={(valueString) => {
                      const value = parseFloat(valueString);
                      if (!isNaN(value)) {
                        handleParamChange('top_p', Math.max(0.1, Math.min(1, value)));
                      }
                    }}
                    step={0.05}
                    min={0.1}
                    max={1}
                    size="xs"
                    maxW="60px"
                    bg={inputBgColor}
                    borderColor={borderColor}
                  >
                    <NumberInputField />
                    <NumberInputStepper>
                      <NumberIncrementStepper />
                      <NumberDecrementStepper />
                    </NumberInputStepper>
                  </NumberInput>
                </HStack>
              </FormControl>
              
              {/* Frequency Penalty */}
              <FormControl>
                <HStack justify="space-between" mb={1}>
                  <FormLabel htmlFor="freq-penalty-slider" fontSize="sm" mb={0} color={labelColor}>
                    Frequency Penalty
                  </FormLabel>
                  <Tooltip label="Reduces repetition by penalizing tokens that have already appeared" placement="top">
                    <InfoIcon boxSize={3} color="gray.500" />
                  </Tooltip>
                </HStack>
                <HStack spacing={4}>
                  <Slider
                    id="freq-penalty-slider"
                    min={0}
                    max={2}
                    step={0.1}
                    value={params.frequency_penalty}
                    onChange={(value) => handleParamChange('frequency_penalty', value)}
                    colorScheme="purple"
                    flex="1"
                  >
                    <SliderTrack>
                      <SliderFilledTrack bg="#4415b6" />
                    </SliderTrack>
                    <SliderThumb />
                  </Slider>
                  <NumberInput
                    value={params.frequency_penalty}
                    onChange={(valueString) => {
                      const value = parseFloat(valueString);
                      if (!isNaN(value)) {
                        handleParamChange('frequency_penalty', Math.max(0, Math.min(2, value)));
                      }
                    }}
                    step={0.1}
                    min={0}
                    max={2}
                    size="xs"
                    maxW="60px"
                    bg={inputBgColor}
                    borderColor={borderColor}
                  >
                    <NumberInputField />
                    <NumberInputStepper>
                      <NumberIncrementStepper />
                      <NumberDecrementStepper />
                    </NumberInputStepper>
                  </NumberInput>
                </HStack>
              </FormControl>
              
              {/* Presence Penalty */}
              <FormControl>
                <HStack justify="space-between" mb={1}>
                  <FormLabel htmlFor="presence-penalty-slider" fontSize="sm" mb={0} color={labelColor}>
                    Presence Penalty
                  </FormLabel>
                  <Tooltip label="Encourages the model to talk about new topics" placement="top">
                    <InfoIcon boxSize={3} color="gray.500" />
                  </Tooltip>
                </HStack>
                <HStack spacing={4}>
                  <Slider
                    id="presence-penalty-slider"
                    min={0}
                    max={2}
                    step={0.1}
                    value={params.presence_penalty}
                    onChange={(value) => handleParamChange('presence_penalty', value)}
                    colorScheme="purple"
                    flex="1"
                  >
                    <SliderTrack>
                      <SliderFilledTrack bg="#4415b6" />
                    </SliderTrack>
                    <SliderThumb />
                  </Slider>
                  <NumberInput
                    value={params.presence_penalty}
                    onChange={(valueString) => {
                      const value = parseFloat(valueString);
                      if (!isNaN(value)) {
                        handleParamChange('presence_penalty', Math.max(0, Math.min(2, value)));
                      }
                    }}
                    step={0.1}
                    min={0}
                    max={2}
                    size="xs"
                    maxW="60px"
                    bg={inputBgColor}
                    borderColor={borderColor}
                  >
                    <NumberInputField />
                    <NumberInputStepper>
                      <NumberIncrementStepper />
                      <NumberDecrementStepper />
                    </NumberInputStepper>
                  </NumberInput>
                </HStack>
              </FormControl>
            </VStack>
          </AccordionPanel>
        </AccordionItem>
      </Accordion>
    </Box>
  );
};

export default ModelParamsSelector; 