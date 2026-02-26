import React from 'react';
import { Box, Flex, Text } from '@chakra-ui/react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import WidgetContainer from './WidgetContainer';

// Mock data for compliance by category
const MOCK_DATA = [
  { name: 'GDPR', value: 85, color: '#4415b6' },
  { name: 'PCI DSS', value: 76, color: '#6236de' },
  { name: 'HIPAA', value: 92, color: '#9475ff' },
  { name: 'SOC 2', value: 65, color: '#c4b1ff' },
];

const RADIAN = Math.PI / 180;
const renderCustomizedLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent, index }) => {
  const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
  const x = cx + radius * Math.cos(-midAngle * RADIAN);
  const y = cy + radius * Math.sin(-midAngle * RADIAN);

  return (
    <text x={x} y={y} fill="white" textAnchor={x > cx ? 'start' : 'end'} dominantBaseline="central">
      {`${(percent * 100).toFixed(0)}%`}
    </text>
  );
};

const ComplianceDonutChart = () => {
  return (
    <WidgetContainer 
      title="Compliance by Framework" 
      description="Current compliance status across regulatory frameworks"
    >
      <Box height="300px" width="100%">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={MOCK_DATA}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={renderCustomizedLabel}
              outerRadius={100}
              innerRadius={60}
              fill="#8884d8"
              dataKey="value"
            >
              {MOCK_DATA.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip 
              formatter={(value) => [`${value}%`, 'Compliance Score']}
            />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </Box>
    </WidgetContainer>
  );
};

export default ComplianceDonutChart; 