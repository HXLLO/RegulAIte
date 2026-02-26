import React from 'react';
import { 
  Box, 
  Card, 
  CardHeader, 
  CardBody, 
  CardFooter,
  Heading, 
  Text,
  useColorModeValue
} from '@chakra-ui/react';

/**
 * A reusable container for dashboard widgets
 */
const WidgetContainer = ({ 
  title, 
  description, 
  children, 
  footer, 
  minHeight = '300px', 
  maxHeight = null,
  width = '100%',
  ...props 
}) => {
  const cardBg = useColorModeValue('white', 'gray.700');
  const accentColor = '#4415b6';

  return (
    <Card 
      bg={cardBg} 
      boxShadow="md" 
      borderRadius="lg" 
      minH={minHeight}
      maxH={maxHeight}
      width={width}
      {...props}
    >
      <CardHeader pb={2}>
        <Heading size="md">{title}</Heading>
        {description && (
          <Text fontSize="sm" color="gray.500" mt={1}>
            {description}
          </Text>
        )}
      </CardHeader>
      <CardBody pt={2}>
        {children}
      </CardBody>
      {footer && (
        <CardFooter>
          {footer}
        </CardFooter>
      )}
    </Card>
  );
};

export default WidgetContainer; 