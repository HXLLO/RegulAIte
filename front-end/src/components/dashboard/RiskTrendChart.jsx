import React from 'react';
import { Box } from '@chakra-ui/react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import WidgetContainer from './WidgetContainer';

// Mock data for risk trends over time
const MOCK_DATA = [
  { name: 'Jan', high: 10, medium: 25, low: 40 },
  { name: 'Feb', high: 8, medium: 22, low: 38 },
  { name: 'Mar', high: 12, medium: 24, low: 35 },
  { name: 'Apr', high: 15, medium: 28, low: 32 },
  { name: 'May', high: 9, medium: 20, low: 30 },
  { name: 'Jun', high: 7, medium: 18, low: 28 },
];

const RiskTrendChart = () => {
  return (
    <WidgetContainer 
      title="Risk Trend Analysis" 
      description="6-month risk level distribution trend"
    >
      <Box height="300px" width="100%">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={MOCK_DATA}
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="high" 
              stroke="#DC2626" 
              activeDot={{ r: 8 }} 
              strokeWidth={2}
              name="High Risk"
            />
            <Line 
              type="monotone" 
              dataKey="medium" 
              stroke="#F59E0B" 
              strokeWidth={2}
              name="Medium Risk"
            />
            <Line 
              type="monotone" 
              dataKey="low" 
              stroke="#4415b6" 
              strokeWidth={2}
              name="Low Risk"
            />
          </LineChart>
        </ResponsiveContainer>
      </Box>
    </WidgetContainer>
  );
};

export default RiskTrendChart; 