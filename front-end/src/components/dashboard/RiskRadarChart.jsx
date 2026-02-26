import React from 'react';
import { Box } from '@chakra-ui/react';
import { 
  RadarChart, 
  PolarGrid, 
  PolarAngleAxis, 
  PolarRadiusAxis, 
  Radar, 
  Legend, 
  ResponsiveContainer,
  Tooltip 
} from 'recharts';
import WidgetContainer from './WidgetContainer';

// Mock data for the risk radar chart
const MOCK_DATA = [
  { category: 'Access Control', current: 65, target: 90 },
  { category: 'Data Protection', current: 78, target: 95 },
  { category: 'Network Security', current: 80, target: 85 },
  { category: 'Incident Response', current: 55, target: 80 },
  { category: 'Vendor Management', current: 60, target: 75 },
  { category: 'Physical Security', current: 70, target: 80 },
];

const RiskRadarChart = () => {
  return (
    <WidgetContainer 
      title="Risk Assessment Radar" 
      description="Current vs target risk assessment by category"
    >
      <Box height="300px" width="100%">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart cx="50%" cy="50%" outerRadius="70%" data={MOCK_DATA}>
            <PolarGrid />
            <PolarAngleAxis dataKey="category" />
            <PolarRadiusAxis angle={30} domain={[0, 100]} />
            <Radar 
              name="Current Score" 
              dataKey="current" 
              stroke="#4415b6" 
              fill="#4415b6" 
              fillOpacity={0.4}
            />
            <Radar 
              name="Target Score" 
              dataKey="target" 
              stroke="#10B981" 
              fill="#10B981" 
              fillOpacity={0.2}
            />
            <Tooltip formatter={(value) => `${value}%`} />
            <Legend />
          </RadarChart>
        </ResponsiveContainer>
      </Box>
    </WidgetContainer>
  );
};

export default RiskRadarChart; 