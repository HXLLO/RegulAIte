import React from 'react';
import { 
  Box, 
  List, 
  ListItem, 
  Flex, 
  Text, 
  Badge,
  Icon
} from '@chakra-ui/react';
import { 
  FiAlertCircle, 
  FiInfo, 
  FiCheckCircle,
  FiClock
} from 'react-icons/fi';
import WidgetContainer from './WidgetContainer';

// Mock data for recent alerts
const MOCK_ALERTS = [
  {
    id: 1,
    title: 'PCI DSS Compliance Alert',
    description: '3 controls need review before the deadline',
    status: 'warning',
    time: '2 hours ago',
  },
  {
    id: 2,
    title: 'GDPR Data Processing',
    description: 'New data processing activity detected',
    status: 'info',
    time: '5 hours ago',
  },
  {
    id: 3,
    title: 'SOC 2 Audit Preparation',
    description: 'All controls reviewed successfully',
    status: 'success',
    time: '1 day ago',
  },
  {
    id: 4,
    title: 'Risk Assessment Update',
    description: 'Quarterly risk assessment due in 5 days',
    status: 'warning',
    time: '2 days ago',
  },
  {
    id: 5,
    title: 'ISO 27001 Certification',
    description: 'New evidence required for compliance',
    status: 'info',
    time: '3 days ago',
  }
];

// Status icon mapping
const statusIconMap = {
  warning: FiAlertCircle,
  info: FiInfo,
  success: FiCheckCircle
};

// Status color mapping
const statusColorMap = {
  warning: 'orange',
  info: 'blue',
  success: 'green'
};

const RecentAlertsWidget = () => {
  return (
    <WidgetContainer 
      title="Recent Alerts" 
      description="Latest compliance and risk notifications"
    >
      <List spacing={3}>
        {MOCK_ALERTS.map(alert => (
          <ListItem key={alert.id} py={2} borderBottom="1px solid" borderColor="gray.100">
            <Flex alignItems="flex-start">
              <Icon 
                as={statusIconMap[alert.status]} 
                color={`${statusColorMap[alert.status]}.500`}
                boxSize={5}
                mr={3}
                mt={1}
              />
              <Box flex="1">
                <Flex justify="space-between" align="center" mb={1}>
                  <Text fontWeight="bold">{alert.title}</Text>
                  <Badge colorScheme={statusColorMap[alert.status]}>
                    {alert.status}
                  </Badge>
                </Flex>
                <Text fontSize="sm" color="gray.600">{alert.description}</Text>
                <Flex align="center" mt={1}>
                  <Icon as={FiClock} color="gray.400" boxSize={3} mr={1} />
                  <Text fontSize="xs" color="gray.400">{alert.time}</Text>
                </Flex>
              </Box>
            </Flex>
          </ListItem>
        ))}
      </List>
    </WidgetContainer>
  );
};

export default RecentAlertsWidget; 