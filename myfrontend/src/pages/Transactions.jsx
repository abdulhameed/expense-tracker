import React, { useState } from 'react';
import { Button } from '../components/ui/Button';
import { CreateTransactionModal } from '../features/transactions/CreateTransactionModal';
import { 
  EllipsisVerticalIcon, 
  FunnelIcon,
  ShoppingBagIcon,
  BriefcaseIcon,
  BanknotesIcon,
  BoltIcon,
  MagnifyingGlassIcon,
  CalendarIcon
} from '@heroicons/react/24/outline';

const dummyData = [
  { id: 1, date: 'Mar 12, 2026', time: '10:45 AM', desc: 'Office Supplies', shortDesc: 'Printer paper and ink', category: 'Office', amount: -45.99, icon: BriefcaseIcon, variant: 'neutral' },
  { id: 2, date: 'Mar 11, 2026', time: '1:30 PM', desc: 'Client Lunch', shortDesc: 'Meeting with Acme Corp', category: 'Food', amount: -67.50, icon: ShoppingBagIcon, variant: 'warning' },
  { id: 3, date: 'Mar 10, 2026', time: '9:00 AM', desc: 'Monthly Salary', shortDesc: 'Direct Deposit', category: 'Income', amount: 5000.00, icon: BanknotesIcon, variant: 'success' },
  { id: 4, date: 'Mar 08, 2026', time: '4:15 PM', desc: 'Internet Bill', shortDesc: 'Monthly subscription', category: 'Utilities', amount: -80.00, icon: BoltIcon, variant: 'primary' },
];

const getCategoryStyles = (variant) => {
  switch(variant) {
    case 'success': return 'bg-success-50 text-success-700 border-success-200';
    case 'warning': return 'bg-warning-50 text-warning-700 border-warning-200';
    case 'primary': return 'bg-primary-50 text-primary-700 border-primary-200';
    default: return 'bg-neutral-50 text-neutral-700 border-neutral-200';
  }
};

const getIconStyles = (variant) => {
  switch(variant) {
    case 'success': return 'bg-success-100 text-success-600';
    case 'warning': return 'bg-warning-100 text-warning-600';
    case 'primary': return 'bg-primary-100 text-primary-600';
    default: return 'bg-neutral-100 text-neutral-600';
  }
};

export default function Transactions() {
  const [isModalOpen, setModalOpen] = useState(false);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-neutral-900">Transactions</h1>
          <p className="text-neutral-700 mt-1">Manage your income and expenses.</p>
        </div>
        <Button onClick={() => setModalOpen(true)}>+ New Transaction</Button>
      </div>

      <div className="bg-white rounded-xl border border-neutral-200 overflow-hidden shadow-sm hover:shadow-md transition-shadow">
        <div className="p-4 border-b border-neutral-200 flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white">
          <div className="flex flex-col sm:flex-row gap-3 flex-1">
            <div className="relative flex-1 max-w-sm">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400">
                <MagnifyingGlassIcon className="w-5 h-5" />
              </span>
              <input 
                type="text" 
                placeholder="Search transactions..." 
                className="w-full pl-10 pr-4 py-2 border border-neutral-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
            <select className="px-3 py-2 border border-neutral-300 rounded-lg text-sm text-neutral-700 bg-white focus:outline-none focus:ring-2 focus:ring-primary-500">
              <option>All Categories</option>
              <option>Food</option>
              <option>Office</option>
              <option>Income</option>
              <option>Utilities</option>
            </select>
            <Button variant="secondary" size="sm" className="flex items-center gap-2 w-full sm:w-auto py-2">
              <CalendarIcon className="w-4 h-4" />
              <span className="whitespace-nowrap">Date Range</span>
            </Button>
          </div>
          <div className="flex items-center justify-between md:justify-end gap-3 border-t border-neutral-100 pt-3 md:border-0 md:pt-0">
            <span className="text-sm text-neutral-500">{dummyData.length} records</span>
            <Button variant="secondary" size="sm" className="flex items-center gap-2 py-2">
              <FunnelIcon className="w-4 h-4" /> 
              More Filters
            </Button>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead className="bg-neutral-50 border-b border-neutral-200">
              <tr>
                <th className="px-6 py-3 text-xs font-semibold text-neutral-500 uppercase tracking-wider">Date</th>
                <th className="px-6 py-3 text-xs font-semibold text-neutral-500 uppercase tracking-wider">Description</th>
                <th className="px-6 py-3 text-xs font-semibold text-neutral-500 uppercase tracking-wider">Category</th>
                <th className="px-6 py-3 text-right text-xs font-semibold text-neutral-500 uppercase tracking-wider">Amount</th>
                <th className="px-6 py-3 text-right text-xs font-semibold text-neutral-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-200 bg-white">
              {dummyData.map((tx) => (
                <tr key={tx.id} className="hover:bg-neutral-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-neutral-900">{tx.date}</div>
                    <div className="text-xs text-neutral-500 mt-0.5">{tx.time}</div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className={`p-2 rounded-lg ${getIconStyles(tx.variant)}`}>
                        <tx.icon className="w-5 h-5" />
                      </div>
                      <div>
                        <div className="text-sm font-medium text-neutral-900">{tx.desc}</div>
                        <div className="text-xs text-neutral-500 mt-0.5">{tx.shortDesc}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2.5 py-1 text-xs font-medium rounded-full border ${getCategoryStyles(tx.variant)}`}>
                      {tx.category}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    <span className={`text-sm font-semibold font-mono ${tx.amount > 0 ? 'text-success-600' : 'text-error-600'}`}>
                      {tx.amount > 0 ? '+' : ''}{tx.amount.toFixed(2)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                    <button className="p-1 rounded text-neutral-400 hover:text-primary-600 hover:bg-primary-50 transition-colors">
                      <EllipsisVerticalIcon className="w-5 h-5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      
      <CreateTransactionModal isOpen={isModalOpen} onClose={() => setModalOpen(false)} />
    </div>
  );
}
