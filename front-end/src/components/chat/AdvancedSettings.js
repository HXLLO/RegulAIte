import React, { useState, useEffect } from 'react';
import { 
  Box, 
  VStack, 
  HStack, 
  Text, 
  Button, 
  Drawer,
  DrawerBody,
  DrawerFooter,
  DrawerHeader,
  DrawerOverlay,
  DrawerContent,
  DrawerCloseButton,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  useColorModeValue
} from '@chakra-ui/react';

import AgentSelector from './AgentSelector';
import ModelParamsSelector from './ModelParamsSelector';

/**
 * Advanced settings component for autonomous agent and LLM parameters
 */
const AdvancedSettings = ({ isOpen, onClose, onSettingsChange, initialSettings = {} }) => {
  // Default settings - agents always enabled
  const defaultSettings = {
    agent: {
      use_agent: true  // Always true, no user control
    },
    llm: {
      model: 'gpt-4',
      temperature: 0.7,
      max_tokens: 2048,
      top_p: 1.0,
      frequency_penalty: 0.0,
      presence_penalty: 0.0
    }
  };
  
  // Local state - only LLM settings are configurable
  const [llmSettings, setLlmSettings] = useState({...defaultSettings.llm});
  
  // Colors
  const accentColor = '#4415b6';
  const secondaryText = useColorModeValue('gray.600', 'gray.400');

  // Initialize settings when drawer opens
  useEffect(() => {
    if (isOpen) {
      // Initialize LLM settings from props, with fallbacks
      setLlmSettings({
        ...defaultSettings.llm,
        ...(initialSettings.llm || {})
      });
    }
  }, [isOpen, initialSettings]);
  
  // Handle Apply button click
  const handleApply = () => {
    // Create a new combined settings object with agents always enabled
    const newSettings = {
      agent: { use_agent: true },  // Always enabled
      llm: llmSettings
    };
    
    // Send it to the parent component
    onSettingsChange(newSettings);
    
    // Close the drawer
    onClose();
  };

  // Handle Reset button click
  const handleReset = () => {
    // Reset LLM settings to defaults, keep agents enabled
    setLlmSettings({...defaultSettings.llm});
    
    // Apply the defaults with agents always enabled
    onSettingsChange({
      agent: { use_agent: true },  // Always enabled
      llm: {...defaultSettings.llm}
    });
    
    // Close the drawer
    onClose();
  };
  
  // Model parameters only update local state
  const handleParamsChange = (newLlmParams) => {
    setLlmSettings(newLlmParams);
  };

  return (
    <Drawer 
      isOpen={isOpen} 
      placement="right" 
      onClose={onClose} 
      size="md"
    >
      <DrawerOverlay />
      <DrawerContent>
        <DrawerCloseButton />
        <DrawerHeader borderBottomWidth="1px">
          <Text color={accentColor}>Advanced Settings</Text>
          <Text fontSize="sm" fontWeight="normal" color={secondaryText}>
            Configure autonomous AI agent and model parameters
          </Text>
        </DrawerHeader>

        <DrawerBody>
          <Tabs colorScheme="purple" variant="enclosed">
            <TabList>
              <Tab>Agent Status</Tab>
              <Tab>Model Parameters</Tab>
            </TabList>
            
            <TabPanels>
              {/* Agent Status Tab - Informational Only */}
              <TabPanel p={3}>
                <AgentSelector />
                <Text fontSize="xs" color={secondaryText} mt={3} fontStyle="italic">
                  Agents are always enabled to provide the best possible responses.
                </Text>
              </TabPanel>
              
              {/* Model Parameters Tab */}
              <TabPanel p={3}>
                <ModelParamsSelector 
                  onParamsChange={handleParamsChange} 
                  initialParams={llmSettings} 
                />
              </TabPanel>
            </TabPanels>
          </Tabs>
        </DrawerBody>

        <DrawerFooter borderTopWidth="1px">
          <HStack spacing={4}>
            <Button 
              variant="outline" 
              mr={3} 
              onClick={handleReset}
              size="sm"
            >
              Reset to Default
            </Button>
            <Button 
              colorScheme="purple" 
              onClick={handleApply}
              size="sm"
              bg={accentColor}
              _hover={{ bg: '#3a1296' }}
            >
              Apply
            </Button>
          </HStack>
        </DrawerFooter>
      </DrawerContent>
    </Drawer>
  );
};

export default AdvancedSettings; 