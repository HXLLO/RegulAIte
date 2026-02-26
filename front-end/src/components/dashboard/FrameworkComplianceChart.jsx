import React from 'react';
import { Box } from '@chakra-ui/react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import WidgetContainer from './WidgetContainer';

// Mock data for framework compliance comparison
const MOCK_DATA = [
  { name: 'GDPR', compliant: 85, nonCompliant: 15 },
  { name: 'PCI DSS', compliant: 76, nonCompliant: 24 },
  { name: 'HIPAA', compliant: 92, nonCompliant: 8 },
  { name: 'SOC 2', compliant: 65, nonCompliant: 35 },
  { name: 'ISO 27001', compliant: 78, nonCompliant: 22 },
];

const FrameworkComplianceChart = () => {
  return (
    <WidgetContainer 
      title="Framework Compliance Status" 
      description="Compliance status across different regulatory frameworks"
    >
      <Box height="300px" width="100%">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={MOCK_DATA}
            margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar 
              dataKey="compliant" 
              name="Compliant" 
              fill="#4415b6" 
              stackId="a" 
              radius={[4, 4, 0, 0]}
            />
            <Bar 
              dataKey="nonCompliant" 
              name="Non-Compliant" 
              fill="#DC2626" 
              stackId="a" 
              radius={[4, 4, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </Box>
    </WidgetContainer>
  );
};

export default FrameworkComplianceChart; 