import React from 'react';
import { Card, CardContent } from '../../components/ui/Card';
import { ArrowUpIcon, ArrowDownIcon } from '@heroicons/react/20/solid';

export const StatCard = ({ title, amount, percentageChange, isPositive, icon: Icon }) => {
  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-neutral-600">
            {title}
          </span>
          <span className={`p-2 rounded-lg ${isPositive ? 'bg-success-50 text-success-600' : 'bg-error-50 text-error-600'}`}>
            <Icon className="w-5 h-5" />
          </span>
        </div>
        <div className="text-3xl font-semibold font-mono text-neutral-900">
          {amount}
        </div>
        <div className={`mt-2 text-sm flex items-center gap-1 ${isPositive ? 'text-success-600' : 'text-error-600'}`}>
          {isPositive ? <ArrowUpIcon className="w-4 h-4" /> : <ArrowDownIcon className="w-4 h-4" />}
          <span>{Math.abs(percentageChange)}% from last month</span>
        </div>
      </CardContent>
    </Card>
  );
};
