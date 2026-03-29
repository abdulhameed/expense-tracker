import React from 'react';
import { Button } from '../components/ui/Button';
import { 
  PlusIcon,
  ArrowTrendingUpIcon,
  ClockIcon,
  FunnelIcon,
  Squares2X2Icon,
  WrenchScrewdriverIcon,
  MegaphoneIcon,
  Cog6ToothIcon,
  GlobeAltIcon
} from '@heroicons/react/24/outline';

export default function Budgets() {
  const departments = [
    { name: 'Engineering', desc: 'Cloud & Infrastructure', used: 78, spent: 58500, limit: 75000, icon: WrenchScrewdriverIcon, color: 'primary' },
    { name: 'Marketing', desc: 'Paid Media & Social', used: 42, spent: 16800, limit: 40000, icon: MegaphoneIcon, color: 'success' },
    { name: 'Operations', desc: 'Real Estate & Supplies', used: 94, spent: 14100, limit: 15000, icon: Cog6ToothIcon, color: 'error' },
    { name: 'Travel', desc: 'Global Offsite', used: 20, spent: 3050, limit: 15000, icon: GlobeAltIcon, color: 'neutral' }
  ];

  const getColorClasses = (color) => {
    switch (color) {
      case 'primary': return { bg: 'bg-primary-50', text: 'text-primary-600', fill: 'bg-primary-600', ring: 'ring-primary-100' };
      case 'success': return { bg: 'bg-success-50', text: 'text-success-600', fill: 'bg-success-500', ring: 'ring-success-100' };
      case 'error': return { bg: 'bg-error-50', text: 'text-error-600', fill: 'bg-error-500', ring: 'ring-error-100' };
      default: return { bg: 'bg-neutral-100', text: 'text-neutral-600', fill: 'bg-neutral-500', ring: 'ring-neutral-200' };
    }
  };

  return (
    <div className="space-y-10">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-8">
        <div className="space-y-2">
          <span className="text-xs uppercase tracking-widest text-neutral-500 font-semibold">Financial Control</span>
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-neutral-900">Budget Management</h1>
        </div>
        <Button className="flex items-center justify-center gap-2 px-8 py-4 text-base shadow-lg shadow-primary-600/20">
          <PlusIcon className="w-5 h-5" />
          Add Budget
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-8 rounded-2xl border-l-4 border-primary-600 shadow-sm border-t border-r border-b border-neutral-200">
          <p className="text-neutral-500 text-sm font-medium mb-4">Total Monthly Budget</p>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold font-mono text-neutral-400">$</span>
            <span className="text-5xl font-extrabold tracking-tighter font-mono text-neutral-900">145,000</span>
          </div>
          <div className="mt-6 flex items-center gap-2 text-primary-600 font-medium text-sm">
            <ArrowTrendingUpIcon className="w-4 h-4" />
            <span>12% from last month</span>
          </div>
        </div>
        
        <div className="bg-white p-8 rounded-2xl shadow-sm border border-neutral-200">
          <p className="text-neutral-500 text-sm font-medium mb-4">Total Spent</p>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold font-mono text-neutral-400">$</span>
            <span className="text-5xl font-extrabold tracking-tighter font-mono text-neutral-900">92,450</span>
          </div>
          <div className="mt-6 flex items-center gap-2 text-neutral-500 font-medium text-sm">
            <ClockIcon className="w-4 h-4" />
            <span>Last updated 2h ago</span>
          </div>
        </div>
        
        <div className="bg-neutral-50 p-8 rounded-2xl shadow-sm border border-neutral-200">
          <p className="text-neutral-500 text-sm font-medium mb-4">Remaining Balance</p>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold font-mono text-success-600">$</span>
            <span className="text-5xl font-extrabold tracking-tighter font-mono text-success-600">52,550</span>
          </div>
          <div className="mt-6 h-2 w-full bg-neutral-200 rounded-full overflow-hidden">
            <div className="h-full bg-success-500 rounded-full" style={{ width: '64%' }}></div>
          </div>
          <p className="mt-2 text-xs text-neutral-500 text-right">64% of budget utilized</p>
        </div>
      </div>

      <div>
        <div className="mb-6 flex items-center justify-between">
          <h2 className="text-2xl font-bold tracking-tight text-neutral-900">Departmental Categories</h2>
          <div className="flex gap-2">
            <button className="p-2 bg-white border border-neutral-200 text-neutral-500 rounded-lg hover:bg-neutral-50 transition-colors">
              <FunnelIcon className="w-5 h-5" />
            </button>
            <button className="p-2 bg-white border border-neutral-200 text-neutral-500 rounded-lg hover:bg-neutral-50 transition-colors">
              <Squares2X2Icon className="w-5 h-5" />
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {departments.map((dept, idx) => {
            const colors = getColorClasses(dept.color);
            return (
              <div key={idx} className="bg-white border border-neutral-200 p-6 rounded-2xl hover:border-neutral-300 transition-colors shadow-sm group">
                <div className="flex justify-between items-start mb-8">
                  <div className={`p-3 rounded-xl ${colors.bg} ${colors.text}`}>
                    <dept.icon className="w-6 h-6" />
                  </div>
                  <span className={`text-xs font-mono font-medium px-2 py-1 rounded-md ${colors.bg} ${colors.text} ring-1 inset-0 ${colors.ring}`}>
                    {dept.used}%
                  </span>
                </div>
                <h3 className="text-lg font-bold mb-1 text-neutral-900">{dept.name}</h3>
                <p className="text-sm text-neutral-500 mb-6">{dept.desc}</p>
                <div className="space-y-4">
                  <div className="h-1.5 w-full bg-neutral-100 rounded-full">
                    <div className={`h-full rounded-full transition-all duration-1000 ${colors.fill}`} style={{ width: `${dept.used}%` }}></div>
                  </div>
                  <div className="flex justify-between items-baseline">
                    <span className="font-mono font-bold text-lg text-neutral-900">${dept.spent.toLocaleString()}</span>
                    <span className="text-xs text-neutral-500">/ ${(dept.limit / 1000)}k</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="bg-white p-8 rounded-3xl border border-neutral-200 shadow-sm overflow-hidden relative">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8 relative z-10">
          <div>
            <h2 className="text-2xl font-bold tracking-tight mb-2 text-neutral-900">Spending Horizon</h2>
            <p className="text-neutral-500 text-sm">Projected budget depletion vs. actual spend across Q3.</p>
          </div>
          <div className="flex bg-neutral-100 rounded-lg p-1 border border-neutral-200">
            <button className="px-4 py-2 text-xs font-bold uppercase tracking-widest bg-white text-neutral-900 rounded-md shadow-sm">Monthly</button>
            <button className="px-4 py-2 text-xs font-bold uppercase tracking-widest text-neutral-500 hover:text-neutral-900">Quarterly</button>
          </div>
        </div>
        
        <div className="h-64 w-full relative">
          <div className="absolute inset-0 flex items-end gap-1 md:gap-4 h-full">
            <div className="flex-1 bg-primary-100 rounded-t-lg h-[40%] transition-all duration-700"></div>
            <div className="flex-1 bg-primary-200 rounded-t-lg h-[55%] transition-all duration-700"></div>
            <div className="flex-1 bg-primary-300 rounded-t-lg h-[45%] transition-all duration-700"></div>
            <div className="flex-1 bg-primary-400 rounded-t-lg h-[70%] transition-all duration-700"></div>
            <div className="flex-1 bg-primary-500 rounded-t-lg h-[60%] transition-all duration-700"></div>
            <div className="flex-1 bg-primary-600 rounded-t-lg h-[85%] relative transition-all duration-700">
              <div className="absolute -top-10 left-1/2 -translate-x-1/2 bg-neutral-900 text-white px-3 py-1 rounded text-[10px] font-mono whitespace-nowrap hidden md:block">
                Current Week
              </div>
            </div>
            <div className="flex-1 bg-neutral-100 rounded-t-lg h-[50%] border-t-2 border-dashed border-primary-300"></div>
            <div className="flex-1 bg-neutral-100 rounded-t-lg h-[40%] border-t-2 border-dashed border-primary-300"></div>
          </div>
          
          <div className="absolute inset-0 flex flex-col justify-between pointer-events-none opacity-10">
            {[1, 2, 3, 4].map(i => <div key={i} className="border-b border-neutral-900 w-full"></div>)}
          </div>
        </div>
        
        <div className="flex justify-between mt-4 text-[10px] uppercase font-bold tracking-widest text-neutral-400 px-2 lg:px-6">
          <span>Jul</span><span>Aug</span><span>Sep</span><span>Oct</span><span>Nov</span><span>Dec</span><span>Jan</span><span>Feb</span>
        </div>
      </div>
    </div>
  );
}
