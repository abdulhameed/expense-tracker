import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';

const data = [
  { month: 'Jan', income: 4000, expenses: 2400 },
  { month: 'Feb', income: 3000, expenses: 1398 },
  { month: 'Mar', income: 2000, expenses: 9800 },
  { month: 'Apr', income: 2780, expenses: 3908 },
  { month: 'May', income: 1890, expenses: 4800 },
  { month: 'Jun', income: 2390, expenses: 3800 },
  { month: 'Jul', income: 3490, expenses: 4300 },
];

export const SpendingChart = () => {
  return (
    <Card className="h-full flex flex-col min-h-[400px]">
      <CardHeader>
        <CardTitle>Income vs Expenses</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 min-h-0">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis dataKey="month" stroke="#6B7280" style={{ fontSize: '12px' }} />
            <YAxis stroke="#6B7280" style={{ fontSize: '12px' }} />
            <Tooltip 
              contentStyle={{
                backgroundColor: '#FFFFFF',
                border: '1px solid #E5E7EB',
                borderRadius: '8px',
                padding: '12px'
              }}
            />
            <Legend />
            <Line type="monotone" dataKey="income" stroke="#10B981" strokeWidth={2} dot={{ fill: '#10B981', r: 4 }} />
            <Line type="monotone" dataKey="expenses" stroke="#EF4444" strokeWidth={2} dot={{ fill: '#EF4444', r: 4 }} />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};
