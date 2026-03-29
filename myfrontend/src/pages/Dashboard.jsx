import React from 'react';
import { StatCard } from '../features/dashboard/StatCard';
import { SpendingChart } from '../features/dashboard/SpendingChart';
import { BanknotesIcon, ArrowTrendingUpIcon, ArrowTrendingDownIcon, CreditCardIcon } from '@heroicons/react/24/outline';

export default function Dashboard() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-neutral-900">Dashboard</h1>
        <p className="text-neutral-700 mt-1">Your financial overview</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
        <StatCard 
          title="Total Balance" 
          amount="$24,562.00" 
          percentageChange={4.5} 
          isPositive={true} 
          icon={BanknotesIcon} 
        />
        <StatCard 
          title="Total Income" 
          amount="$8,240.50" 
          percentageChange={12.5} 
          isPositive={true} 
          icon={ArrowTrendingUpIcon} 
        />
        <StatCard 
          title="Total Expenses" 
          amount="$3,450.20" 
          percentageChange={-2.4} 
          isPositive={false} 
          icon={ArrowTrendingDownIcon} 
        />
        <StatCard 
          title="Active Subscriptions" 
          amount="$245.00" 
          percentageChange={1.2} 
          isPositive={false} 
          icon={CreditCardIcon} 
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <SpendingChart />
        </div>
        <div className="lg:col-span-1">
          <div className="bg-white rounded-xl border border-neutral-200 p-6 h-full shadow-sm hover:shadow-md transition-shadow">
             <h3 className="text-lg font-semibold text-neutral-900 mb-4">Recent Transactions</h3>
             <div className="space-y-4">
               {[1, 2, 3, 4].map((i) => (
                 <div key={i} className="flex justify-between items-center py-2 border-b border-neutral-100 last:border-0 hover:bg-neutral-50 rounded-lg -mx-2 px-2 transition-colors cursor-pointer">
                   <div>
                     <div className="font-medium text-neutral-900">Office Supplies</div>
                     <div className="text-xs text-neutral-500">Mar 12, 2026</div>
                   </div>
                   <div className="font-mono font-semibold text-error-600">-$45.99</div>
                 </div>
               ))}
             </div>
          </div>
        </div>
      </div>
    </div>
  );
}
